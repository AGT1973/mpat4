# MPAT4_DEST
# destino: core
# nombre: devops_orchestrator.py
# alumno: Claude Sonnet 4.6

# devops_orchestrator.py
## Autor: Claude Sonnet 4.6 · 2026-05-28
## Módulo: core/devops/ · Lenguaje: Python · Versión: V4_14
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

"""
DevOpsOrchestrator — RES.177 AI Native DevOps
Coordina el pipeline completo. Detecta y adapta ante patrones recurrentes.
INV-DEV.9: pipeline secuencial MONITOR → TEST → DEPLOY → ALERT.
INV-DEV.10: N >= RECURRENCE_THRESHOLD fallos → activar adaptive_mode.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable, Awaitable

from schema_res177 import (
    AdaptationTrigger,
    AnomalyEvent,
    AnomalySeverity,
    DeployRequest,
    DeploymentRecord,
    DeployStatus,
    DeployStrategy,
    DevOpsEvent,
    FailurePattern,
    PipelineAdaptation,
    PipelineEventType,
    PipelineState,
    RECURRENCE_THRESHOLD,
    RuntimeMetrics,
    TestResult,
)
from monitoring_agent import MonitoringAgent
from testing_agent import TestingAgent
from deployment_agent import DeploymentAgent
from alert_agent import AlertAgent, AlertChannel

logger = logging.getLogger(__name__)


class DevOpsOrchestrator:
    """
    Orquestador del pipeline AI Native DevOps — RES.177.

    Diferenciador clave: el pipeline no solo ejecuta —
    MODIFICA su comportamiento cuando detecta patrones de fallo recurrentes.

    INV-DEV.9: MONITOR → TEST → DEPLOY → ALERT (secuencial, no saltear pasos).
    INV-DEV.10: N >= RECURRENCE_THRESHOLD fallos del mismo tipo → adaptive_mode.
    """

    def __init__(
        self,
        tenant_id: str = "default",
        channels: list[AlertChannel] | None = None,
    ) -> None:
        self._tenant_id = tenant_id
        self._state = PipelineState(tenant_id=tenant_id)
        self._event_log: list[DevOpsEvent] = []

        # Bus interno: collect all events emitted by sub-agents
        async def _bus_emit(event: DevOpsEvent) -> None:
            self._event_log.append(event)
            logger.debug("EVENT | type=%s sha256=%s", event.event_type.value, event.event_sha256)

        # Sub-agentes con bus inyectado (INV-DEV.1: MonitoringAgent asíncrono)
        self.monitoring = MonitoringAgent(emit=_bus_emit, tenant_id=tenant_id)
        self.testing = TestingAgent(emit=_bus_emit, tenant_id=tenant_id)
        self.deployment = DeploymentAgent(emit=_bus_emit, tenant_id=tenant_id)
        self.alerting = AlertAgent(
            emit=_bus_emit,
            channels=channels or [AlertChannel.EVENT_BUS],
            tenant_id=tenant_id,
        )

    # -----------------------------------------------------------------------
    # PASO PRINCIPAL: ejecutar pipeline completo
    # -----------------------------------------------------------------------

    async def run_pipeline(
        self,
        artifact_path: str,
        version: str,
        strategy: DeployStrategy = DeployStrategy.ROLLING,
    ) -> dict:
        """
        INV-DEV.9: pipeline MONITOR → TEST → DEPLOY → ALERT.
        Retorna un resumen del resultado del pipeline completo.
        """
        logger.info(
            "PIPELINE start | version=%s artifact=%s strategy=%s",
            version, artifact_path, strategy.value,
        )
        summary = {
            "version": version,
            "artifact_path": artifact_path,
            "strategy": strategy.value,
            "tenant_id": self._tenant_id,
            "started_at": datetime.utcnow().isoformat(),
        }

        # ── PASO 1: TEST (INV-DEV.9: siempre antes de deploy) ──────────────
        test_result: TestResult = await self.testing.run(artifact_path)
        summary["test_status"] = test_result.status.value
        summary["test_coverage"] = test_result.coverage
        summary["test_sha256"] = test_result.result_sha256

        if test_result.status.value != "approved":
            # Testing falló — registrar patrón y alertar
            await self._record_failure("testing_rejected", artifact_path)
            await self.alerting.send(
                severity=AnomalySeverity.HIGH,
                message=f"Testing REJECTED for version {version}: coverage={test_result.coverage:.0%}, "
                        f"failures={len(test_result.failures)}",
                source_event_id=test_result.result_sha256,
                component="testing_agent",
            )
            summary["pipeline_status"] = "aborted_testing_failed"
            summary["completed_at"] = datetime.utcnow().isoformat()
            logger.warning("PIPELINE aborted: testing failed | version=%s", version)
            return summary

        # ── PASO 2: DEPLOY (INV-DEV.9: solo si test pasó) ──────────────────
        deploy_request = DeployRequest(
            version=version,
            artifact_path=artifact_path,
            strategy=strategy,
            test_result=test_result,
            tenant_id=self._tenant_id,
        )
        deploy_record: DeploymentRecord = await self.deployment.deploy(deploy_request)
        summary["deploy_status"] = deploy_record.status.value
        summary["deploy_sha256"] = deploy_record.record_sha256
        self._update_state(deploy_record)

        # ── PASO 3: ALERT si deploy falló / rollback (INV-DEV.9) ───────────
        if deploy_record.status in (DeployStatus.ROLLED_BACK, DeployStatus.FAILED):
            await self._record_failure("deploy_failed", version)
            severity = (
                AnomalySeverity.CRITICAL
                if deploy_record.status == DeployStatus.FAILED
                else AnomalySeverity.HIGH
            )
            await self.alerting.send(
                severity=severity,
                message=f"Deploy {deploy_record.status.value.upper()} for version {version}. "
                        f"Health check: {deploy_record.health_check_passed}",
                source_event_id=deploy_record.record_sha256,
                component="deployment_agent",
            )
            summary["pipeline_status"] = f"deploy_{deploy_record.status.value}"
        else:
            summary["pipeline_status"] = "success"
            logger.info("PIPELINE success | version=%s", version)

        # ── PASO 4: detectar adaptaciones necesarias (INV-DEV.10) ──────────
        adaptation = self._check_adaptive_mode()
        if adaptation:
            summary["adaptation_applied"] = adaptation.adaptation_applied
            self._emit_adaptation_event(adaptation)

        summary["completed_at"] = datetime.utcnow().isoformat()
        summary["adaptive_mode"] = self._state.adaptive_mode
        return summary

    # -----------------------------------------------------------------------
    # OBSERVACIÓN — integra MonitoringAgent en el pipeline
    # -----------------------------------------------------------------------

    async def observe_metrics(self, metrics: RuntimeMetrics) -> AnomalyEvent | None:
        """
        Punto de entrada para métricas OTel externas.
        INV-DEV.1: MonitoringAgent es asíncrono — no bloquea.
        """
        anomaly = await self.monitoring.observe(metrics)
        if anomaly and anomaly.severity in (
            AnomalySeverity.HIGH, AnomalySeverity.CRITICAL
        ):
            await self.alerting.send(
                severity=anomaly.severity,
                message=(
                    f"Anomaly in {anomaly.component}: {anomaly.threshold_violated}. "
                    f"P99={anomaly.metrics_snapshot.latency_p99_ms:.0f}ms "
                    f"error_rate={anomaly.metrics_snapshot.error_rate:.1%}"
                ),
                source_event_id=anomaly.event_id,
                component=anomaly.component,
            )
        return anomaly

    # -----------------------------------------------------------------------
    # ADAPTIVE PIPELINE — INV-DEV.10
    # -----------------------------------------------------------------------

    def _record_failure(self, failure_type: str, component: str) -> None:
        """Registra un fallo en el estado para detección de patrones."""
        now = datetime.utcnow()
        existing = next(
            (p for p in self._state.failure_patterns
             if p.failure_type == failure_type and p.component == component),
            None,
        )
        if existing:
            object.__setattr__(existing, "occurrences", existing.occurrences + 1)
            object.__setattr__(existing, "last_seen", now)
        else:
            self._state.failure_patterns.append(
                FailurePattern(
                    component=component,
                    failure_type=failure_type,
                    occurrences=1,
                    first_seen=now,
                    last_seen=now,
                )
            )

    def _check_adaptive_mode(self) -> PipelineAdaptation | None:
        """
        INV-DEV.10: si algún patrón es recurrente → activar adaptive_mode
        y retornar la adaptación aplicada.
        """
        for pattern in self._state.failure_patterns:
            if pattern.is_recurrent and not self._state.adaptive_mode:
                # Activar adaptive mode
                object.__setattr__(self._state, "adaptive_mode", True)
                adaptation_desc = self._determine_adaptation(pattern)
                adaptation = PipelineAdaptation(
                    trigger=AdaptationTrigger.RECURRENT_FAILURE,
                    trigger_pattern=pattern,
                    adaptation_applied=adaptation_desc,
                )
                self._state.adaptations_applied.append(adaptation)
                logger.warning(
                    "ADAPTIVE MODE activated | pattern=%s occurrences=%d adaptation=%s",
                    pattern.failure_type,
                    pattern.occurrences,
                    adaptation_desc,
                )
                return adaptation
        return None

    def _determine_adaptation(self, pattern: FailurePattern) -> str:
        """
        Determina qué adaptación aplicar según el patrón de fallo.
        DT-RES177-04: V1 usa reglas simples — V2 usará ML real.
        """
        if pattern.failure_type == "testing_rejected":
            return (
                f"Incrementar MIN_COVERAGE threshold logging ante {pattern.occurrences} "
                f"rechazos en '{pattern.component}'. Revisar test suite."
            )
        elif pattern.failure_type == "deploy_failed":
            return (
                f"Activar estrategia CANARY en próximos deploys de '{pattern.component}' "
                f"tras {pattern.occurrences} fallos consecutivos."
            )
        else:
            return (
                f"Patrón '{pattern.failure_type}' en '{pattern.component}' "
                f"recurrente ({pattern.occurrences}x). Revisión manual recomendada."
            )

    def _emit_adaptation_event(self, adaptation: PipelineAdaptation) -> None:
        """Registra el evento de adaptación en el log interno."""
        event = DevOpsEvent(
            event_type=PipelineEventType.PIPELINE_ADAPTED,
            tenant_id=self._tenant_id,
            payload={
                "trigger": adaptation.trigger.value,
                "component": adaptation.trigger_pattern.component,
                "occurrences": adaptation.trigger_pattern.occurrences,
                "adaptation": adaptation.adaptation_applied,
            },
        )
        self._event_log.append(event)

    def _update_state(self, record: DeploymentRecord) -> None:
        """Actualiza el estado del pipeline con el resultado del deploy."""
        if record.status == DeployStatus.COMPLETED:
            object.__setattr__(self._state, "current_version", record.version)
        object.__setattr__(self._state, "last_deploy", record)
        self._state.version_history.append(record)
        if len(self._state.version_history) > 5:
            object.__setattr__(
                self._state, "version_history",
                self._state.version_history[-5:]
            )
        object.__setattr__(self._state, "last_updated", datetime.utcnow())

    # -----------------------------------------------------------------------
    # ACCESORES
    # -----------------------------------------------------------------------

    @property
    def state(self) -> PipelineState:
        return self._state

    @property
    def event_log(self) -> list[DevOpsEvent]:
        return list(self._event_log)
