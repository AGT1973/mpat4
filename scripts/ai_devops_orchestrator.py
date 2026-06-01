# ai_devops_orchestrator.py
## Autor: ai.mpat.info@gmail.com · 2026-05-28
## Modulo: core/devops/ · Version: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## RES: RES.177 — AI Native DevOps
## Schema: schemas/schema_res177.py
*que has usado el formato de razonamiento adaptado por AGT*

# ===========================================================================
# POR QUE EXISTE ESTE MODULO
# ===========================================================================
# Un pipeline convencional (GitHub Actions) sigue el mismo grafo de pasos
# sin importar el historial de fallos. AIDevOpsOrchestrator detecta patrones
# de fallo recurrentes y modifica el pipeline:
# - P99 > umbral -> activa routing a SLM local
# - deployment falla -> rollback automatico + alerta + HITL si CRITICAL
# - pool miss alto -> señal para aumentar pool (RuntimeOptimizer)
#
# INV-DEVOPS-001: metricas tienen timestamp UTC.
# INV-DEVOPS-002: latencias en milisegundos.
# INV-DEVOPS-003: version_id inmutable.
# INV-DEVOPS-004: rollback_version_id apunta a version estable.
# INV-DEVOPS-005: NUNCA ejecutar codigo no verificado fuera de sandbox.
# INV-DEVOPS-006: alertas CRITICAL requieren confirmacion HITL.
# INV-DEVOPS-007: latency_threshold_ms activa routing a SLM.
# INV-DEVOPS-008: max_rollback_attempts limite antes de escalar a HITL.
# INV-COG-007: NUNCA Docker.
# ===========================================================================

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

from schema_res177 import (
    AlertNotification,
    AlertSeverity,
    AnomalyDetection,
    DeploymentResult,
    DeploymentSpec,
    DeploymentStatus,
    DevOpsConfig,
    PipelineEvent,
    PipelinePhase,
    RuntimeMetrics,
    SandboxTestRequest,
    SandboxTestResult,
    TestOutcome,
)

logger = logging.getLogger(__name__)


class AIDevOpsOrchestrator:
    """
    Orquestador de CI/CD gestionado por agentes IA para MPAT4. Version V4_01.

    Coordina cuatro agentes especializados:
      1. Agente de monitoreo: observa RuntimeMetrics via OTel (P69)
      2. Agente de testing: ejecuta tests en sandbox Firecracker (INV-DEVOPS-005)
      3. Agente de deployment: gestiona versiones con rollback automatico
      4. Agente de alertas: notifica via WhatsApp/Telegram (items 07/08)

    INV-COG-002: toda comunicacion externa via emit inyectado.
    INV-COG-006: stateless entre llamadas.
    INV-COG-007: NUNCA Docker.

    Postcondicion run_pipeline():
      - Retorna DeploymentResult siempre (nunca lanza hacia arriba).
      - Si deployment falla: rollback automatico.
      - Si rollback falla o severity=CRITICAL: emite evento HITL.
    """

    def __init__(
        self,
        config: DevOpsConfig | None = None,
        emit: Callable[[str, dict], Awaitable[None]] | None = None,
    ) -> None:
        self._config = config or DevOpsConfig()
        self._emit = emit
        self._rollback_attempts: dict[str, int] = {}

    async def run_pipeline(
        self,
        spec: DeploymentSpec,
        metrics: RuntimeMetrics | None = None,
    ) -> DeploymentResult:
        """
        Ejecuta el pipeline CI/CD completo para un deployment.

        Fases: MONITOR -> TEST (sandbox) -> DEPLOY -> VERIFY -> ROLLBACK? -> ALERT
        Retorna DeploymentResult siempre. Nunca lanza excepcion hacia arriba.
        """
        started_at = datetime.now(timezone.utc)
        logger.info(
            "[DevOps] iniciando pipeline: deployment=%s component=%s version=%s",
            spec.deployment_id, spec.component_id, spec.version_id,
        )

        try:
            # FASE 1: MONITOR
            if metrics is not None:
                anomalies = self._detect_anomalies(metrics)
                await self._emit_phase(spec, PipelinePhase.MONITOR, DeploymentStatus.RUNNING, {
                    "anomalies_detected": len(anomalies),
                    "anomalies": [a.anomaly_type for a in anomalies],
                })
                critical = [a for a in anomalies if a.severity == AlertSeverity.CRITICAL]
                if critical:
                    logger.warning("[DevOps] anomalias criticas pre-deploy: %s",
                                   [a.anomaly_type for a in critical])
                    await self._send_alert(spec, critical[0], pre_deploy=True)

            # FASE 2: TEST en sandbox
            if spec.requires_sandbox or self._config.sandbox_required_by_default:
                test_result = await self._run_sandbox_tests(spec)
                await self._emit_phase(spec, PipelinePhase.TEST,
                    DeploymentStatus.RUNNING if test_result.outcome == TestOutcome.PASSED
                    else DeploymentStatus.FAILED,
                    {"test_outcome": test_result.outcome.value,
                     "tests_passed": test_result.tests_passed,
                     "tests_failed": test_result.tests_failed},
                )
                if test_result.outcome != TestOutcome.PASSED:
                    return await self._abort_with_result(
                        spec, started_at,
                        f"Tests fallidos en sandbox: {test_result.tests_failed} failed",
                        DeploymentStatus.FAILED,
                    )

            # FASE 3: DEPLOY
            deploy_ok = await self._execute_deployment(spec)
            await self._emit_phase(spec, PipelinePhase.DEPLOY,
                DeploymentStatus.RUNNING if deploy_ok else DeploymentStatus.FAILED,
                {"deploy_success": deploy_ok},
            )
            if not deploy_ok:
                return await self._handle_deployment_failure(spec, started_at)

            # FASE 4: VERIFY
            verify_ok = await self._verify_deployment(spec)
            await self._emit_phase(spec, PipelinePhase.VERIFY,
                DeploymentStatus.SUCCESS if verify_ok else DeploymentStatus.FAILED,
                {"verify_success": verify_ok},
            )
            if not verify_ok:
                return await self._handle_deployment_failure(spec, started_at)

            # SUCCESS
            duration = (datetime.now(timezone.utc) - started_at).total_seconds()
            result = DeploymentResult(
                deployment_id=spec.deployment_id,
                status=DeploymentStatus.SUCCESS,
                version_deployed=spec.version_id,
                rollback_used=False,
                duration_seconds=duration,
            )
            await self._emit_phase(spec, PipelinePhase.ALERT, DeploymentStatus.SUCCESS, {
                "message": f"Deployment exitoso: {spec.version_id}",
            })
            logger.info("[DevOps] deployment exitoso: %s version=%s duration=%.1fs",
                        spec.deployment_id, spec.version_id, duration)
            return result

        except Exception as exc:
            logger.error("[DevOps] excepcion no esperada en pipeline: %s", exc)
            duration = (datetime.now(timezone.utc) - started_at).total_seconds()
            return DeploymentResult(
                deployment_id=spec.deployment_id,
                status=DeploymentStatus.FAILED,
                version_deployed=spec.version_id,
                rollback_used=False,
                duration_seconds=duration,
                error_message=f"Excepcion no esperada: {exc}",
            )

    # ---------------------------------------------------------------------------
    # AGENTE DE MONITOREO
    # ---------------------------------------------------------------------------

    def _detect_anomalies(self, metrics: RuntimeMetrics) -> list[AnomalyDetection]:
        """
        Analiza RuntimeMetrics y retorna lista de anomalias detectadas.
        INV-DEVOPS-007: latency_p99_ms > latency_threshold_ms activa routing a SLM.
        """
        anomalies: list[AnomalyDetection] = []
        rule_checks = [
            ("latencia_p99_alta",
             metrics.latency_p99_ms,
             self._config.latency_threshold_ms,
             AlertSeverity.CRITICAL,
             "Activar routing a SLM local para reducir latencia"),
            ("latencia_p50_alta",
             metrics.latency_p50_ms,
             self._config.latency_threshold_ms * 0.5,
             AlertSeverity.WARNING,
             "Monitorear — latencia P50 elevada"),
            ("pool_miss_alto",
             metrics.pool_miss_rate,
             self._config.pool_miss_threshold_pct,
             AlertSeverity.WARNING,
             "Aumentar warm pool size en RuntimeOptimizer"),
            ("error_rate_alto",
             metrics.error_rate_pct,
             5.0,
             AlertSeverity.CRITICAL,
             "Investigar causa de errores — posible rollback requerido"),
        ]
        for anomaly_type, value, threshold, severity, recommendation in rule_checks:
            if value > threshold:
                anomalies.append(AnomalyDetection(
                    component_id=metrics.component_id,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    metric_name=anomaly_type,
                    metric_value=value,
                    threshold=threshold,
                    recommendation=recommendation,
                ))
        return anomalies

    async def observe_metrics(self, metrics: RuntimeMetrics) -> list[AnomalyDetection]:
        """API publica para monitoreo periodico."""
        anomalies = self._detect_anomalies(metrics)
        if anomalies:
            await self._emit_event("devops.anomaly_detected", {
                "component_id": metrics.component_id,
                "anomaly_count": len(anomalies),
                "anomalies": [{"type": a.anomaly_type, "severity": a.severity.value,
                               "recommendation": a.recommendation} for a in anomalies],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        return anomalies

    # ---------------------------------------------------------------------------
    # AGENTE DE TESTING EN SANDBOX
    # ---------------------------------------------------------------------------

    async def _run_sandbox_tests(self, spec: DeploymentSpec) -> SandboxTestResult:
        """
        Ejecuta tests en sandbox Firecracker.
        INV-DEVOPS-005: NUNCA ejecutar codigo no verificado fuera de sandbox.
        STUB: integracion real con cognitive_sandboxing (VOL1 item 15) pendiente.
        """
        test_id = f"test-{uuid.uuid4().hex[:8]}"
        logger.info("[DevOps] ejecutando tests en sandbox: test_id=%s artifact=%s",
                    test_id, spec.artifact_path)
        # STUB — DT-DEVOPS-001
        return SandboxTestResult(
            test_id=test_id,
            deployment_id=spec.deployment_id,
            outcome=TestOutcome.PASSED,
            tests_passed=42,
            tests_failed=0,
            coverage_pct=87.3,
            duration_seconds=23.4,
            output_summary="[STUB] todos los tests pasaron en sandbox Firecracker",
        )

    # ---------------------------------------------------------------------------
    # AGENTE DE DEPLOYMENT
    # ---------------------------------------------------------------------------

    async def _execute_deployment(self, spec: DeploymentSpec) -> bool:
        """
        Ejecuta el deployment del artefacto.
        STUB — DT-DEVOPS-002: integracion NanoVM/Unikraft/Firecracker pendiente.
        INV-COG-007: NUNCA Docker.
        """
        logger.info("[DevOps] ejecutando deployment: component=%s version=%s",
                    spec.component_id, spec.version_id)
        return True  # STUB

    async def _verify_deployment(self, spec: DeploymentSpec) -> bool:
        """Verifica health post-deployment. STUB."""
        return True

    async def _execute_rollback(self, spec: DeploymentSpec) -> bool:
        """
        Ejecuta rollback a spec.rollback_version_id.
        INV-DEVOPS-004: rollback_version_id apunta a version estable.
        INV-DEVOPS-008: si supera max_rollback_attempts, escalar a HITL.
        """
        attempts = self._rollback_attempts.get(spec.deployment_id, 0) + 1
        self._rollback_attempts[spec.deployment_id] = attempts
        if attempts > self._config.max_rollback_attempts:
            logger.error("[DevOps] max rollback attempts superado (%d/%d): escalar a HITL",
                         attempts, self._config.max_rollback_attempts)
            await self._emit_event("devops.hitl_required", {
                "deployment_id": spec.deployment_id,
                "component_id": spec.component_id,
                "reason": "max_rollback_attempts_exceeded",
                "rollback_version": spec.rollback_version_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return False
        logger.info("[DevOps] rollback: %s -> %s (intento %d/%d)",
                    spec.version_id, spec.rollback_version_id,
                    attempts, self._config.max_rollback_attempts)
        return True  # STUB

    # ---------------------------------------------------------------------------
    # AGENTE DE ALERTAS
    # ---------------------------------------------------------------------------

    async def _send_alert(
        self,
        spec: DeploymentSpec,
        anomaly: AnomalyDetection,
        pre_deploy: bool = False,
    ) -> None:
        """
        Envia alerta via WhatsApp/Telegram.
        INV-DEVOPS-006: alertas CRITICAL requieren confirmacion HITL.
        """
        requires_hitl = (
            anomaly.severity == AlertSeverity.CRITICAL
            and self._config.hitl_required_for_critical
        )
        prefix = "[PRE-DEPLOY] " if pre_deploy else "[POST-DEPLOY] "
        notification = AlertNotification(
            alert_id=f"alert-{uuid.uuid4().hex[:8]}",
            severity=anomaly.severity,
            component_id=spec.component_id,
            message=(
                f"{prefix}{anomaly.anomaly_type} "
                f"(valor={anomaly.metric_value:.2f}, umbral={anomaly.threshold:.2f}). "
                f"{anomaly.recommendation}"
            ),
            requires_hitl=requires_hitl,
            channel=self._config.alert_channel,
            tenant_id=spec.tenant_id,
        )
        await self._emit_event("devops.alert_sent", {
            "alert_id": notification.alert_id,
            "severity": notification.severity.value,
            "channel": notification.channel,
            "requires_hitl": notification.requires_hitl,
            "message": notification.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # ---------------------------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------------------------

    async def _handle_deployment_failure(
        self, spec: DeploymentSpec, started_at: datetime
    ) -> DeploymentResult:
        rollback_ok = await self._execute_rollback(spec)
        await self._emit_phase(spec, PipelinePhase.ROLLBACK,
            DeploymentStatus.ROLLED_BACK if rollback_ok else DeploymentStatus.FAILED,
            {"rollback_success": rollback_ok, "rollback_to": spec.rollback_version_id},
        )
        duration = (datetime.now(timezone.utc) - started_at).total_seconds()
        return DeploymentResult(
            deployment_id=spec.deployment_id,
            status=DeploymentStatus.ROLLED_BACK if rollback_ok else DeploymentStatus.FAILED,
            version_deployed=spec.rollback_version_id if rollback_ok else spec.version_id,
            rollback_used=True,
            duration_seconds=duration,
            error_message=(
                f"Deployment fallido. Rollback a {spec.rollback_version_id} exitoso."
                if rollback_ok
                else "Deployment fallido. Rollback fallido — requiere intervencion manual."
            ),
        )

    async def _abort_with_result(
        self, spec: DeploymentSpec, started_at: datetime,
        error_message: str, status: DeploymentStatus,
    ) -> DeploymentResult:
        duration = (datetime.now(timezone.utc) - started_at).total_seconds()
        logger.error("[DevOps] pipeline abortado: %s reason=%s",
                     spec.deployment_id, error_message)
        return DeploymentResult(
            deployment_id=spec.deployment_id,
            status=status,
            version_deployed=spec.version_id,
            rollback_used=False,
            duration_seconds=duration,
            error_message=error_message,
        )

    async def _emit_phase(
        self, spec: DeploymentSpec, phase: PipelinePhase,
        status: DeploymentStatus, payload: dict,
    ) -> None:
        event = PipelineEvent(
            event_id=f"pipe-{uuid.uuid4().hex[:8]}",
            deployment_id=spec.deployment_id,
            phase=phase,
            status=status,
            payload=payload,
            agent_id="ai_devops_orchestrator",
        )
        await self._emit_event("devops.pipeline_phase", {
            "event_id": event.event_id,
            "deployment_id": event.deployment_id,
            "phase": event.phase.value,
            "status": event.status.value,
            "payload": event.payload,
            "agent_id": event.agent_id,
            "emitted_at": event.emitted_at.isoformat(),
        })

    async def _emit_event(self, event_name: str, payload: dict) -> None:
        """INV-COG-002: toda comunicacion externa via emit inyectado."""
        if self._emit is not None:
            try:
                await self._emit(event_name, payload)
            except Exception as exc:
                logger.warning("[DevOps] error al emitir %s: %s", event_name, exc)
        else:
            logger.debug("[DevOps] evento (sin bus): %s", event_name)


# ---------------------------------------------------------------------------
# DEUDA TECNICA
# ---------------------------------------------------------------------------
# DT-DEVOPS-001: _run_sandbox_tests es stub — integracion con cognitive_sandboxing (VOL1 item 15)
# DT-DEVOPS-002: _execute_deployment es stub — integracion NanoVM/Unikraft/Firecracker
# DT-DEVOPS-003: Temporal.io para workflows larga duracion (VOL2 item 57)
# DT-DEVOPS-004: integracion WhatsApp/Telegram real (RES.170/RES.171)
# DT-DEVOPS-005: pattern learning de fallos recurrentes — RuntimeOptimizer (RES.168)
# ---------------------------------------------------------------------------

*ai_devops_orchestrator.py V4_01 · RES.177 · ai.mpat.info@gmail.com · 2026-05-28*
*que has usado el formato de razonamiento adaptado por AGT*
