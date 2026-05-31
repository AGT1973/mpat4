# a2a_economy_engine.py
## Autor: andrea.bio · 2026-05-25
## Módulo: A2A Economy Engine · Lenguaje: Python · Versión: V4_12
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Contrato: A2A_ECONOMY_CONTRACT_V4_01.md (ID: 1LKEpcZsN-lTWwdT1VP1cwBDp92SJxGtR)
## Schema: schema_a2a_economy.py (ID: 1RWUrI9rgYPVmgEjUPPusSl3U2szfuTdK)
## Carpeta: ecosystem/a2a_economy/
## que has usado el formato de razonamiento adaptado por AGT

"""
A2AEconomyEngine — implementación RES.166.

Gestiona contratos de valor entre agentes autónomos MPAT4.
Integra con AuditLedger (RES.168), EventBusV4 (RES.164), OPA (RES.162).

Invariantes cubiertos:
  INV-A2A.1: transiciones de estado validadas en A2AContract.transition_to()
  INV-A2A.2: AgentCard.status == PUBLISHED verificado antes de crear/aceptar
  INV-A2A.3: escrow deducido ANTES de cambiar status a ACTIVE
  INV-A2A.4: HandoffReceiptV4 siempre incluye audit_hash
  INV-A2A.5: contratos DRAFT con TTL superado → EXPIRED (sin deducción)
  INV-A2A.6: cross_tenant → DisputeArbiterAgent, no OPA local
  INV-A2A.7: settle solo por accept_agent con HDP token válido
  INV-A2A.8: budget via kernel.deduct_budget() / kernel.credit_budget()
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
import uuid
from typing import Protocol, runtime_checkable

from schema_a2a_economy import (
    A2AAuditEventType,
    A2AContract,
    A2AContractAcceptedEvent,
    A2AContractExpiredEvent,
    A2AContractProposedEvent,
    A2AContractSettledEvent,
    A2ADisputeRaisedEvent,
    HandoffReceiptV4,
)

logger = logging.getLogger("mpat4.a2a_economy")


# ---------------------------------------------------------------------------
# Protocolos de dependencias (interfaces esperadas)
# ---------------------------------------------------------------------------

@runtime_checkable
class AuditLedgerProtocol(Protocol):
    async def append(
        self,
        event_type: str,
        payload: dict,
        agent_id: str | None = None,
    ) -> str:
        """Retorna audit_hash del entry creado."""
        ...


@runtime_checkable
class EventBusProtocol(Protocol):
    async def publish(self, event_type: str, payload: dict) -> None: ...


@runtime_checkable
class AgentRegistryProtocol(Protocol):
    async def get_card(self, agent_id: str, tenant_id: str) -> dict | None:
        """Retorna AgentCard como dict o None si no existe."""
        ...


@runtime_checkable
class KernelBudgetProtocol(Protocol):
    async def deduct_budget(self, agent_id: str, amount: float, tenant_id: str) -> bool:
        """Retorna True si hay fondos suficientes y se dedujo. False si no hay fondos."""
        ...

    async def credit_budget(self, agent_id: str, amount: float, tenant_id: str) -> None:
        """Acredita amount al agente."""
        ...


@runtime_checkable
class OPAProtocol(Protocol):
    async def evaluate(self, policy_path: str, context: dict) -> dict: ...


@runtime_checkable
class ContractStoreProtocol(Protocol):
    async def save(self, contract: A2AContract) -> None: ...
    async def get(self, contract_id: str) -> A2AContract | None: ...
    async def list_draft_expired(self) -> list[A2AContract]: ...


# ---------------------------------------------------------------------------
# Excepciones específicas del módulo
# ---------------------------------------------------------------------------

class A2AContractError(Exception):
    """Error base de A2A Economy."""


class A2AInsufficientBudgetError(A2AContractError):
    """INV-A2A.3: presupuesto insuficiente al intentar escrow."""


class A2AAgentNotPublishedError(A2AContractError):
    """INV-A2A.2: AgentCard no tiene status PUBLISHED."""


class A2AInvalidTransitionError(A2AContractError):
    """INV-A2A.1: transición de estado no permitida."""


class A2AHDPTokenError(A2AContractError):
    """INV-4-HO.1 / INV-A2A.7: HDP token inválido o sin scope."""


class A2ACrossTenantDisputeError(A2AContractError):
    """INV-A2A.6: disputa cross-tenant no resuelta por OPA local."""


# ---------------------------------------------------------------------------
# A2AEconomyEngine
# ---------------------------------------------------------------------------

class A2AEconomyEngine:
    """
    Motor de economía A2A para MPAT4.

    Comunicación siempre vía EventBusV4 — NUNCA HTTP directo entre agentes.
    Escrow atómico: si kernel.deduct_budget() falla → contrato no pasa a ACTIVE.
    Audit trail en AuditLedger (RES.168) para cada transición.
    """

    def __init__(
        self,
        ledger: AuditLedgerProtocol,
        event_bus: EventBusProtocol,
        registry: AgentRegistryProtocol,
        kernel: KernelBudgetProtocol,
        opa: OPAProtocol,
        store: ContractStoreProtocol,
    ):
        self._ledger = ledger
        self._bus = event_bus
        self._registry = registry
        self._kernel = kernel
        self._opa = opa
        self._store = store

    # -----------------------------------------------------------------------
    # PASO 1: propose_contract
    # -----------------------------------------------------------------------

    async def propose_contract(
        self,
        offer_agent_id: str,
        accept_agent_id: str,
        budget_tokens: float,
        service_description: str,
        tenant_id: str,
        ttl_seconds: int = 3600,
        service_schema: dict | None = None,
        accept_agent_tenant_id: str | None = None,
    ) -> A2AContract:
        """
        Crea contrato DRAFT y publica evento en EventBusV4.

        INV-A2A.2: verifica offer_agent.status == PUBLISHED.
        INV-A2A.3: NO deduce presupuesto — solo al aceptar.
        INV-A2A.6: detecta cross_tenant si accept_agent pertenece a tenant distinto.
        """
        # INV-A2A.2 — verificar offer_agent
        offer_card = await self._registry.get_card(offer_agent_id, tenant_id)
        if offer_card is None or offer_card.get("status") != "PUBLISHED":
            raise A2AAgentNotPublishedError(
                f"INV-A2A.2: offer_agent {offer_agent_id} no tiene AgentCard PUBLISHED"
            )

        # Detectar cross_tenant
        effective_accept_tenant = accept_agent_tenant_id or tenant_id
        cross_tenant = effective_accept_tenant != tenant_id

        if cross_tenant:
            # Verificar accept_agent en su propio tenant
            accept_card = await self._registry.get_card(
                accept_agent_id, effective_accept_tenant
            )
        else:
            accept_card = await self._registry.get_card(accept_agent_id, tenant_id)

        if accept_card is None or accept_card.get("status") != "PUBLISHED":
            raise A2AAgentNotPublishedError(
                f"INV-A2A.2: accept_agent {accept_agent_id} no tiene AgentCard PUBLISHED"
            )

        # Crear contrato DRAFT
        contract = A2AContract(
            tenant_id=tenant_id,
            offer_agent_id=offer_agent_id,
            accept_agent_id=accept_agent_id,
            budget_tokens=budget_tokens,
            service_description=service_description,
            service_schema=service_schema,
            ttl_seconds=ttl_seconds,
            cross_tenant=cross_tenant,
        )

        # Persistir
        await self._store.save(contract)

        # Audit
        await self._ledger.append(
            event_type="a2a.contract_created",
            payload={
                "contract_id": contract.contract_id,
                "offer_agent_id": offer_agent_id,
                "accept_agent_id": accept_agent_id,
                "budget_tokens": budget_tokens,
                "tenant_id": tenant_id,
                "cross_tenant": cross_tenant,
                "ttl_seconds": ttl_seconds,
            },
            agent_id=offer_agent_id,
        )

        # Publicar en EventBusV4
        event = A2AContractProposedEvent(
            contract_id=contract.contract_id,
            offer_agent_id=offer_agent_id,
            accept_agent_id=accept_agent_id,
            budget_tokens=budget_tokens,
            service_description=service_description,
            ttl_seconds=ttl_seconds,
            tenant_id=tenant_id,
            cross_tenant=cross_tenant,
        )
        await self._bus.publish(event.event_type, event.model_dump())

        logger.info(
            "Contrato DRAFT creado: %s — %s → %s — %.2f tokens",
            contract.contract_id, offer_agent_id, accept_agent_id, budget_tokens
        )
        return contract

    # -----------------------------------------------------------------------
    # PASO 2: accept_contract
    # -----------------------------------------------------------------------

    async def accept_contract(
        self,
        contract_id: str,
        accept_agent_id: str,
        hdp_token,
        tenant_id: str,
    ) -> HandoffReceiptV4:
        """
        Acepta un contrato DRAFT → ACTIVE.

        INV-4-HO.1: verifica HDP token.
        INV-A2A.2: verifica accept_agent PUBLISHED.
        INV-A2A.3: escrow ANTES de cambiar status. Si falla → contrato queda DRAFT.
        INV-A2A.4: HandoffReceiptV4 con audit_hash.
        """
        # Verificar HDP token — INV-4-HO.1
        if not self._verify_hdp_token(hdp_token, "agent.handoff"):
            raise A2AHDPTokenError(
                "INV-4-HO.1: HDP token inválido o sin scope agent.handoff"
            )

        contract = await self._store.get(contract_id)
        if contract is None:
            raise A2AContractError(f"Contrato {contract_id} no encontrado")

        if contract.status != "DRAFT":
            raise A2AInvalidTransitionError(
                f"INV-A2A.1: contrato {contract_id} en status {contract.status} — no se puede aceptar"
            )

        if contract.is_expired():
            # Marcar como expirado y retornar error
            await self._expire_contract(contract)
            raise A2AContractError(
                f"INV-A2A.5: contrato {contract_id} expiró antes de aceptarse"
            )

        if contract.accept_agent_id != accept_agent_id:
            raise A2AContractError(
                f"Agente {accept_agent_id} no es el destinatario del contrato {contract_id}"
            )

        # INV-A2A.3: ESCROW ANTES de cambiar status
        budget_ok = await self._kernel.deduct_budget(
            agent_id=contract.offer_agent_id,
            amount=contract.budget_tokens,
            tenant_id=contract.tenant_id,
        )
        if not budget_ok:
            # Contrato queda en DRAFT — no se activa
            await self._ledger.append(
                event_type="a2a.contract_created",  # re-usa tipo para registrar intento
                payload={
                    "contract_id": contract_id,
                    "event": "escrow_failed",
                    "offer_agent_id": contract.offer_agent_id,
                    "budget_tokens": contract.budget_tokens,
                },
                agent_id=contract.offer_agent_id,
            )
            raise A2AInsufficientBudgetError(
                f"INV-A2A.3: {contract.offer_agent_id} no tiene {contract.budget_tokens} tokens"
            )

        # Audit del escrow
        await self._ledger.append(
            event_type="a2a.budget_deducted",
            payload={
                "contract_id": contract_id,
                "agent_id": contract.offer_agent_id,
                "amount": contract.budget_tokens,
                "tenant_id": contract.tenant_id,
            },
            agent_id=contract.offer_agent_id,
        )

        # Transición de estado
        active_contract = contract.transition_to("ACTIVE")
        await self._store.save(active_contract)

        # Audit de aceptación — obtener hash para HandoffReceipt
        audit_hash = await self._ledger.append(
            event_type="a2a.contract_accepted",
            payload={
                "contract_id": contract_id,
                "accept_agent_id": accept_agent_id,
                "offer_agent_id": contract.offer_agent_id,
                "budget_tokens": contract.budget_tokens,
                "tenant_id": tenant_id,
            },
            agent_id=accept_agent_id,
        )

        # HandoffReceiptV4 con audit_hash — INV-A2A.4
        receipt = HandoffReceiptV4.from_payload(
            from_agent=contract.offer_agent_id,
            to_agent=accept_agent_id,
            tenant_id=tenant_id,
            contract_id=contract_id,
            audit_hash=audit_hash,
            payload={"status": "ACTIVE", "budget_tokens": contract.budget_tokens},
        )

        # Publicar en EventBusV4
        event = A2AContractAcceptedEvent(
            contract_id=contract_id,
            audit_hash=audit_hash,
        )
        await self._bus.publish(event.event_type, event.model_dump())

        logger.info(
            "Contrato ACTIVE: %s — escrow %.2f tokens deducidos de %s",
            contract_id, contract.budget_tokens, contract.offer_agent_id
        )
        return receipt

    # -----------------------------------------------------------------------
    # PASO 3: settle_transaction
    # -----------------------------------------------------------------------

    async def settle_transaction(
        self,
        contract_id: str,
        accept_agent_id: str,
        hdp_token,
        output_payload: dict,
        tenant_id: str,
    ) -> HandoffReceiptV4:
        """
        Liquida un contrato ACTIVE → COMPLETED.

        INV-A2A.7: solo accept_agent con HDP token válido.
        INV-A2A.8: acredita budget_tokens al accept_agent.
        INV-A2A.4: HandoffReceiptV4 con audit_hash.
        """
        # INV-A2A.7 — HDP token y verificar que es el accept_agent
        if not self._verify_hdp_token(hdp_token, "agent.settle"):
            raise A2AHDPTokenError(
                "INV-A2A.7: HDP token inválido o sin scope agent.settle"
            )

        contract = await self._store.get(contract_id)
        if contract is None:
            raise A2AContractError(f"Contrato {contract_id} no encontrado")

        if contract.accept_agent_id != accept_agent_id:
            raise A2AHDPTokenError(
                f"INV-A2A.7: solo {contract.accept_agent_id} puede liquidar este contrato"
            )

        if contract.status != "ACTIVE":
            raise A2AInvalidTransitionError(
                f"INV-A2A.1: contrato {contract_id} en status {contract.status} — no se puede liquidar"
            )

        # INV-A2A.8: acreditar al accept_agent
        await self._kernel.credit_budget(
            agent_id=accept_agent_id,
            amount=contract.budget_tokens,
            tenant_id=tenant_id,
        )

        # Audit de crédito
        await self._ledger.append(
            event_type="a2a.budget_credited",
            payload={
                "contract_id": contract_id,
                "agent_id": accept_agent_id,
                "amount": contract.budget_tokens,
                "tenant_id": tenant_id,
            },
            agent_id=accept_agent_id,
        )

        # Audit de liquidación — obtener hash para HandoffReceipt
        audit_hash = await self._ledger.append(
            event_type="a2a.contract_settled",
            payload={
                "contract_id": contract_id,
                "accept_agent_id": accept_agent_id,
                "offer_agent_id": contract.offer_agent_id,
                "budget_tokens": contract.budget_tokens,
                "output_keys": list(output_payload.keys()),
            },
            agent_id=accept_agent_id,
        )

        # Transición de estado
        completed_contract = contract.transition_to("COMPLETED")
        # Pydantic frozen: rebuild con audit_hash
        completed_contract = completed_contract.model_copy(update={"audit_hash": audit_hash})
        await self._store.save(completed_contract)

        # HandoffReceiptV4 — INV-A2A.4
        receipt = HandoffReceiptV4.from_payload(
            from_agent=accept_agent_id,
            to_agent=contract.offer_agent_id,
            tenant_id=tenant_id,
            contract_id=contract_id,
            audit_hash=audit_hash,
            payload=output_payload,
        )

        # Publicar en EventBusV4
        event = A2AContractSettledEvent(
            contract_id=contract_id,
            audit_hash=audit_hash,
            output_hash=receipt.payload_hash,
        )
        await self._bus.publish(event.event_type, event.model_dump())

        logger.info(
            "Contrato COMPLETED: %s — %.2f tokens acreditados a %s",
            contract_id, contract.budget_tokens, accept_agent_id
        )
        return receipt

    # -----------------------------------------------------------------------
    # PASO 4: raise_dispute
    # -----------------------------------------------------------------------

    async def raise_dispute(
        self,
        contract_id: str,
        raising_agent_id: str,
        reason: str,
        tenant_id: str,
    ) -> str:
        """
        Abre disputa en un contrato ACTIVE → DISPUTED.

        INV-A2A.6: cross_tenant → DisputeArbiterAgent federado (no OPA local).
        Retorna dispute_id.
        """
        contract = await self._store.get(contract_id)
        if contract is None:
            raise A2AContractError(f"Contrato {contract_id} no encontrado")

        if contract.status != "ACTIVE":
            raise A2AInvalidTransitionError(
                f"INV-A2A.1: contrato {contract_id} en {contract.status} — no se puede disputar"
            )

        disputed_contract = contract.transition_to("DISPUTED")
        disputed_contract = disputed_contract.model_copy(
            update={"dispute_reason": reason}
        )
        await self._store.save(disputed_contract)

        dispute_id = str(uuid.uuid4())

        await self._ledger.append(
            event_type="a2a.dispute_raised",
            payload={
                "contract_id": contract_id,
                "dispute_id": dispute_id,
                "raising_agent_id": raising_agent_id,
                "reason": reason,
                "cross_tenant": contract.cross_tenant,
            },
            agent_id=raising_agent_id,
        )

        event = A2ADisputeRaisedEvent(
            contract_id=contract_id,
            raising_agent_id=raising_agent_id,
            reason=reason,
            cross_tenant=contract.cross_tenant,
        )
        await self._bus.publish(event.event_type, event.model_dump())

        if contract.cross_tenant:
            # INV-A2A.6: emitir evento para DisputeArbiterAgent federado
            # (DT-RES166-01: arquitectura del árbitro pendiente de diseño)
            await self._bus.publish(
                "a2a_economy.cross_tenant_dispute",
                {
                    "contract_id": contract_id,
                    "dispute_id": dispute_id,
                    "offer_tenant": contract.tenant_id,
                    "offer_agent": contract.offer_agent_id,
                    "accept_agent": contract.accept_agent_id,
                    "budget_tokens": contract.budget_tokens,
                    "reason": reason,
                },
            )
            logger.warning(
                "Disputa cross-tenant %s — esperando DisputeArbiterAgent (DT-RES166-01)",
                dispute_id
            )
        else:
            # OPA resuelve disputas within-tenant — INV-OPA.2
            opa_context = {
                "contract_id": contract_id,
                "offer_agent_id": contract.offer_agent_id,
                "accept_agent_id": contract.accept_agent_id,
                "raising_agent_id": raising_agent_id,
                "budget_tokens": contract.budget_tokens,
                "reason": reason,
                "tenant_id": tenant_id,
            }
            opa_result = await self._opa.evaluate("governance.a2a_dispute", opa_context)
            logger.info("OPA dispute result para %s: %s", contract_id, opa_result)

        return dispute_id

    # -----------------------------------------------------------------------
    # Tarea periódica: expirar contratos DRAFT con TTL superado
    # -----------------------------------------------------------------------

    async def expire_stale_contracts(self) -> list[str]:
        """
        Marca como EXPIRED contratos DRAFT con TTL superado.

        INV-A2A.5: no deduce presupuesto — el escrow nunca se realizó.
        Debe llamarse periódicamente (scheduler externo o background task).
        """
        stale = await self._store.list_draft_expired()
        expired_ids = []

        for contract in stale:
            if not contract.is_expired():
                continue

            await self._expire_contract(contract)
            expired_ids.append(contract.contract_id)

        if expired_ids:
            logger.info("Contratos expirados: %d", len(expired_ids))

        return expired_ids

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    async def _expire_contract(self, contract: A2AContract) -> None:
        """Transiciona a EXPIRED y registra en audit + EventBus."""
        expired = contract.transition_to("EXPIRED")
        await self._store.save(expired)

        await self._ledger.append(
            event_type="a2a.contract_expired",
            payload={
                "contract_id": contract.contract_id,
                "offer_agent_id": contract.offer_agent_id,
                "ttl_seconds": contract.ttl_seconds,
                "created_at": contract.created_at,
            },
            agent_id=contract.offer_agent_id,
        )

        event = A2AContractExpiredEvent(contract_id=contract.contract_id)
        await self._bus.publish(event.event_type, event.model_dump())

    def _verify_hdp_token(self, hdp_token, required_scope: str) -> bool:
        """
        Verifica HDP token — INV-4-HO.1.
        Delega a la interface del token (contrato de CAPA_12/13).
        Retorna False si el token no tiene el scope requerido.
        """
        if hdp_token is None:
            return False
        try:
            if not hdp_token.verify_chain():
                return False
            if not hdp_token.can_perform(required_scope):
                return False
            return True
        except Exception as exc:
            logger.warning("HDP token verification error: %s", exc)
            return False
