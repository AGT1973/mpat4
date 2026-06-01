"""
T008__session_scheduler_v4.py
DESTINO FINAL: session_scheduler/session_scheduler_v4.py
RES.163 - MPAT4 | Relay: RELAY_009 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


INV-SCHED.1: OPA antes de SPAWN.
INV-SCHED.2: warm pool repone en background - asyncio.create_task().
INV-SCHED.3: hydration idempotente (V4-INV-MEMORY.4).
INV-SCHED.4: budget antes del boot - nunca post-boot.
INV-WARM.1: pool_size configurable default 5.
INV-WARM.2: reponer tras cada SPAWN.
INV-WARM.3: idle TTL 300s.


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
import asyncio, logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from fase0_schemas import SessionEnvelope, SessionPhase, EventEnvelope
from governance_engine.opa_engine import OPAEngine, OPADecision
from event_bus_v4 import EventBusV4
from core.kernel_bridge import CognitiveKernelBridge
from session_scheduler.hydration_loader import HydrationLoader
from session_scheduler.session_scheduler_schema_v4 import WarmPoolState, WarmPoolEntry, SchedulerConfig


logger = logging.getLogger("mpat.session_scheduler")




class WarmPool:
    def __init__(self, config: SchedulerConfig, kernel: CognitiveKernelBridge):
        self._config = config
        self._kernel = kernel
        self._pool: list[WarmPoolEntry] = []
        self._lock = asyncio.Lock()


    async def initialize(self, tenant_id: str) -> None:
        async with self._lock:
            for _ in range(self._config.warm_pool_size):
                self._pool.append(await self._boot(tenant_id))
        logger.info("WarmPool init tenant=%s size=%d", tenant_id, len(self._pool))


    async def pop(self, tenant_id: str) -> Optional[WarmPoolEntry]:
        async with self._lock:
            now = datetime.now(timezone.utc)
            self._pool = [e for e in self._pool
                          if (now - e.booted_at).total_seconds() < self._config.idle_ttl_seconds]
            return self._pool.pop(0) if self._pool else None


    async def replenish(self, tenant_id: str) -> None:
        async with self._lock:
            for _ in range(self._config.warm_pool_size - len(self._pool)):
                try:
                    self._pool.append(await self._boot(tenant_id))
                except Exception as exc:
                    logger.warning("replenish error: %s", exc)


    async def _boot(self, tenant_id: str) -> WarmPoolEntry:
        uid = await self._kernel.spawn_unikernel(tenant_id=tenant_id)
        return WarmPoolEntry(unikernel_id=uid, tenant_id=tenant_id, booted_at=datetime.now(timezone.utc))


    def state(self, tenant_id: str) -> WarmPoolState:
        return WarmPoolState(tenant_id=tenant_id, available_unikernels=len(self._pool),
                             target_pool_size=self._config.warm_pool_size,
                             last_replenished_at=datetime.now(timezone.utc))




class SessionSchedulerV4:
    """
    Ciclo completo: COLD_BOOT|HYDRATING -> ACTIVE -> TEARDOWN -> TERMINATED.


    start_session flujo:
      1. deduct_budget (INV-SCHED.4)
      2. OPA evaluate (INV-SCHED.1)  -> Deny: return_budget + governance.violation
      3. warm pool pop o cold boot
      4. hydration si relay_packet_id (INV-SCHED.3)
      5. publish session.started
      6. asyncio.create_task(replenish) (INV-SCHED.2)
      7. return SessionEnvelope ACTIVE


    teardown_session flujo:
      1. publish session.teardown
      2. RelayExporter.export() si relay_export_required
      3. destroy_unikernel
      4. return_budget al padre (P7 Conservation Law)
      5. asyncio.create_task(replenish)
    """
    def __init__(self, config: SchedulerConfig, kernel: CognitiveKernelBridge,
                 opa: OPAEngine, event_bus: EventBusV4, hydration_loader: HydrationLoader):
        self._config = config
        self._kernel = kernel
        self._opa = opa
        self._event_bus = event_bus
        self._hydration_loader = hydration_loader
        self._warm_pool = WarmPool(config, kernel)
        self._active: dict[str, SessionEnvelope] = {}


    async def initialize(self, tenant_id: str) -> None:
        await self._warm_pool.initialize(tenant_id)


    async def start_session(self, tenant_id: str, agent_id: str, agent_card_id: str,
                             budget_tokens: int, relay_packet_id: Optional[str] = None) -> SessionEnvelope:
        session_id = str(uuid4())


        # INV-SCHED.4
        if not await self._kernel.deduct_budget(tenant_id, session_id, budget_tokens):
            raise InsufficientBudgetError(f"tenant={tenant_id} budget insuficiente")


        # INV-SCHED.1
        decision: OPADecision = await self._opa.evaluate(
            tenant_id=tenant_id, action="spawn_agent",
            context={"agent_id": agent_id, "agent_card_id": agent_card_id,
                     "budget_tokens": budget_tokens, "session_id": session_id})
        if decision.deny:
            await self._kernel.return_budget(tenant_id, session_id, budget_tokens, None)
            await self._event_bus.publish(EventEnvelope(
                event_type="governance.violation", tenant_id=tenant_id,
                payload={"session_id": session_id, "agent_id": agent_id,
                         "reason": decision.reason, "action": "spawn_agent"}))
            raise PolicyDeniedError(f"OPA Deny spawn agent={agent_id}: {decision.reason}")


        warm = await self._warm_pool.pop(tenant_id)
        unikernel_id = warm.unikernel_id if warm else await self._kernel.spawn_unikernel(tenant_id=tenant_id)


        hydrated = False
        if relay_packet_id:  # INV-SCHED.3
            hydrated = await self._hydration_loader.load(tenant_id, session_id, relay_packet_id)


        session = SessionEnvelope(
            session_id=session_id, tenant_id=tenant_id, agent_id=agent_id,
            unikernel_id=unikernel_id, phase=SessionPhase.ACTIVE,
            relay_packet_id=relay_packet_id, relay_export_required=relay_packet_id is not None,
            budget_tokens=budget_tokens)
        self._active[session_id] = session


        await self._event_bus.publish(EventEnvelope(
            event_type="session.started", tenant_id=tenant_id,
            payload={"session_id": session_id, "agent_id": agent_id,
                     "unikernel_id": unikernel_id, "hydrated": hydrated, "budget_tokens": budget_tokens}))


        asyncio.create_task(self._warm_pool.replenish(tenant_id))  # INV-SCHED.2
        logger.info("ACTIVE session=%s agent=%s hydrated=%s", session_id, agent_id, hydrated)
        return session


    async def teardown_session(self, session_id: str, tenant_id: str, reason: str) -> None:
        session = self._active.pop(session_id, None)
        if not session:
            logger.warning("teardown: session=%s no encontrada", session_id)
            return
        await self._event_bus.publish(EventEnvelope(
            event_type="session.teardown", tenant_id=tenant_id,
            payload={"session_id": session_id, "agent_id": session.agent_id,
                     "reason": reason, "relay_export_required": session.relay_export_required}))
        if session.relay_export_required:
            try:
                from session_scheduler.relay_exporter import RelayExporter
                await RelayExporter(self._kernel).export(session_id, tenant_id)
            except Exception as exc:
                logger.error("RelayExporter error session=%s: %s", session_id, exc)
        await self._kernel.destroy_unikernel(tenant_id, session.unikernel_id)
        await self._kernel.return_budget(tenant_id, session_id, session.budget_tokens, None)
        asyncio.create_task(self._warm_pool.replenish(tenant_id))
        logger.info("TERMINATED session=%s reason=%s", session_id, reason)


    def warm_pool_state(self, tenant_id: str) -> WarmPoolState:
        return self._warm_pool.state(tenant_id)


    def active_count(self) -> int:
        return len(self._active)




class InsufficientBudgetError(Exception): pass
class PolicyDeniedError(Exception): pass