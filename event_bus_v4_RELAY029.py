# MPAT4_DEST
# destino: runtime
# nombre: event_bus_v4.py
# alumno: ai.mpat.info@gmail.com
# relay: RELAY_029
# que has usado el formato de razonamiento adaptado por AGT

# event_bus/event_bus_v4.py
## Resuelve: DT-BUS-004 — integracion BusPolicy en EventBusV4.__init__
## Version: V4_RELAY029
## Extiende: event_bus_v4.py (ID: 1pMu_-qIc5hjWGh8BaPlQ6bZCZvbeI1Uq)
## Depende: event_bus/bus_policy.py (bus_policy_V1_00_RELAY028.py)
## GARANTIA RETRO-COMPAT: policy=None -> BusPolicy.from_yaml() -> defaults() si no existe yaml
##   Todos los tests existentes pasan sin modificacion (no pasan policy -> defaults identicos)
## INV-BUS.1: todo evento tiene tenant_id -- nunca cross-tenant routing.
## INV-BUS.2: el bus NO interpreta el payload -- solo enruta por event_type.
## INV-BUS.3: handlers registrados son por (tenant_id, event_type) -- nunca globales.
## INV-BUS.4: un evento sin handler registrado emite WARNING en OTel, no crash.
## INV-BUS.5: CRITICAL events se procesan ANTES que cualquier cola pendiente.
## INV-BUS.6: el bus es el UNICO canal de I/O entre subsistemas del Cognitive Kernel.

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Awaitable, Callable, Optional
from uuid import uuid4

logger = logging.getLogger("mpat4.event_bus")


# ------------------------------------------------------------------------------
# Payloads tipados para los 6 event_types canonicos
# Cada payload es Pydantic-free (dataclass frozen) para maxima velocidad.
# La serializacion Protobuf ocurre en el productor antes de EventEnvelope.payload
# ------------------------------------------------------------------------------

@dataclass(frozen=True)
class SessionStartedPayload:
    """
    session.started -- sesion de agente iniciada.

    Emitido por: Cognitive Kernel (session_scheduler/)
    Consumido por: governance_engine/ (activar policies), observability/ (span inicio)

    cold_boot=True: sin RelayPacket previo -- sesion desde cero.
    cold_boot=False: sesion hidratada desde RelayPacket (relay_packet_id presente).

    INV-SESSION.1: session_id unico por tenant.
    """
    tenant_id:        str
    session_id:       str
    agent_id:         str
    unikernel_id:     str
    cold_boot:        bool
    relay_packet_id:  Optional[str]  = None
    budget_tokens:    int             = 4096
    occurred_at:      str             = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class SessionTeardownPayload:
    """
    session.teardown -- sesion terminando, debe exportar RelayPacket.

    Emitido por: Cognitive Kernel al recibir SIGTERM del unikernel o
                 al detectar budget.exhausted o fin de tarea.
    Consumido por: memory_fabric/ (consolidar), relay_exporter/ (exportar RelayPacket)

    relay_export_required=True si habia memoria episodica o semantica activa.
    INV-BUS.5: si priority=CRITICAL, se procesa antes que cualquier cola pendiente.

    TRAMPA EDUCATIVA: "teardown y terminated son lo mismo".
    FALSO: teardown es el inicio del proceso de cierre (aun hay trabajo --
    exportar RelayPacket). terminated es el estado final cuando el unikernel
    ya fue destruido. Entre teardown y terminated hay un ciclo completo de
    consolidacion y exportacion de memoria.
    """
    tenant_id:             str
    session_id:            str
    agent_id:              str
    unikernel_id:          str
    relay_export_required: bool
    budget_consumed:       int
    budget_remaining:      int
    termination_reason:    str   # "task_completed" | "budget_exhausted" | "timeout" | "error"
    occurred_at:           str   = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class MemoryConsolidatedPayload:
    """
    memory.consolidated -- ciclo de consolidacion completado.

    Emitido por: memory_fabric/ al completar un ciclo DreamCycle (RES.142 V3)
    Consumido por: relay_exporter/ (incluir en RelayPacket), observability/

    fragments_consolidated: cuantos fragmentos episodicos se procesaron.
    hebbiano_updates: cuantos pesos hebbianos se actualizaron.
    q_value_updates: cuantos Q-values se actualizaron (RES.119 V3).
    """
    tenant_id:             str
    session_id:            str
    agent_id:              str
    fragments_consolidated: int
    hebbiano_updates:       int
    q_value_updates:        int
    consolidation_ms:       float
    occurred_at:            str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class BudgetExhaustedPayload:
    """
    budget.exhausted -- budget de tokens agotado (P7 conservation law).

    Emitido por: Cognitive Kernel al detectar budget_consumed >= budget_tokens.
    Consumido por: session_scheduler/ (iniciar teardown), governance_engine/ (audit),
                   observability/ (alerta CRITICAL)

    INV-BUS.5: priority=CRITICAL -- se procesa ANTES que cualquier cola pendiente.
    P7 (V3 heredado): Conservation Law -- budget_consumed nunca supera budget_tokens.
    Este evento NO viola P7 -- es la notificacion de que P7 esta siendo respetado
    (el sistema para antes de superar el limite).

    TRAMPA EDUCATIVA: "budget.exhausted significa que el sistema fallo".
    FALSO: es exactamente lo contrario. budget.exhausted es P7 funcionando
    correctamente -- el sistema detecta el limite y se detiene ordenadamente
    (emite session.teardown). Un sistema que NO emite este evento y continua
    consumiendo es el que esta fallando (violacion de P7).
    """
    tenant_id:        str
    session_id:       str
    agent_id:         str
    budget_tokens:    int
    budget_consumed:  int
    last_tool_id:     Optional[str]  # tool que agoto el budget (si aplica)
    occurred_at:      str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class GovernanceViolationPayload:
    """
    governance.violation -- politica OPA/Cedar violada.

    Emitido por: governance_engine/ al evaluar PolicyContract y detectar violacion.
    Consumido por: Cognitive Kernel (bloquear accion), observability/ (alerta CRITICAL),
                   audit_log/ (registro permanente)

    INV-BUS.5: priority=CRITICAL -- se procesa ANTES que cualquier cola pendiente.
    INV-POLICY.1 (FASE 0): toda violacion tiene tenant_id -- nunca global.

    action_blocked: la accion que fue bloqueada por la policy.
    policy_id: ID de la PolicyContract que detecto la violacion.
    violation_code: codigo especifico de la violacion (definido en policy_code Rego/Cedar).

    TRAMPA EDUCATIVA: "governance.violation solo aplica a tool_calls externas".
    FALSO: governance.violation aplica a CUALQUIER accion del sistema -- incluyendo
    acciones internas del Cognitive Kernel como spawning de agentes, consolidacion
    de memoria, o modificacion de presupuesto. Las politicas son transversales --
    no solo guardianes del perimetro externo.
    """
    tenant_id:        str
    session_id:       str
    agent_id:         str
    policy_id:        str
    policy_engine:    str   # "opa" | "cedar"
    action_blocked:   str
    violation_code:   str
    violation_detail: str
    occurred_at:      str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class AgentSpawnedPayload:
    """
    agent.spawned -- agente nuevo creado en el Cognitive Kernel.

    Emitido por: Cognitive Kernel al completar SPAWN exitoso.
    Consumido por: agent_registry/ (registrar AgentCard), observability/ (span lifecycle),
                   governance_engine/ (activar policies del agente)

    parent_agent_id: agente padre si es un sub-agente (Managed Agents V3 RES.055).
    None si es un agente raiz creado directamente por el Orchestrator.

    unikernel_boot_ms: tiempo de boot del Firecracker MicroVM (target < 50ms).
    INV-ECS-V4.1: todo agente spawneado tiene unikernel_id.
    """
    tenant_id:         str
    session_id:        str
    agent_id:          str
    unikernel_id:      str
    agent_card_id:     str
    parent_agent_id:   Optional[str]
    unikernel_boot_ms: float
    cold_boot:         bool
    occurred_at:       str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ------------------------------------------------------------------------------
# Handler type
# ------------------------------------------------------------------------------

EventHandler = Callable[[str, bytes], Awaitable[None]]
# firma: async def handler(tenant_id: str, payload_bytes: bytes) -> None


# ------------------------------------------------------------------------------
# EventBusV4 — con integracion BusPolicy (DT-BUS-004)
# ------------------------------------------------------------------------------

class EventBusV4:
    """
    Bus de eventos central de MPAT4.

    Routing por (tenant_id, event_type). Aislamiento absoluto entre tenants.
    Handlers async registrados por subsistema. CRITICAL events priority queue.

    DT-BUS-004: integracion BusPolicy via parametro policy en __init__.
    GARANTIA RETRO-COMPAT: policy=None -> BusPolicy.from_yaml() -> defaults()
        Todos los tests existentes sin modificacion.

    INV-BUS.1: todo evento tiene tenant_id -- nunca cross-tenant routing.
    INV-BUS.2: el bus NO interpreta el payload -- solo enruta por event_type.
    INV-BUS.3: handlers registrados son por (tenant_id, event_type).
    INV-BUS.4: evento sin handler emite WARNING, no crash.
    INV-BUS.5: CRITICAL events procesados antes que cualquier cola pendiente.
    INV-BUS.6: unico canal I/O entre subsistemas del Cognitive Kernel.
    """

    # Los 6 event_types canonicos -- ninguna otra constante es valida sin RES
    SESSION_STARTED       = "session.started"
    SESSION_TEARDOWN      = "session.teardown"
    MEMORY_CONSOLIDATED   = "memory.consolidated"
    BUDGET_EXHAUSTED      = "budget.exhausted"
    GOVERNANCE_VIOLATION  = "governance.violation"
    AGENT_SPAWNED         = "agent.spawned"

    # Fallback CRITICAL_EVENTS hardcodeado -- usado solo si BusPolicy no esta disponible
    # En produccion: policy.critical_events es la fuente canonica
    _CRITICAL_EVENTS_FALLBACK = frozenset({
        BUDGET_EXHAUSTED,
        GOVERNANCE_VIOLATION,
        SESSION_TEARDOWN,
    })

    def __init__(self, policy: Optional["BusPolicy"] = None) -> None:  # noqa: F821
        """
        Inicializa el EventBusV4.

        DT-BUS-004: parametro policy opcional.
        Si policy=None: carga desde BusPolicy.from_yaml() (retorna defaults si yaml ausente).
        GARANTIA: comportamiento identico al anterior cuando no se pasa policy.

        Args:
            policy: BusPolicy instancia. None = cargar desde yaml o usar defaults.
        """
        # Cargar policy -- retro-compatible: None -> from_yaml() -> defaults()
        if policy is None:
            try:
                from event_bus.bus_policy import BusPolicy
                self._policy = BusPolicy.from_yaml()
            except ImportError:
                logger.warning(
                    "DT-BUS-004: bus_policy no disponible -- usando CRITICAL_EVENTS_FALLBACK."
                )
                self._policy = None
        else:
            self._policy = policy

        # CRITICAL_EVENTS desde policy (INV-BUS.5) o fallback hardcodeado
        if self._policy is not None:
            self.CRITICAL_EVENTS: frozenset[str] = self._policy.critical_events
            self._loop_timeout_secs: float = self._policy.loop_timeout_secs
            self._default_budget_tokens: int = self._policy.default_tokens
        else:
            self.CRITICAL_EVENTS = self._CRITICAL_EVENTS_FALLBACK
            self._loop_timeout_secs = 0.05
            self._default_budget_tokens = 4096

        # handlers[(tenant_id, event_type)] = [handler1, handler2, ...]
        self._handlers: dict[tuple[str, str], list[EventHandler]] = defaultdict(list)
        # Cola CRITICAL separada -- procesada primero (INV-BUS.5)
        self._critical_queue: asyncio.Queue[tuple[str, str, str, bytes]] = asyncio.Queue()
        # Cola normal
        self._normal_queue: asyncio.Queue[tuple[str, str, str, bytes]] = asyncio.Queue()
        self._running = False
        self._stats: dict[str, int] = defaultdict(int)

        logger.debug(
            "EventBusV4 inicializado. loop_timeout=%.3fs default_tokens=%d critical_events=%s",
            self._loop_timeout_secs,
            self._default_budget_tokens,
            sorted(self.CRITICAL_EVENTS),
        )

    def register(
        self,
        tenant_id: str,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """
        Registra un handler para (tenant_id, event_type).

        INV-BUS.3: handler es por tenant -- nunca '*' como tenant_id.
        """
        if not tenant_id or tenant_id == "*":
            raise ValueError(
                "INV-BUS.3: tenant_id no puede ser vacio ni '*'. "
                "Los handlers son siempre por tenant especifico."
            )
        self._handlers[(tenant_id, event_type)].append(handler)
        logger.debug("handler registrado: tenant=%s event=%s", tenant_id, event_type)

    async def publish(
        self,
        tenant_id: str,
        event_type: str,
        payload_bytes: bytes,
        event_id: Optional[str] = None,
    ) -> str:
        """
        Publica un evento en el bus.

        INV-BUS.1: tenant_id obligatorio.
        INV-BUS.2: payload_bytes no interpretado -- bytes opacos.
        INV-BUS.5: CRITICAL events van a cola prioritaria.

        Retorna el event_id asignado.
        """
        if not tenant_id:
            raise ValueError("INV-BUS.1: tenant_id obligatorio en publish().")

        eid = event_id or str(uuid4())

        if event_type in self.CRITICAL_EVENTS:
            await self._critical_queue.put((eid, tenant_id, event_type, payload_bytes))
            self._stats["critical_published"] += 1
        else:
            await self._normal_queue.put((eid, tenant_id, event_type, payload_bytes))
            self._stats["normal_published"] += 1

        logger.debug("evento publicado: id=%s tenant=%s type=%s", eid[:8], tenant_id, event_type)
        return eid

    async def _dispatch(
        self,
        event_id: str,
        tenant_id: str,
        event_type: str,
        payload_bytes: bytes,
    ) -> None:
        """
        Despacha un evento a todos los handlers registrados.

        INV-BUS.4: sin handlers -> WARNING, no crash.
        """
        key = (tenant_id, event_type)
        handlers = self._handlers.get(key, [])

        if not handlers:
            logger.warning(
                "INV-BUS.4: evento sin handler registrado -- "
                "tenant=%s event=%s id=%s",
                tenant_id, event_type, event_id[:8]
            )
            self._stats["unhandled"] += 1
            return

        # Ejecutar handlers en paralelo -- fallo de uno no afecta a los otros
        results = await asyncio.gather(
            *[h(tenant_id, payload_bytes) for h in handlers],
            return_exceptions=True,
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "handler[%d] fallo para event=%s tenant=%s: %s",
                    i, event_type, tenant_id, result
                )
                self._stats["handler_errors"] += 1

        self._stats["dispatched"] += 1

    async def _process_loop(self) -> None:
        """
        Loop principal del bus.

        INV-BUS.5: drena cola CRITICAL antes de procesar normal.
        DT-BUS-004: usa self._loop_timeout_secs desde BusPolicy.
        """
        self._running = True
        while self._running:
            # Drena CRITICAL primero (INV-BUS.5)
            while not self._critical_queue.empty():
                eid, tid, etype, payload = await self._critical_queue.get()
                await self._dispatch(eid, tid, etype, payload)
                self._critical_queue.task_done()

            # Procesa un evento normal (si hay)
            try:
                eid, tid, etype, payload = await asyncio.wait_for(
                    self._normal_queue.get(), timeout=self._loop_timeout_secs
                )
                await self._dispatch(eid, tid, etype, payload)
                self._normal_queue.task_done()
            except asyncio.TimeoutError:
                pass  # sin eventos -- continuar loop

    async def start(self) -> None:
        """Inicia el loop de procesamiento."""
        asyncio.create_task(self._process_loop())
        logger.info("EventBusV4 iniciado.")

    async def stop(self) -> None:
        """Detiene el loop. Drena las colas pendientes antes de parar."""
        self._running = False
        # Drena lo que queda
        while not self._critical_queue.empty() or not self._normal_queue.empty():
            await asyncio.sleep(0.01)
        logger.info("EventBusV4 detenido. Stats: %s", dict(self._stats))

    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    @property
    def default_budget_tokens(self) -> int:
        """Budget de tokens por defecto desde BusPolicy. INV-BUS.1."""
        return self._default_budget_tokens


# ------------------------------------------------------------------------------
# Singleton por proceso
# ------------------------------------------------------------------------------

_bus_instance: Optional[EventBusV4] = None


def get_event_bus() -> EventBusV4:
    """
    Retorna el singleton del EventBusV4.

    INV-BUS.6: un solo bus por proceso -- todos los subsistemas usan este singleton.
    """
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBusV4()
    return _bus_instance


# ------------------------------------------------------------------------------
# Helpers de publicacion tipada -- evitan errores de event_type string
# ------------------------------------------------------------------------------

async def publish_session_started(
    bus: EventBusV4,
    payload: SessionStartedPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.SESSION_STARTED,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )


async def publish_session_teardown(
    bus: EventBusV4,
    payload: SessionTeardownPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.SESSION_TEARDOWN,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )


async def publish_memory_consolidated(
    bus: EventBusV4,
    payload: MemoryConsolidatedPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.MEMORY_CONSOLIDATED,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )


async def publish_budget_exhausted(
    bus: EventBusV4,
    payload: BudgetExhaustedPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.BUDGET_EXHAUSTED,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )


async def publish_governance_violation(
    bus: EventBusV4,
    payload: GovernanceViolationPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.GOVERNANCE_VIOLATION,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )


async def publish_agent_spawned(
    bus: EventBusV4,
    payload: AgentSpawnedPayload,
) -> str:
    import json
    return await bus.publish(
        tenant_id=payload.tenant_id,
        event_type=EventBusV4.AGENT_SPAWNED,
        payload_bytes=json.dumps(payload.__dict__).encode(),
    )
