"""
RES164__cognitive_mesh_schema.py
DESTINO FINAL: schemas/cognitive_mesh_schema.py
RES.164 - MPAT4 | Relay: RELAY_010 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field




class NodeStatus(str, Enum):
    ALIVE     = "ALIVE"
    DEAD      = "DEAD"
    DRAINING  = "DRAINING"




class NodeSpecialization(str, Enum):
    GENERAL   = "general"
    VOICE     = "voice"
    VISION    = "vision"
    CODE      = "code"
    RESEARCH  = "research"




class EventComplexity(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"




class CircuitState(str, Enum):
    CLOSED    = "closed"
    OPEN      = "open"
    HALF_OPEN = "half_open"




class MeshNodeSchema(BaseModel):
    model_config = {"frozen": True}
    node_id: str
    tenant_id: str
    agent_id: str
    endpoint: str
    specialization: NodeSpecialization = NodeSpecialization.GENERAL
    capacity_tokens: int = Field(default=4096, ge=0)
    status: NodeStatus = NodeStatus.ALIVE
    vector_clock: dict[str, int] = Field(default_factory=dict)
    joined_at: datetime
    schema_version: str = "v4.0"




class MeshStatusSchema(BaseModel):
    model_config = {"frozen": True}
    node_id: str
    tenant_id: str
    alive_nodes: int
    nodes: list[MeshNodeSchema]
    vector_clock: dict[str, int]
    bus_stats: dict[str, int]
    schema_version: str = "v4.0"




class RoutingDecisionSchema(BaseModel):
    model_config = {"frozen": True}
    complexity: EventComplexity
    target_backend: str          # "slm_local" | "api_haiku" | "api_sonnet"
    target_node_id: Optional[str]
    target_agent_id: Optional[str]
    estimated_tokens: int
    reason: str
    schema_version: str = "v4.0"




class CausalConflictSchema(BaseModel):
    """Emitido en mesh.causal.conflict (INV-MESH.5)."""
    model_config = {"frozen": True}
    tenant_id: str
    local_vector: dict[str, int]
    remote_vector: dict[str, int]
    resolution: str = "last_write_wins"
    detected_at: datetime
    schema_version: str = "v4.0"




class CircuitBreakerStateSchema(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    node_id: str
    state: CircuitState
    failure_count: int
    threshold: int
    schema_version: str = "v4.0"




class MeshJoinedEventSchema(BaseModel):
    """Payload de mesh.node.joined en EventBusV4."""
    model_config = {"frozen": True}
    node_id: str
    agent_id: str
    specialization: NodeSpecialization
    capacity_tokens: int
    joined_at: str   # ISO8601
    schema_version: str = "v4.0"