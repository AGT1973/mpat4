"""
RES168__audit_schema.py
DESTINO FINAL: observability/audit_schema.py
RES.168 - MPAT4 | Relay: RELAY_014 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field




class AuditEventType(str, Enum):
    # Sesiones
    SESSION_STARTED    = "session.started"
    SESSION_TEARDOWN   = "session.teardown"
    # Governance
    GOVERNANCE         = "governance"
    GOVERNANCE_VIOLATION = "governance.violation"
    # Mesh
    MESH_NODE_JOINED   = "mesh.node.joined"
    MESH_CAUSAL_CONFLICT = "mesh.causal.conflict"
    # A2A Economy
    A2A_CONTRACT_PROPOSED = "a2a.contract.proposed"
    A2A_CONTRACT_ACTIVE   = "a2a.contract.active"
    A2A_CONTRACT_SETTLED  = "a2a.contract.settled"
    A2A_CONTRACT_DISPUTED = "a2a.contract.disputed"
    A2A_CONTRACT_EXPIRED  = "a2a.contract.expired"
    # OS
    OS_PROCESS_SPAWNED    = "cognitive_os.process.spawned"
    OS_PROCESS_TERMINATED = "cognitive_os.process.terminated"
    # Audit propio
    CHAIN_VERIFIED     = "audit.chain.verified"
    CHAIN_CORRUPTED    = "audit.chain.corrupted"
    # Genérico
    TOOL_CALL          = "tool.call"
    LLM_CALL           = "llm.call"
    MEMORY_CONSOLIDATION = "memory.consolidation"




class GovernanceEventType(str, Enum):
    """INV-LEDGER.5: los 6 tipos de eventos de gobernanza."""
    REVIEW_CREATED   = "review.request.created"
    REVIEW_APPROVED  = "review.request.approved"
    REVIEW_REJECTED  = "review.request.rejected"
    REVIEW_MODIFIED  = "review.request.modified"
    REVIEW_EXPIRED   = "review.request.expired"
    REVIEW_CANCELLED = "review.request.cancelled"




class AuditBlock(BaseModel):
    """Representación de un bloque del ledger (para lectura/serialización)."""
    model_config = {"frozen": True}
    block_id: str
    block_index: int
    tenant_id: str
    event_type: str
    payload: dict[str, Any]
    previous_hash: str
    block_hash: str
    recorded_at: str    # ISO8601
    schema_version: str = "v4.0"




class ChainVerificationResult(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    is_valid: bool
    blocks_verified: int
    first_invalid_block: Optional[int] = None
    error_detail: Optional[str] = None
    message: Optional[str] = None
    verified_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    schema_version: str = "v4.0"




class LedgerStats(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    total_blocks: int
    file_size_bytes: int
    first_block_at: Optional[str] = None
    last_block_at: Optional[str] = None
    last_block_hash: str = ""
    schema_version: str = "v4.0"




class LedgerQueryResult(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    event_type: Optional[str] = None
    blocks: list[dict[str, Any]]
    total_returned: int
    schema_version: str = "v4.0"