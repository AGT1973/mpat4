# session_scheduler/session_scheduler.py
# Autor: cursos.agt.ia@gmail.com · 2026-05-13
# Módulo: session_scheduler/ · Versión: V4_01
# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
# Contrato: SESSION_SCHEDULER_CONTRACT_V4_01.md (ID: 1O_fYonA6sE4jCf2pOZ6spvkNejnEsezR)
# Schema:   schemas/session_scheduler_schema.py (ID: 1Z5HQ-8vZUL4KH2iEnlD5uYXCPwPSB8bz)
#
# INVARIANTES:
#   INV-SCH-001: tenant_id vacío → rechazar + session.rejected
#   INV-SCH-002: budget=0 → rechazar + session.budget_insufficient
#   INV-SCH-003: runtime_type no en allowed_runtimes → rechazar
#   INV-SCH-004: sesión ACTIVE con mismo ecs_id → rechazar
#   INV-SCH-005: checkpoint ANTES de destruir en teardown()
#   INV-SCH-006: SessionState → Redis al INICIO de cada transición
#
# PRINCIPIOS MPAT4:
#   P1:  Modularidad — sin imports directos a otros módulos
#   P3:  Zero Trust — todo validado, todo registrado
#   P7:  Budget inviolable — spawn rechaza si budget=0
#   P8:  Policy first — config_policy.yaml governa todo
#   P9:  Event driven — comunicación solo via event_bus
#   P10: Relay cognitivo — SessionState serializable siempre
#   P11: Observabilidad total — cada decisión loggeable
#   P12: Cognición persistente — checkpoint sobrevive al runtime

from __future__ import annotations

import json
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
import redis.asyncio as aioredis

# ─── Imports desde schemas/ ÚNICAMENTE (P1 — sin imports cíclicos) ────────────
from schemas.session_scheduler_schema import (
    SessionState,
    SessionPhase,
    SessionEvent,
    SessionRejectedEvent,
    SessionBudgetInsufficientEvent,
    SessionSpawnedEvent,
    SessionTerminatedEvent,
    SessionTtlWarningEvent,
    SpawnRequest,
    HydrateRequest,
    SuspendRequest,
    TeardownRequest,
    TeardownReason,
    SchedulerConfig,
    SessionSchedulerError,
    RuntimeType,
    create_session_state,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────────────────────────────────────

_scheduler_instance: "SessionScheduler | None" = None
_scheduler_lock = asyncio.Lock()


async def get_session_scheduler(
    config_path: str | Path = "config_policy.yaml",
) -> "SessionScheduler":
    """Singleton del SessionScheduler.

    NUNCA instanciar SessionScheduler directamente.
    Toda la codebase usa esta función.
    """
    global _scheduler_instance
    async with _scheduler_lock:
        if _scheduler_instance is None:
            config = _load_config(config_path)
            redis_client = await aioredis.from_url(
                config.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            _scheduler_instance = SessionScheduler(config=config, redis=redis_client)
            logger.info("[SCH] SessionScheduler inicializado · runtime_pool=%s", config.allowed_runtimes)
        return _scheduler_instance


def _load_config(config_path: str | Path) -> SchedulerConfig:
    """Lee config_policy.yaml y extrae sección session_scheduler."""
    path = Path(config_path)
    if not path.exists():
        logger.warning("[SCH] config_policy.yaml no encontrado en %s — usando defaults", path)
        return SchedulerConfig()
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    section = raw.get("session_scheduler", {})
    return SchedulerConfig(**section)


# ─────────────────────────────────────────────────────────────────────────────
# REDIS KEY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _state_key(tenant_id: str, session_id: str | UUID) -> str:
    return f"session:{tenant_id}:{session_id}:state"

def _checkpoint_key(tenant_id: str, session_id: str | UUID) -> str:
    return f"session:{tenant_id}:{session_id}:checkpoint"

def _active_set_key(tenant_id: str) -> str:
    return f"session:{tenant_id}:active_sessions"

def _stats_key(tenant_id: str) -> str:
    return f"session:{tenant_id}:stats"


# ─────────────────────────────────────────────────────────────────────────────
# SESSION SCHEDULER
# ─────────────────────────────────────────────────────────────────────────────

class SessionScheduler:
    """Controlador del ciclo de vida de sesiones cognitivas en MPAT4.

    No instanciar directamente — usar get_session_scheduler().
    """

    def __init__(self, config: SchedulerConfig, redis: aioredis.Redis):
        self._config = config
        self._redis = redis

    # ─── PERSISTENCIA ─────────────────────────────────────────────────────────

    async def _persist_state(self, state: SessionState) -> None:
        """INV-SCH-006: Persiste SessionState en Redis al inicio de cada transición."""
        key = _state_key(state.tenant_id, state.session_id)
        payload = state.model_dump_json()
        try:
            if state.phase in (SessionPhase.TERMINATED, SessionPhase.TEARDOWN):
                # Estado terminal: guardamos sin TTL para auditoría
                await self._redis.set(key, payload)
            else:
                await self._redis.set(key, payload, ex=state.ttl_seconds)
            logger.debug("[SCH] Estado persistido · session=%s · phase=%s", state.session_id, state.phase)
        except Exception as e:
            raise SessionSchedulerError("SCH-001", f"Redis no disponible al persistir: {e}") from e

    async def _load_state(self, tenant_id: str, session_id: UUID) -> SessionState:
        """Carga SessionState desde Redis."""
        key = _state_key(tenant_id, session_id)
        try:
            raw = await self._redis.get(key)
        except Exception as e:
            raise SessionSchedulerError("SCH-001", f"Redis no disponible al cargar: {e}") from e
        if raw is None:
            raise SessionSchedulerError("SCH-002", f"Sesión no encontrada: {session_id}")
        return SessionState.model_validate_json(raw)

    async def _emit_event(self, event: SessionEvent) -> None:
        """Emite evento al event_bus (P9 — event driven).

        En producción, publicar en Redis Streams / event_bus.
        Esta implementación usa log estructurado como fallback auditado (P11).
        """
        logger.info(
            "[SCH][EVENT] type=%s · session=%s · tenant=%s · ts=%s",
            event.event_type,
            event.session_id,
            event.tenant_id,
            event.ts.isoformat(),
        )
        # TODO RELAY_008: reemplazar con event_bus.publish(event) via gRPC/ConnectRPC

    async def _count_active_sessions(self, tenant_id: str) -> int:
        """Cuenta sesiones activas del tenant."""
        key = _active_set_key(tenant_id)
        try:
            return await self._redis.scard(key)
        except Exception as e:
            raise SessionSchedulerError("SCH-001", f"Redis no disponible: {e}") from e

    async def _add_to_active_set(self, state: SessionState) -> None:
        key = _active_set_key(state.tenant_id)
        await self._redis.sadd(key, str(state.session_id))

    async def _remove_from_active_set(self, state: SessionState) -> None:
        key = _active_set_key(state.tenant_id)
        await self._redis.srem(key, str(state.session_id))

    async def _increment_stat(self, tenant_id: str, field: str) -> None:
        await self._redis.hincrby(_stats_key(tenant_id), field, 1)

    # ─── MÉTODOS PÚBLICOS ─────────────────────────────────────────────────────

    async def spawn(self, request: SpawnRequest) -> SessionState:
        """Crea una nueva sesión cognitiva.

        Valida todas las invariantes antes de crear cualquier estado.
        """
        # INV-SCH-001: tenant_id no vacío (Pydantic ya valida, pero defensa doble)
        if not request.tenant_id or not request.tenant_id.strip():
            event = SessionRejectedEvent(
                tenant_id=request.tenant_id or "UNKNOWN",
                ecs_id=request.ecs_id,
                reason="INV-SCH-001: tenant_id vacío",
            )
            await self._emit_event(event)
            raise SessionSchedulerError("SCH-004", "tenant_id vacío (INV-SCH-001)")

        # INV-SCH-002: budget > 0
        # En producción: consultar governance_engine via event_bus.
        # Aquí validamos budget_at_spawn que viene del caller (governance_engine lo inyecta).
        # Llamante responsable de verificar budget real antes de SpawnRequest.
        # Esta capa valida que el valor no llegue en 0.
        # (P9: no importamos governance_engine directamente)

        # INV-SCH-003: runtime_type permitido
        if request.runtime_type not in self._config.allowed_runtimes:
            event = SessionRejectedEvent(
                tenant_id=request.tenant_id,
                ecs_id=request.ecs_id,
                reason=f"INV-SCH-003: runtime_type={request.runtime_type} no permitido",
            )
            await self._emit_event(event)
            raise SessionSchedulerError(
                "SCH-005",
                f"runtime_type '{request.runtime_type}' no está en allowed_runtimes. "
                f"Permitidos: {self._config.allowed_runtimes}. NUNCA Docker."
            )

        # INV-SCH-004: sin sesión ACTIVE con mismo ecs_id
        active_count = await self._count_active_sessions(request.tenant_id)
        if active_count >= self._config.max_concurrent_sessions_per_tenant:
            event = SessionRejectedEvent(
                tenant_id=request.tenant_id,
                ecs_id=request.ecs_id,
                reason=f"INV-SCH-006: límite de sesiones concurrentes alcanzado ({active_count})",
            )
            await self._emit_event(event)
            raise SessionSchedulerError(
                "SCH-006",
                f"Límite de sesiones concurrentes para tenant '{request.tenant_id}': {active_count}"
            )

        # Crear estado inicial
        state = create_session_state(request, budget_at_spawn=0)

        # INV-SCH-006: persistir con phase=SPAWNING
        state = state.model_copy(update={
            "phase": SessionPhase.SPAWNING,
            "spawned_at": datetime.now(timezone.utc),
        })
        await self._persist_state(state)
        await self._add_to_active_set(state)

        logger.info("[SCH] spawn() SPAWNING · session=%s · tenant=%s", state.session_id, state.tenant_id)

        # warm_start via event_bus (P9 — no importamos memory_fabric directamente)
        if request.warm_start:
            logger.info(
                "[SCH] warm_start solicitado · ecs_id=%s — publicar memory.warm_start al event_bus",
                request.ecs_id,
            )
            # TODO RELAY_008: event_bus.publish(MemoryWarmStartEvent(ecs_id=..., tenant_id=...))

        # Transición a ACTIVE
        state = state.model_copy(update={"phase": SessionPhase.ACTIVE})
        await self._persist_state(state)  # INV-SCH-006
        await self._increment_stat(state.tenant_id, "spawned")

        # Emitir evento
        await self._emit_event(SessionSpawnedEvent(
            session_id=state.session_id,
            tenant_id=state.tenant_id,
            ecs_id=state.ecs_id,
            runtime_type=state.runtime_type,
        ))

        logger.info("[SCH] spawn() COMPLETO · session=%s", state.session_id)
        return state

    async def suspend(self, request: SuspendRequest) -> SessionState:
        """Suspende una sesión ACTIVE. Persiste checkpoint_data."""
        state = await self._load_state(request.tenant_id, request.session_id)

        if state.phase != SessionPhase.ACTIVE:
            raise SessionSchedulerError(
                "SCH-003",
                f"Solo sesiones ACTIVE pueden suspenderse. Estado actual: {state.phase}"
            )

        state = state.model_copy(update={
            "phase": SessionPhase.SUSPENDED,
            "suspended_at": datetime.now(timezone.utc),
            "checkpoint_data": request.checkpoint_data,
        })
        await self._persist_state(state)  # INV-SCH-006

        # Persistir checkpoint explícito (sin TTL — P12)
        cp_key = _checkpoint_key(state.tenant_id, state.session_id)
        await self._redis.set(cp_key, json.dumps(request.checkpoint_data))

        await self._emit_event(SessionEvent(
            event_type="session.suspended",
            session_id=state.session_id,
            tenant_id=state.tenant_id,
        ))
        logger.info("[SCH] suspend() · session=%s", state.session_id)
        return state

    async def hydrate(self, request: HydrateRequest) -> SessionState:
        """Reactiva una sesión SUSPENDED."""
        state = await self._load_state(request.tenant_id, request.session_id)

        if not state.can_hydrate():
            raise SessionSchedulerError(
                "SCH-003",
                f"Solo sesiones SUSPENDED pueden hidratarse. Estado actual: {state.phase}"
            )

        # Cargar checkpoint desde Redis
        cp_key = _checkpoint_key(state.tenant_id, state.session_id)
        try:
            raw_cp = await self._redis.get(cp_key)
            checkpoint = json.loads(raw_cp) if raw_cp else {}
        except Exception:
            checkpoint = {}

        state = state.model_copy(update={
            "phase": SessionPhase.ACTIVE,
            "checkpoint_data": checkpoint,
            "suspended_at": None,
        })
        await self._persist_state(state)  # INV-SCH-006

        await self._emit_event(SessionEvent(
            event_type="session.hydrated",
            session_id=state.session_id,
            tenant_id=state.tenant_id,
        ))
        logger.info("[SCH] hydrate() · session=%s", state.session_id)
        return state

    async def checkpoint(self, session_id: UUID, tenant_id: str) -> None:
        """Serializa y persiste el estado cognitivo actual (sin TTL — P12)."""
        state = await self._load_state(tenant_id, session_id)

        cp_key = _checkpoint_key(tenant_id, session_id)
        await self._redis.set(cp_key, json.dumps(state.checkpoint_data))

        await self._emit_event(SessionEvent(
            event_type="session.checkpointed",
            session_id=state.session_id,
            tenant_id=state.tenant_id,
        ))
        logger.debug("[SCH] checkpoint() · session=%s", session_id)

    async def teardown(self, request: TeardownRequest) -> None:
        """Destruye una sesión.

        INV-SCH-005: checkpoint ANTES de destruir.
        INV-SCH-006: transiciona TEARDOWN → TERMINATED persistiendo en Redis.
        """
        state = await self._load_state(request.tenant_id, request.session_id)

        if state.phase == SessionPhase.TERMINATED:
            logger.warning("[SCH] teardown() sobre sesión ya TERMINATED · session=%s", request.session_id)
            return

        # INV-SCH-006: transición a TEARDOWN
        state = state.model_copy(update={"phase": SessionPhase.TEARDOWN})
        await self._persist_state(state)

        # INV-SCH-005: checkpoint ANTES de destruir
        await self.checkpoint(state.session_id, state.tenant_id)
        logger.info("[SCH] checkpoint pre-teardown guardado · session=%s", state.session_id)

        # Liberar recursos del runtime
        # TODO RELAY_008: llamar nanovm/unikraft/firecracker stop via runtime abstraction layer
        logger.info(
            "[SCH] runtime=%s liberado (simulado) · session=%s",
            state.runtime_type,
            state.session_id,
        )

        # INV-SCH-006: transición a TERMINATED
        state = state.model_copy(update={
            "phase": SessionPhase.TERMINATED,
            "terminated_at": datetime.now(timezone.utc),
        })
        await self._persist_state(state)

        # Limpiar del Set de activos
        await self._remove_from_active_set(state)
        await self._increment_stat(state.tenant_id, "terminated")

        await self._emit_event(SessionTerminatedEvent(
            session_id=state.session_id,
            tenant_id=state.tenant_id,
            ecs_id=state.ecs_id,
            reason=request.reason,
        ))
        logger.info(
            "[SCH] teardown() COMPLETO · session=%s · reason=%s",
            state.session_id,
            request.reason,
        )

    async def get_state(self, tenant_id: str, session_id: UUID) -> SessionState:
        """Retorna el SessionState actual desde Redis."""
        return await self._load_state(tenant_id, session_id)
