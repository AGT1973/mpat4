"""
RES166__a2a_schema.py
DESTINO FINAL: ecosystem/a2a_economy/a2a_schema.py
RES.166 - MPAT4 | Relay: RELAY_012 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field




class A2AContractStatus(str, Enum):
    PROPOSED  = "PROPOSED"   # propuesto por el buyer, sin escrow
    ESCROWED  = "ESCROWED"   # aceptado, budget bloqueado (legacy — fusionado con ACTIVE)
    ACTIVE    = "ACTIVE"     # escrow realizado, tarea en curso
    COMPLETED = "COMPLETED"  # tarea completada, tokens transferidos al seller
    DISPUTED  = "DISPUTED"   # en disputa — escrow devuelto al buyer
    CANCELLED = "CANCELLED"  # cancelado — escrow devuelto al buyer sin penalización
    EXPIRED   = "EXPIRED"    # TTL expirado — escrow devuelto al buyer




class A2ASettlement(str, Enum):
    SUCCESS   = "SUCCESS"
    DISPUTE   = "DISPUTE"
    CANCELLED = "CANCELLED"




class A2AContractConfig(BaseModel):
    model_config = {"frozen": True}
    contract_ttl_seconds: int = Field(default=300, ge=30, le=86400,
        description="INV-A2A.3: segundos antes de expirar un contrato sin actividad")
    max_concurrent_contracts: int = Field(default=10, ge=1, le=100,
        description="INV-A2A.5: máximo de contratos concurrentes por tenant")
    max_contract_pct: float = Field(default=0.50, gt=0.0, le=1.0,
        description="INV-A2A.6: máximo del budget total que puede comprometer un contrato")
    schema_version: str = "v4.0"




class A2AContract(BaseModel):
    """
    Contrato A2A inmutable. Cada transición crea una nueva instancia (with_status).
    La inmutabilidad garantiza auditabilidad completa del historial del contrato.
    """
    model_config = {"frozen": True}


    contract_id: str
    tenant_id: str
    buyer_agent_id: str
    seller_agent_id: str
    budget_tokens: int = Field(ge=1)
    service_description: str
    deliverable_spec: str
    status: A2AContractStatus = A2AContractStatus.PROPOSED
    proposed_at: datetime
    expires_at_ts: float          # monotonic timestamp para comparación interna
    escrowed_at: Optional[datetime] = None
    escrow_session_id: Optional[str] = None
    settled_at: Optional[datetime] = None
    dispute_resolution: Optional[str] = None
    schema_version: str = "v4.0"


    def with_status(
        self,
        new_status: A2AContractStatus,
        **kwargs,
    ) -> "A2AContract":
        """Crea una nueva instancia con el nuevo estado. Patrón immutable update."""
        return self.model_copy(update={"status": new_status, **kwargs})




class A2AProposal(BaseModel):
    """Input de propose_contract()."""
    model_config = {"frozen": True}
    tenant_id: str
    buyer_agent_id: str
    seller_agent_id: str
    budget_tokens: int = Field(ge=1)
    service_description: str
    deliverable_spec: str
    schema_version: str = "v4.0"




class A2ADisputeResolution(BaseModel):
    model_config = {"frozen": True}
    contract_id: str
    arbitrator: str = "opa_engine"
    decision: str                        # "buyer_wins" | "seller_wins" | "split"
    escrow_returned_to: str              # agent_id que recibe el escrow
    tokens_returned: int
    reputation_penalty_agent_id: Optional[str] = None
    reason: str
    resolved_at: datetime
    schema_version: str = "v4.0"




# Eventos emitidos en EventBusV4 por A2AEconomyEngine


class A2AContractProposedEvent(BaseModel):
    model_config = {"frozen": True}
    contract_id: str
    buyer_agent_id: str
    seller_agent_id: str
    budget_tokens: int
    service_description: str
    schema_version: str = "v4.0"




class A2AContractActiveEvent(BaseModel):
    model_config = {"frozen": True}
    contract_id: str
    buyer_agent_id: str
    seller_agent_id: str
    budget_tokens: int
    escrowed_at: str
    schema_version: str = "v4.0"




class A2AContractSettledEvent(BaseModel):
    model_config = {"frozen": True}
    contract_id: str
    result: str
    tokens_transferred: Optional[int] = None
    seller_agent_id: Optional[str] = None
    schema_version: str = "v4.0"




class A2AEngineStatsSchema(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    total_contracts: int
    by_status: dict[str, int]
    config: dict
    schema_version: str = "v4.0"