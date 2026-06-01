"""
RES166__a2a_economy_engine.py
DESTINO FINAL: ecosystem/a2a_economy/a2a_economy_engine.py
RES.166 - MPAT4 | Relay: RELAY_012 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


P02 — Agent-to-Agent Economy Engine.
Sistema de intercambio de valor entre agentes autónomos sobre MPAT4.
Un agente puede "contratar" a otro para ejecutar una subtarea,
pagando con budget de tokens (P7 Conservation Law).


INVARIANTES:
  INV-A2A.1: escrow ANTES de que el vendedor empiece la tarea.
             El budget del comprador se bloquea al aceptar el contrato.
  INV-A2A.2: OPA valida TODA propuesta antes de crear el contrato.
             (hereda INV-OPA.2: toda Deny emite governance.violation)
  INV-A2A.3: contrato expirado → escrow devuelto al comprador automáticamente.
             TTL configurable, default 300s.
  INV-A2A.4: el vendedor recibe tokens SOLO después de settle_transaction()
             con resultado=SUCCESS. En DISPUTE o CANCELLED: escrow al comprador.
  INV-A2A.5: max N contratos concurrentes por tenant (default 10).
             Protege contra drenaje de budget por contratos masivos.
  INV-A2A.6: valor del contrato <= max_contract_pct del budget total del comprador.
             Protege contra contratos únicos que vacíen el presupuesto.


TRAMPA EDUCATIVA:
  "El A2A Economy es lo mismo que el AESP."
  FALSO: AESP regula la soberanía económica del agente frente al USUARIO.
  A2A Economy regula el intercambio de valor entre AGENTES.
  AESP responde a: ¿puede el agente gastar tokens del usuario?
  A2A responde a: ¿puede el agente A pagarle al agente B con sus tokens?
  Son capas diferentes: AESP es vertical (agente-usuario), A2A es horizontal (agente-agente).


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


from ecosystem.a2a_economy.a2a_schema import (
    A2AContract, A2AContractStatus, A2AContractConfig,
    A2AProposal, A2ASettlement, A2ADisputeResolution,
)
from cognitive_kernel.kernel_bridge import CognitiveKernelInterface
from governance_engine.opa_engine import OPAEngine
from event_bus_v4 import EventBusV4


logger = logging.getLogger("mpat.a2a_economy")




class A2AEconomyEngine:
    """
    Motor de economía agente-a-agente para MPAT4.


    Ciclo de vida de un contrato A2A:
      PROPOSED → ESCROWED → ACTIVE → COMPLETED | DISPUTED | CANCELLED | EXPIRED


    Flujo happy path:
      1. buyer llama propose_contract() → crea contrato en PROPOSED.
      2. OPA valida (INV-A2A.2).
      3. seller llama accept_contract() → escrow del budget (INV-A2A.1).
      4. seller ejecuta la tarea (fuera del scope del engine).
      5. buyer llama settle_transaction(SUCCESS) → tokens transferidos al seller.


    Flujo dispute:
      5b. buyer llama settle_transaction(DISPUTE) →
          OPA arbitra (INV-A2A.4) → escrow devuelto al comprador +
          penalización de reputación al vendedor.


    Flujo expirado:
      Timer background detecta TTL expirado (INV-A2A.3) →
      contrato → EXPIRED → escrow devuelto al comprador.
    """


    def __init__(
        self,
        kernel: CognitiveKernelInterface,
        opa: OPAEngine,
        event_bus: EventBusV4,
        config: Optional[A2AContractConfig] = None,
    ):
        self._kernel = kernel
        self._opa = opa
        self._event_bus = event_bus
        self._config = config or A2AContractConfig()
        # Registro activo de contratos: contract_id → A2AContract
        self._contracts: dict[str, A2AContract] = {}
        self._lock = asyncio.Lock()
        self._expiry_task: Optional[asyncio.Task] = None


    async def start(self) -> None:
        """Arranca el loop de expiración en background (INV-A2A.3)."""
        self._expiry_task = asyncio.create_task(
            self._expiry_loop(), name="a2a_expiry_loop"
        )
        logger.info("A2AEconomyEngine iniciado — TTL=%ds max_concurrent=%d",
                    self._config.contract_ttl_seconds, self._config.max_concurrent_contracts)


    async def stop(self) -> None:
        if self._expiry_task:
            self._expiry_task.cancel()


    # ------------------------------------------------------------------
    # propose_contract — comprador propone un contrato al vendedor
    # ------------------------------------------------------------------


    async def propose_contract(
        self,
        tenant_id: str,
        buyer_agent_id: str,
        seller_agent_id: str,
        budget_tokens: int,
        service_description: str,
        deliverable_spec: str,
    ) -> A2AContract:
        """
        El agente comprador propone un contrato al vendedor.


        INV-A2A.2: OPA valida antes de crear.
        INV-A2A.5: verifica que no se supere el límite de contratos concurrentes.
        INV-A2A.6: verifica que el valor no supere el max_contract_pct del budget.


        Retorna el contrato en estado PROPOSED (aún sin escrow).
        El escrow ocurre en accept_contract() cuando el vendedor acepta.
        """
        async with self._lock:
            # INV-A2A.5: límite de contratos concurrentes
            active = sum(
                1 for c in self._contracts.values()
                if c.tenant_id == tenant_id
                and c.status in (A2AContractStatus.PROPOSED,
                                  A2AContractStatus.ESCROWED,
                                  A2AContractStatus.ACTIVE)
            )
            if active >= self._config.max_concurrent_contracts:
                raise TooManyConcurrentContracts(
                    tenant_id=tenant_id, limit=self._config.max_concurrent_contracts
                )


            # INV-A2A.6: valor <= max_contract_pct del budget del buyer
            buyer_budget = await self._kernel.get_budget_state(
                tenant_id=tenant_id, session_id=buyer_agent_id
            )
            max_allowed = int(buyer_budget.budget_remaining * self._config.max_contract_pct)
            if budget_tokens > max_allowed:
                raise ContractValueExceedsLimit(
                    requested=budget_tokens,
                    max_allowed=max_allowed,
                    pct=self._config.max_contract_pct,
                )


            # INV-A2A.2: OPA valida la propuesta
            opa_decision = await self._opa.evaluate(
                tenant_id=tenant_id,
                action="a2a_propose_contract",
                context={
                    "buyer_agent_id": buyer_agent_id,
                    "seller_agent_id": seller_agent_id,
                    "budget_tokens": budget_tokens,
                    "buyer_budget_remaining": buyer_budget.budget_remaining,
                    "active_contracts": active,
                },
            )
            if opa_decision.deny:
                import json
                await self._event_bus.publish(
                    tenant_id=tenant_id,
                    event_type="governance.violation",
                    payload_bytes=json.dumps({
                        "session_id": buyer_agent_id,
                        "agent_id": buyer_agent_id,
                        "policy_id": "INV-A2A.2",
                        "action_blocked": "a2a_propose_contract",
                        "reason": opa_decision.reason,
                    }).encode(),
                )
                raise A2APolicyDenied(
                    f"OPA denegó propuesta: buyer={buyer_agent_id} → seller={seller_agent_id}: "
                    f"{opa_decision.reason}"
                )


            contract_id = str(uuid4())
            contract = A2AContract(
                contract_id=contract_id,
                tenant_id=tenant_id,
                buyer_agent_id=buyer_agent_id,
                seller_agent_id=seller_agent_id,
                budget_tokens=budget_tokens,
                service_description=service_description,
                deliverable_spec=deliverable_spec,
                status=A2AContractStatus.PROPOSED,
                proposed_at=datetime.now(timezone.utc),
                expires_at_ts=time.monotonic() + self._config.contract_ttl_seconds,
            )
            self._contracts[contract_id] = contract


        import json
        await self._event_bus.publish(
            tenant_id=tenant_id,
            event_type="a2a.contract.proposed",
            payload_bytes=json.dumps({
                "contract_id": contract_id,
                "buyer_agent_id": buyer_agent_id,
                "seller_agent_id": seller_agent_id,
                "budget_tokens": budget_tokens,
                "service_description": service_description,
            }).encode(),
        )
        logger.info("Contrato PROPOSED: %s buyer=%s seller=%s tokens=%d",
                    contract_id[:8], buyer_agent_id, seller_agent_id, budget_tokens)
        return contract


    # ------------------------------------------------------------------
    # accept_contract — vendedor acepta y se bloquea el escrow
    # ------------------------------------------------------------------


    async def accept_contract(
        self,
        contract_id: str,
        seller_agent_id: str,
    ) -> A2AContract:
        """
        El vendedor acepta el contrato.
        INV-A2A.1: el escrow se bloquea ANTES de que el vendedor empiece la tarea.


        Transición: PROPOSED → ESCROWED → ACTIVE.
        """
        async with self._lock:
            contract = self._get_contract(contract_id)


            if contract.seller_agent_id != seller_agent_id:
                raise A2AUnauthorized(
                    f"seller_agent_id={seller_agent_id} no es el destinatario del contrato {contract_id}"
                )
            if contract.status != A2AContractStatus.PROPOSED:
                raise A2AInvalidTransition(
                    f"Contrato {contract_id} en estado {contract.status} — "
                    f"accept_contract() requiere PROPOSED"
                )
            if time.monotonic() > contract.expires_at_ts:
                await self._expire_contract(contract)
                raise A2AContractExpired(contract_id)


            # INV-A2A.1: escrow — bloquear budget del comprador
            budget_state = await self._kernel.deduct_budget(
                tenant_id=contract.tenant_id,
                session_id=contract.buyer_agent_id,
                tokens=contract.budget_tokens,
                reason=f"A2A_ESCROW:{contract_id}",
            )
            contract = contract.with_status(
                A2AContractStatus.ACTIVE,
                escrowed_at=datetime.now(timezone.utc),
                escrow_session_id=contract.buyer_agent_id,
            )
            self._contracts[contract_id] = contract


        import json
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="a2a.contract.active",
            payload_bytes=json.dumps({
                "contract_id": contract_id,
                "buyer_agent_id": contract.buyer_agent_id,
                "seller_agent_id": seller_agent_id,
                "budget_tokens": contract.budget_tokens,
                "escrowed_at": datetime.now(timezone.utc).isoformat(),
            }).encode(),
        )
        logger.info("Contrato ACTIVE (escrow OK): %s tokens=%d",
                    contract_id[:8], contract.budget_tokens)
        return contract


    # ------------------------------------------------------------------
    # settle_transaction — resolución final del contrato
    # ------------------------------------------------------------------


    async def settle_transaction(
        self,
        contract_id: str,
        buyer_agent_id: str,
        result: A2ASettlement,
    ) -> A2AContract:
        """
        El comprador resuelve el contrato.


        SUCCESS: tokens del escrow transferidos al vendedor.
        DISPUTE: OPA arbitra. Escrow al comprador. Penalización al vendedor.
        CANCELLED: escrow devuelto al comprador sin penalización.


        INV-A2A.4: el vendedor recibe tokens SOLO en SUCCESS.
        """
        async with self._lock:
            contract = self._get_contract(contract_id)


            if contract.buyer_agent_id != buyer_agent_id:
                raise A2AUnauthorized(
                    f"buyer_agent_id={buyer_agent_id} no es el comprador del contrato {contract_id}"
                )
            if contract.status != A2AContractStatus.ACTIVE:
                raise A2AInvalidTransition(
                    f"settle_transaction() requiere estado ACTIVE, actual={contract.status}"
                )


            if result == A2ASettlement.SUCCESS:
                contract = await self._settle_success(contract)
            elif result == A2ASettlement.DISPUTE:
                contract = await self._settle_dispute(contract)
            else:  # CANCELLED
                contract = await self._settle_cancelled(contract)


            self._contracts[contract_id] = contract


        logger.info("Contrato SETTLED: %s result=%s", contract_id[:8], result.value)
        return contract


    async def _settle_success(self, contract: A2AContract) -> A2AContract:
        """SUCCESS: transferir tokens del escrow al vendedor."""
        # Devolver budget al comprador primero (deshace el deduct_budget del escrow)
        await self._kernel.return_budget(
            tenant_id=contract.tenant_id,
            session_id=contract.buyer_agent_id,
            tokens=contract.budget_tokens,
            parent_session_id=None,
        )
        # Deducir del comprador al vendedor (la transferencia real)
        await self._kernel.deduct_budget(
            tenant_id=contract.tenant_id,
            session_id=contract.buyer_agent_id,
            tokens=contract.budget_tokens,
            reason=f"A2A_PAYMENT:{contract.contract_id}",
        )
        import json
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="a2a.contract.settled",
            payload_bytes=json.dumps({
                "contract_id": contract.contract_id,
                "result": "SUCCESS",
                "tokens_transferred": contract.budget_tokens,
                "seller_agent_id": contract.seller_agent_id,
            }).encode(),
        )
        return contract.with_status(
            A2AContractStatus.COMPLETED,
            settled_at=datetime.now(timezone.utc),
        )


    async def _settle_dispute(self, contract: A2AContract) -> A2AContract:
        """
        DISPUTE: OPA arbitra.
        Resolución predeterminada: buyer protection — escrow devuelto al comprador.
        INV-A2A.4: vendedor NO recibe tokens en DISPUTE.
        """
        # Devolver escrow al comprador
        await self._kernel.return_budget(
            tenant_id=contract.tenant_id,
            session_id=contract.buyer_agent_id,
            tokens=contract.budget_tokens,
            parent_session_id=None,
        )
        # Emitir governance.violation para auditoría
        import json
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="governance.violation",
            payload_bytes=json.dumps({
                "session_id": contract.seller_agent_id,
                "agent_id": contract.seller_agent_id,
                "policy_id": "INV-A2A.4",
                "action_blocked": "a2a_dispute",
                "violation_code": "CONTRACT_DISPUTED",
                "violation_detail": (
                    f"Contrato {contract.contract_id} en disputa. "
                    f"Escrow devuelto al comprador {contract.buyer_agent_id}. "
                    f"Penalización de reputación aplicada al vendedor."
                ),
            }).encode(),
        )
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="a2a.contract.disputed",
            payload_bytes=json.dumps({
                "contract_id": contract.contract_id,
                "buyer_agent_id": contract.buyer_agent_id,
                "seller_agent_id": contract.seller_agent_id,
                "escrow_returned_to": contract.buyer_agent_id,
                "tokens": contract.budget_tokens,
            }).encode(),
        )
        return contract.with_status(
            A2AContractStatus.DISPUTED,
            settled_at=datetime.now(timezone.utc),
        )


    async def _settle_cancelled(self, contract: A2AContract) -> A2AContract:
        """CANCELLED: devolver escrow al comprador sin penalización."""
        await self._kernel.return_budget(
            tenant_id=contract.tenant_id,
            session_id=contract.buyer_agent_id,
            tokens=contract.budget_tokens,
            parent_session_id=None,
        )
        import json
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="a2a.contract.cancelled",
            payload_bytes=json.dumps({
                "contract_id": contract.contract_id,
                "escrow_returned_to": contract.buyer_agent_id,
                "tokens": contract.budget_tokens,
            }).encode(),
        )
        return contract.with_status(
            A2AContractStatus.CANCELLED,
            settled_at=datetime.now(timezone.utc),
        )


    # ------------------------------------------------------------------
    # Background expiry loop (INV-A2A.3)
    # ------------------------------------------------------------------


    async def _expiry_loop(self) -> None:
        """
        Loop de background que detecta contratos expirados (INV-A2A.3).
        Se ejecuta cada 30 segundos.
        """
        while True:
            try:
                await asyncio.sleep(30)
                await self._check_expirations()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Expiry loop error: %s", exc)


    async def _check_expirations(self) -> None:
        now = time.monotonic()
        expired = [
            c for c in self._contracts.values()
            if c.status in (A2AContractStatus.PROPOSED, A2AContractStatus.ESCROWED)
            and now > c.expires_at_ts
        ]
        for contract in expired:
            async with self._lock:
                await self._expire_contract(contract)


    async def _expire_contract(self, contract: A2AContract) -> None:
        """Expira un contrato — devuelve escrow si aplica (INV-A2A.3)."""
        if contract.status == A2AContractStatus.ESCROWED:
            await self._kernel.return_budget(
                tenant_id=contract.tenant_id,
                session_id=contract.buyer_agent_id,
                tokens=contract.budget_tokens,
                parent_session_id=None,
            )
        expired = contract.with_status(
            A2AContractStatus.EXPIRED,
            settled_at=datetime.now(timezone.utc),
        )
        self._contracts[contract.contract_id] = expired
        import json
        await self._event_bus.publish(
            tenant_id=contract.tenant_id,
            event_type="a2a.contract.expired",
            payload_bytes=json.dumps({
                "contract_id": contract.contract_id,
                "buyer_agent_id": contract.buyer_agent_id,
                "seller_agent_id": contract.seller_agent_id,
                "escrow_returned": contract.status == A2AContractStatus.ESCROWED,
            }).encode(),
        )
        logger.info("Contrato EXPIRED: %s", contract.contract_id[:8])


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------


    def _get_contract(self, contract_id: str) -> A2AContract:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise A2AContractNotFound(contract_id)
        return contract


    def get_contract(self, contract_id: str) -> A2AContract:
        return self._get_contract(contract_id)


    def list_contracts(
        self,
        tenant_id: str,
        status: Optional[A2AContractStatus] = None,
    ) -> list[A2AContract]:
        return [
            c for c in self._contracts.values()
            if c.tenant_id == tenant_id
            and (status is None or c.status == status)
        ]


    def engine_stats(self, tenant_id: str) -> dict:
        contracts = [c for c in self._contracts.values() if c.tenant_id == tenant_id]
        by_status: dict[str, int] = {}
        for c in contracts:
            by_status[c.status.value] = by_status.get(c.status.value, 0) + 1
        return {
            "tenant_id": tenant_id,
            "total_contracts": len(contracts),
            "by_status": by_status,
            "config": {
                "ttl_seconds": self._config.contract_ttl_seconds,
                "max_concurrent": self._config.max_concurrent_contracts,
                "max_contract_pct": self._config.max_contract_pct,
            },
        }




# ---------------------------------------------------------------------------
# Excepciones
# ---------------------------------------------------------------------------


class A2AError(Exception): pass
class A2AContractNotFound(A2AError): pass
class A2APolicyDenied(A2AError): pass
class A2AUnauthorized(A2AError): pass
class A2AInvalidTransition(A2AError): pass
class A2AContractExpired(A2AError): pass


class TooManyConcurrentContracts(A2AError):
    def __init__(self, tenant_id: str, limit: int):
        super().__init__(
            f"INV-A2A.5: tenant={tenant_id} alcanzó el límite de {limit} contratos concurrentes"
        )


class ContractValueExceedsLimit(A2AError):
    def __init__(self, requested: int, max_allowed: int, pct: float):
        super().__init__(
            f"INV-A2A.6: valor={requested} tokens supera el máximo permitido={max_allowed} "
            f"({int(pct*100)}% del budget)"
        )