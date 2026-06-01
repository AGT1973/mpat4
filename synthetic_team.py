# synthetic_team.py
# RES.176 -- SyntheticTeam -- Orquestador principal
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# Contrato: CONTRACT_RES176_v1.md (ID: 1vMvJE3JJIygByoICpWrqso86duqY_01DFziWrTO-L9c)
# que has usado el formato de razonamiento adaptado por AGT
#
# INVARIANTES:
#   INV-TEAM.1: workflow siempre secuencial, nunca salta fases
#   INV-TEAM.2: cada fase DEBE producir TeamArtifact no vacio
#   INV-TEAM.3: QA SIEMPRE antes de DOCS
#   INV-TEAM.4: DEV reintenta max 3 veces si QA rechaza
#   INV-TEAM.5: PM evalua el resultado final (Self-Rewarding)
#   INV-TEAM.6: solo emit inyectado
#   INV-TEAM.7: todos los artefactos tienen SHA-256


from __future__ import annotations


import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any


from schema_res176 import (
    CodeArtifact,
    PhaseRecord,
    PhaseStatus,
    ProjectBrief,
    ProjectResult,
    ProjectStatus,
    QAVerdict,
    TeamArtifact,
    TeamContext,
    TeamPhase,
    TeamRole,
)
from team_roles import (
    ARCHAgent,
    DEVAgent,
    DOCSAgent,
    PMAgent,
    QAAgent,
    RoleAgent,
    create_team,
)


logger = logging.getLogger("mpat4.synthetic_teams")


EmitFn = Callable[[str, dict[str, Any]], None]
LLMFn  = Callable[[str], "Awaitable[str]"]


MAX_DEV_RETRIES = 3   # INV-TEAM.4


# Eventos (INV-TEAM.6)
_EVT_STARTED          = "team.project_started"
_EVT_PHASE_COMPLETE   = "team.phase_complete"
_EVT_QA_REJECTED      = "team.qa_rejected"
_EVT_REVISION_NEEDED  = "team.revision_requested"
_EVT_PROJECT_COMPLETE = "team.project_complete"
_EVT_AUDIT            = "team.audit"




class SyntheticTeam:
    """
    Equipo sintetico de agentes especializados para desarrollo de software.


    Workflow (INV-TEAM.1 -- siempre secuencial):
      PRD -> Architecture -> Implementation -> Testing/QA -> Documentation


    INV-TEAM.3: QA siempre antes de DOCS.
    INV-TEAM.4: DEV reintenta max 3 veces ante rechazo de QA.
    INV-TEAM.5: PM evalua el output final via Self-Rewarding.
    INV-TEAM.6: solo emit inyectado.
    INV-TEAM.7: SHA-256 en todo TeamArtifact (garantizado por schema).
    """


    def __init__(
        self,
        agent_id:  str,
        tenant_id: str,
        llm_fn:    LLMFn,
        emit:      EmitFn,
        role_fns:  dict[str, LLMFn] | None = None,
    ) -> None:
        self._agent_id  = agent_id
        self._tenant_id = tenant_id
        self._emit      = emit
        self._agents    = create_team(llm_fn, role_fns)


    # -----------------------------------------------------------------------
    # execute_project -- punto de entrada principal
    # -----------------------------------------------------------------------


    async def execute_project(self, brief: ProjectBrief) -> ProjectResult:
        """
        Ejecuta el workflow completo.
        INV-TEAM.1: secuencial, sin saltarse fases.
        """
        project_id = str(uuid.uuid4())
        t0         = time.monotonic()
        phases:    list[PhaseRecord] = []
        artifacts: list[TeamArtifact] = []


        context = TeamContext(project_id=project_id, brief=brief)


        self._emit(_EVT_STARTED, {
            "project_id": project_id,
            "agent_id":   self._agent_id,
            "tenant_id":  self._tenant_id,
            "title":      brief.title,
        })


        try:
            # --- FASE 1: PM -> PRD ---
            record, prd = await self._run_phase(
                TeamPhase.PRD, TeamRole.PM, context, artifacts
            )
            phases.append(record)
            if record.status == PhaseStatus.FAILED:
                return self._fail(project_id, brief.brief_id, phases, artifacts, t0, "PRD fallido")
            context.prd = prd
            context.current_phase = TeamPhase.ARCHITECTURE


            # --- FASE 2: ARCH -> Architecture ---
            record, arch = await self._run_phase(
                TeamPhase.ARCHITECTURE, TeamRole.ARCH, context, artifacts
            )
            phases.append(record)
            if record.status == PhaseStatus.FAILED:
                return self._fail(project_id, brief.brief_id, phases, artifacts, t0, "Architecture fallido")
            context.architecture = arch
            context.current_phase = TeamPhase.IMPLEMENTATION


            # --- FASE 3: DEV -> Code (con reintentos QA -- INV-TEAM.4) ---
            dev_success = False
            for dev_attempt in range(1, MAX_DEV_RETRIES + 1):
                context.dev_attempts = dev_attempt


                code_record, code = await self._run_phase(
                    TeamPhase.IMPLEMENTATION, TeamRole.DEV, context, artifacts
                )
                phases.append(code_record)
                if code_record.status == PhaseStatus.FAILED:
                    break
                context.code_artifacts.append(code)


                # --- FASE 4: QA -> Review (INV-TEAM.3) ---
                qa_record, test_artifact = await self._run_phase(
                    TeamPhase.TESTING, TeamRole.QA, context, artifacts
                )
                phases.append(qa_record)
                context.test_artifact = test_artifact


                # Review del codigo por QA
                qa_agent = self._agents[TeamRole.QA]
                review   = await qa_agent.review(code, context)
                context.qa_reviews.append(review)


                if review.approved:
                    logger.info(
                        "QA APROBADO en intento %d (score=%.2f)", dev_attempt, review.score
                    )
                    dev_success = True
                    break
                else:
                    logger.info(
                        "QA RECHAZADO intento %d/%d: %d issues",
                        dev_attempt, MAX_DEV_RETRIES, len(review.issues),
                    )
                    self._emit(_EVT_QA_REJECTED, {
                        "project_id": project_id,
                        "attempt":    dev_attempt,
                        "issues":     review.issues[:5],
                    })
                    if dev_attempt == MAX_DEV_RETRIES:
                        return self._fail(
                            project_id, brief.brief_id, phases, artifacts, t0,
                            f"QA rechazo 3 veces -- INV-TEAM.4"
                        )


            if not dev_success:
                return self._fail(project_id, brief.brief_id, phases, artifacts, t0, "DEV fallido")


            context.current_phase = TeamPhase.DOCUMENTATION


            # --- FASE 5: DOCS -> Documentation ---
            docs_record, docs = await self._run_phase(
                TeamPhase.DOCUMENTATION, TeamRole.DOCS, context, artifacts
            )
            phases.append(docs_record)
            if docs_record.status == PhaseStatus.FAILED:
                return self._fail(project_id, brief.brief_id, phases, artifacts, t0, "DOCS fallido")
            context.docs_artifact = docs


            # --- INV-TEAM.5: Self-Rewarding por PM ---
            pm_agent   = self._agents[TeamRole.PM]
            total_ms   = int((time.monotonic() - t0) * 1000)
            result_tmp = ProjectResult(
                project_id=project_id,
                brief_id=brief.brief_id,
                status=ProjectStatus.RUNNING,
                phases=phases,
                artifacts=artifacts,
                total_duration_ms=total_ms,
            )
            pm_eval = await pm_agent.self_reward(context, result_tmp)
            logger.info(
                "PM Self-Rewarding: score=%.2f, meets_prd=%s, approved=%s",
                pm_eval.score, pm_eval.meets_prd, pm_eval.approved,
            )


            total_ms = int((time.monotonic() - t0) * 1000)
            result = ProjectResult(
                project_id=project_id,
                brief_id=brief.brief_id,
                status=ProjectStatus.COMPLETED,
                phases=phases,
                artifacts=artifacts,
                pm_evaluation=pm_eval,
                total_duration_ms=total_ms,
                total_tokens=sum(
                    len(a.content.split()) for a in artifacts
                ),
            )


            self._emit(_EVT_PROJECT_COMPLETE, {
                "project_id":  project_id,
                "agent_id":    self._agent_id,
                "tenant_id":   self._tenant_id,
                "status":      ProjectStatus.COMPLETED,
                "phases_done": len(phases),
                "pm_score":    pm_eval.score,
                "duration_ms": total_ms,
            })
            self._emit(_EVT_AUDIT, {
                "project_id":   project_id,
                "status":       ProjectStatus.COMPLETED,
                "total_tokens": result.total_tokens,
                "dev_attempts": context.dev_attempts,
            })


            return result


        except Exception as exc:
            logger.error("SyntheticTeam.execute_project error: %s", exc)
            return self._fail(
                project_id, brief.brief_id, phases, artifacts, t0, str(exc)
            )


    # -----------------------------------------------------------------------
    # _run_phase -- ejecuta un rol y valida el artefacto (INV-TEAM.2)
    # -----------------------------------------------------------------------


    async def _run_phase(
        self,
        phase:     TeamPhase,
        role:      TeamRole,
        context:   TeamContext,
        artifacts: list[TeamArtifact],
    ) -> tuple[PhaseRecord, TeamArtifact]:
        """
        Ejecuta la fase y valida que el artefacto no este vacio (INV-TEAM.2).
        Emite team.phase_complete.
        """
        agent = self._agents[role]
        t0    = time.monotonic()


        try:
            artifact   = await agent.execute(context)
            duration_ms = int((time.monotonic() - t0) * 1000)


            # INV-TEAM.2: artefacto no vacio
            if artifact.is_empty:
                raise ValueError(f"INV-TEAM.2: {role} genero un artefacto vacio en fase {phase}")


            artifacts.append(artifact)
            record = PhaseRecord(
                phase=phase,
                status=PhaseStatus.COMPLETED,
                role=role,
                artifact_id=artifact.artifact_id,
                duration_ms=duration_ms,
                attempt=context.dev_attempts if role == TeamRole.DEV else 1,
            )


            self._emit(_EVT_PHASE_COMPLETE, {
                "project_id":  context.project_id,
                "phase":       phase,
                "role":        role,
                "artifact_id": artifact.artifact_id,
                "sha256":      artifact.sha256[:16],  # prefijo para log
                "duration_ms": duration_ms,
            })
            logger.info(
                "_run_phase: %s/%s completado en %dms (sha256=%s...)",
                phase, role, duration_ms, artifact.sha256[:8],
            )
            return record, artifact


        except Exception as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            logger.error("_run_phase: %s/%s fallido: %s", phase, role, exc)
            from schema_res176 import TeamArtifact as TA
            empty = TA(
                project_id=context.project_id,
                phase=phase,
                role=role,
                content="",
            )
            record = PhaseRecord(
                phase=phase,
                status=PhaseStatus.FAILED,
                role=role,
                artifact_id=empty.artifact_id,
                duration_ms=duration_ms,
            )
            return record, empty


    # -----------------------------------------------------------------------
    # _fail -- helper para retornar ProjectResult.FAILED
    # -----------------------------------------------------------------------


    def _fail(
        self,
        project_id: str,
        brief_id:   str,
        phases:     list[PhaseRecord],
        artifacts:  list[TeamArtifact],
        t0:         float,
        error:      str,
    ) -> ProjectResult:
        total_ms = int((time.monotonic() - t0) * 1000)
        self._emit(_EVT_AUDIT, {
            "project_id": project_id,
            "status":     ProjectStatus.FAILED,
            "error":      error,
            "duration_ms": total_ms,
        })
        return ProjectResult(
            project_id=project_id,
            brief_id=brief_id,
            status=ProjectStatus.FAILED,
            phases=phases,
            artifacts=artifacts,
            error=error,
            total_duration_ms=total_ms,
        )


    # -----------------------------------------------------------------------
    # API auxiliar
    # -----------------------------------------------------------------------


    def get_phase_status(self, project_id: str) -> list[dict[str, str]]:
        """Placeholder -- en produccion persistir estado de fases por project_id."""
        return []


    def request_revision(
        self, project_id: str, phase: TeamPhase, feedback: str
    ) -> None:
        """Emite solicitud de revision HITL."""
        self._emit(_EVT_REVISION_NEEDED, {
            "project_id": project_id,
            "phase":      phase,
            "feedback":   feedback,
            "agent_id":   self._agent_id,
        })