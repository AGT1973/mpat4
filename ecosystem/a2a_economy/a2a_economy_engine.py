# a2a_economy_engine.py
## Autor: cursos.ai.agt@gmail.com · 2026-05-24
## Módulo: ecosystem/a2a_economy/ · Lenguaje: Python · Versión: V4_13
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## RES: RES.166 — P02 A2A Economy

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from event_bus.mesh_router import build_router_for_tenant, MeshRouterFacade
from schemas.a2a_economy_schema import (
    A2AContractSchema,
    A2AEconomyConfig,
    ContractStatus,
    DisputeReason,
    EscrowRecord,
    SettlementOutcome,
    TransactionRecord,
    create_economy_config,
)

logger = logging.getLogger("mpat4.a2a_economy")


# ---------------------------------------------------------------------------
# INVARIANTES
#
# INV-A2A.1: tenant_id siempre presente — no hay contratos cross-tenant.
# INV-A2A.2: budget_tokens > 0 — no hay contratos gratuitos.
# INV-A2A.3: expiry siempre en el futuro al crear.
# INV-A2A.4: offer_agent_id != accept_agent_id.
# INV-A2A.5: transaction log append-only — nunca modificar.
# INV-A2A.6: escrow se bloquea al aceptar — no al proponer.
# INV-A2A.7: settle() NUNCA lanza excepción — emite governance.violation en error.
# ---------------------------------------------------------------------------


class A2AEconomyEngine:
    """Motor de economía entre agentes autónomos de MPAT4.

    Gestiona el ciclo completo de un contrato A2A:
    propose → accept → escrow → execute → settle (o dispute).

    Analogía educativa:
    Imaginar un mercado de freelancers donde los agentes son los trabajadores.
    - propose_contract(): el cliente publica la oferta
    - accept_contract(): el freelancer la acepta
    - escrow_budget(): el cliente deposita el pago en garantía
    - settle_transaction(): el pago se libera al freelancer al completar
    - dispute_contract(): si el trabajo no se entregó, OPA decide

    La diferencia con un mercado humano: todo es automático, auditable
    y con contratos inteligentes que se ejecutan solos.
    """

    def __init__(
        self,
        tenant_id: str,
        config: A2AEconomyConfig | None = None,
    ) -> None:
        self._tenant_id = tenant_id
        self._config    = config or create_economy_config()
        self._router: MeshRouterFacade = build_router_for_tenant(tenant_id)

        # Almacenamiento en memoria — en producción: persistir en memory_fabric
        self._contracts:    dict[str, A2AContractSchema] = {}
        self._escrows:      dict[str, EscrowRecord]       = {}
        self._transactions: list[TransactionRecord]       = []  # append-only

    # ------------------------------------------------------------------
    # PROPOSE
    # ------------------------------------------------------------------

    async def propose_contract(
        self,
        offer_agent_id: str,
        accept_agent_id: str,
        service_description: str,
        budget_tokens: int,
        ttl_minutes: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> A2AContractSchema:
        """Propone un contrato de servicio entre dos agentes.

        INV-A2A.1: tenant_id tomado del engine.
        INV-A2A.2: budget_tokens validado por el schema.
        INV-A2A.4: offer != accept validado por el schema.
        """
        from datetime import timedelta
        expiry_minutes = ttl_minutes or self._config.default_contract_ttl_minutes

        # Verificar límite de contratos activos por agente
        active_count = sum(
            1 for c in self._contracts.values()
            if c.offer_agent_id == offer_agent_id and c.is_active()
        )
        if active_count >= self._config.max_contracts_per_agent:
            raise RuntimeError(
                f"INV-A2A: agente {offer_agent_id} alcanzó el límite de "
                f"{self._config.max_contracts_per_agent} contratos activos"
            )

        contract = A2AContractSchema(
            tenant_id=self._tenant_id,
            offer_agent_id=offer_agent_id,
            accept_agent_id=accept_agent_id,
            service_description=service_description,
            budget_tokens=budget_tokens,
            expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
            metadata=metadata or {},
        )
        self._contracts[contract.contract_id] = contract

        await self._router.publish(
            "a2a.contract_proposed",
            {
                "contract_id":   contract.contract_id,
                "offer_agent":   offer_agent_id,
                "accept_agent":  accept_agent_id,
                "budget_tokens": budget_tokens,
                "service":       service_description[:100],
                "expiry":        contract.expiry.isoformat(),
            },
            causal=True,
        )
        logger.info(
            "contrato propuesto: id=%s %s→%s tokens=%d",
            contract.contract_id[:8], offer_agent_id[:8],
            accept_agent_id[:8], budget_tokens
        )
        return contract

    # ------------------------------------------------------------------
    # ACCEPT
    # ------------------------------------------------------------------

    async def accept_contract(self, contract_id: str) -> A2AContractSchema:
        """Acepta un contrato propuesto.

        INV-A2A.6: el escrow se bloquea en este paso, no antes.
        """
        contract = self._get_contract(contract_id)
        self._assert_status(contract, ContractStatus.PROPOSED)
        self._assert_not_expired(contract)

        contract.status = ContractStatus.ACCEPTED
        contract.accepted_at = datetime.now(timezone.utc)

        await self._router.publish(
            "a2a.contract_accepted",
            {"contract_id": contract_id, "accepted_at": contract.accepted_at.isoformat()},
            causal=True,
        )
        return contract

    # ------------------------------------------------------------------
    # ESCROW
    # ------------------------------------------------------------------

    async def escrow_budget(self, contract_id: str) -> EscrowRecord:
        """Bloquea el presupuesto en escrow.

        INV-A2A.6: solo se puede escrow un contrato ACCEPTED.
        El presupuesto queda bloqueado hasta settle() o dispute().
        """
        contract = self._get_contract(contract_id)
        self._assert_status(contract, ContractStatus.ACCEPTED)
        self._assert_not_expired(contract)

        escrow = EscrowRecord(
            contract_id=contract_id,
            tenant_id=self._tenant_id,
            amount=contract.budget_tokens,
        )
        self._escrows[contract_id] = escrow
        contract.escrow_locked = True
        contract.status = ContractStatus.ESCROWED

        await self._router.publish(
            "a2a.budget_escrowed",
            {
                "contract_id": contract_id,
                "escrow_id":   escrow.escrow_id,
                "amount":      escrow.amount,
            },
        )
        logger.info("escrow bloqueado: contrato=%s tokens=%d", contract_id[:8], escrow.amount)
        return escrow

    # ------------------------------------------------------------------
    # MARK IN FLIGHT
    # ------------------------------------------------------------------

    async def start_service(self, contract_id: str) -> A2AContractSchema:
        """Marca el contrato como en ejecución (servicio iniciado)."""
        contract = self._get_contract(contract_id)
        self._assert_status(contract, ContractStatus.ESCROWED)
        contract.status = ContractStatus.IN_FLIGHT
        await self._router.publish("a2a.service_started", {"contract_id": contract_id})
        return contract

    # ------------------------------------------------------------------
    # SETTLE
    # ------------------------------------------------------------------

    async def settle_transaction(
        self,
        contract_id: str,
        quality_score: float = 1.0,
    ) -> TransactionRecord:
        """Liquida el contrato y libera el escrow al agente proveedor.

        INV-A2A.7: NUNCA lanza excepción — emite governance.violation en error.
        INV-A2A.5: TransactionRecord es append-only.

        quality_score < config.min_quality_score_for_payment → disputa automática.
        """
        try:
            contract = self._get_contract(contract_id)

            if contract.status not in (ContractStatus.IN_FLIGHT, ContractStatus.ESCROWED):
                raise ValueError(
                    f"settle requiere IN_FLIGHT o ESCROWED, actual: {contract.status}"
                )

            contract.quality_score = max(0.0, min(1.0, quality_score))

            # Calidad insuficiente → disputa automática
            if contract.quality_score < self._config.min_quality_score_for_payment:
                return await self._auto_dispute(
                    contract_id,
                    DisputeReason.QUALITY_BELOW_THRESHOLD,
                )

            # Liquidación normal
            escrow = self._escrows.get(contract_id)
            amount = escrow.amount if escrow else contract.budget_tokens
            outcome = SettlementOutcome.FULL_PAYMENT

            txn = await self._record_transaction(
                contract=contract,
                from_agent_id=contract.accept_agent_id,   # comprador paga
                to_agent_id=contract.offer_agent_id,      # proveedor recibe
                amount=amount,
                outcome=outcome,
            )

            if escrow:
                escrow.released_at = datetime.now(timezone.utc)
                escrow.released_to = contract.offer_agent_id

            contract.status = ContractStatus.COMPLETED
            contract.completed_at = datetime.now(timezone.utc)

            await self._router.publish(
                "a2a.contract_settled",
                {
                    "contract_id":    contract_id,
                    "transaction_id": txn.transaction_id,
                    "outcome":        outcome.value,
                    "amount":         amount,
                    "quality_score":  quality_score,
                },
                causal=True,
            )
            return txn

        except Exception as exc:
            # INV-A2A.7: nunca propagar
            logger.error("settle_transaction error: %s", exc)
            await self._router.publish(
                "governance.violation",
                {
                    "module":      "a2a_economy",
                    "error":       "SETTLE_FAILED",
                    "contract_id": contract_id,
                    "detail":      str(exc),
                },
            )
            # Retornar transacción de error para que el caller sepa qué pasó
            return TransactionRecord(
                contract_id=contract_id,
                tenant_id=self._tenant_id,
                from_agent_id="ERROR",
                to_agent_id="ERROR",
                amount=0,
                outcome=SettlementOutcome.REFUND,
            )

    # ------------------------------------------------------------------
    # DISPUTE
    # ------------------------------------------------------------------

    async def dispute_contract(
        self,
        contract_id: str,
        reason: DisputeReason,
    ) -> A2AContractSchema:
        """Abre una disputa — OPA decide el resultado.

        En V1: disputa resulta en refund automático al comprador.
        En V2+: integrar con governance_engine/opa_engine.py para resolución.
        """
        contract = self._get_contract(contract_id)
        contract.status = ContractStatus.DISPUTED
        contract.dispute_reason = reason

        await self._router.publish(
            "a2a.contract_disputed",
            {
                "contract_id": contract_id,
                "reason":      reason.value,
                "tenant_id":   self._tenant_id,
            },
            causal=True,
        )

        # V1: refund automático
        escrow = self._escrows.get(contract_id)
        if escrow:
            await self._record_transaction(
                contract=contract,
                from_agent_id=contract.offer_agent_id,
                to_agent_id=contract.accept_agent_id,
                amount=escrow.amount,
                outcome=SettlementOutcome.REFUND,
            )
            escrow.released_at = datetime.now(timezone.utc)
            escrow.released_to = contract.accept_agent_id

        contract.settlement_outcome = SettlementOutcome.REFUND
        return contract

    # ------------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------------

    def _get_contract(self, contract_id: str) -> A2AContractSchema:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise KeyError(f"contrato no encontrado: {contract_id}")
        return contract

    def _assert_status(self, contract: A2AContractSchema, expected: ContractStatus) -> None:
        if contract.status != expected:
            raise ValueError(
                f"estado esperado {expected.value}, actual {contract.status.value}"
            )

    def _assert_not_expired(self, contract: A2AContractSchema) -> None:
        if contract.is_expired():
            contract.status = ContractStatus.EXPIRED
            raise ValueError(f"contrato {contract.contract_id[:8]} expirado")

    async def _auto_dispute(
        self,
        contract_id: str,
        reason: DisputeReason,
    ) -> TransactionRecord:
        await self.dispute_contract(contract_id, reason)
        contract = self._contracts[contract_id]
        escrow   = self._escrows.get(contract_id)
        return TransactionRecord(
            contract_id=contract_id,
            tenant_id=self._tenant_id,
            from_agent_id=contract.offer_agent_id,
            to_agent_id=contract.accept_agent_id,
            amount=escrow.amount if escrow else 0,
            outcome=SettlementOutcome.REFUND,
        )

    async def _record_transaction(
        self,
        contract: A2AContractSchema,
        from_agent_id: str,
        to_agent_id: str,
        amount: int,
        outcome: SettlementOutcome,
    ) -> TransactionRecord:
        """Registra una transacción — INV-A2A.5: append-only."""
        txn = TransactionRecord(
            contract_id=contract.contract_id,
            tenant_id=self._tenant_id,
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            amount=amount,
            outcome=outcome,
        )
        # Hash para integración futura con Audit Ledger (RES.168)
        txn.audit_hash = hashlib.sha256(
            json.dumps(txn.model_dump(), default=str).encode()
        ).hexdigest()
        self._transactions.append(txn)  # INV-A2A.5: solo append
        return txn

    # ------------------------------------------------------------------
    # CONSULTAS
    # ------------------------------------------------------------------

    def get_contracts(self, agent_id: str) -> list[A2AContractSchema]:
        return [
            c for c in self._contracts.values()
            if c.offer_agent_id == agent_id or c.accept_agent_id == agent_id
        ]

    def get_transaction_history(self, agent_id: str) -> list[TransactionRecord]:
        return [
            t for t in self._transactions
            if t.from_agent_id == agent_id or t.to_agent_id == agent_id
        ]

    def get_balance(self, agent_id: str) -> int:
        """Calcula el balance neto de un agente (tokens recibidos - pagados)."""
        received = sum(t.amount for t in self._transactions if t.to_agent_id == agent_id)
        paid     = sum(t.amount for t in self._transactions if t.from_agent_id == agent_id)
        return received - paid


# ---------------------------------------------------------------------------
# SINGLETON POR TENANT
# ---------------------------------------------------------------------------

_engines: dict[str, A2AEconomyEngine] = {}


def get_economy_engine(
    tenant_id: str,
    config: A2AEconomyConfig | None = None,
) -> A2AEconomyEngine:
    """Retorna el singleton del A2AEconomyEngine para un tenant."""
    if tenant_id not in _engines:
        _engines[tenant_id] = A2AEconomyEngine(tenant_id, config)
    return _engines[tenant_id]
