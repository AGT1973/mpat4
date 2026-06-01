"""
RES167__graph_schema.py
DESTINO FINAL: core/memory_fabric/graph/graph_schema.py
RES.167 - MPAT4 | Relay: RELAY_013 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field




class NodeType(str, Enum):
    ENTITY  = "Entity"   # personas, proyectos, organizaciones
    CONCEPT = "Concept"  # tecnologías, ideas abstractas, términos




class RelationType(str, Enum):
    RELATED_TO   = "RELATED_TO"    # relación genérica
    OWNED_BY     = "OWNED_BY"      # pertenencia
    MENTIONED_IN = "MENTIONED_IN"  # co-aparición en sesión
    CONTRADICTS  = "CONTRADICTS"   # hechos contradictorios (INV-GRAPH.5)




class GraphNode(BaseModel):
    model_config = {"frozen": True}
    node_id: str
    tenant_id: str
    node_type: NodeType
    name: str
    session_id: Optional[str] = None
    embedding_hash: Optional[str] = None  # SHA-256 del embedding vectorial
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    schema_version: str = "v4.0"




class GraphRelation(BaseModel):
    model_config = {"frozen": True}
    relation_id: str
    tenant_id: str
    from_node_id: str
    to_node_id: str
    relation_type: RelationType
    weight: float = Field(default=0.7, ge=0.0, le=1.0)
    session_id: Optional[str] = None
    created_at: datetime
    schema_version: str = "v4.0"




class GraphDelta(BaseModel):
    """Cambios en el grafo desde un timestamp dado."""
    model_config = {"frozen": True}
    tenant_id: str
    since: datetime
    nodes_added: int
    relations_added: int
    node_ids: list[str] = Field(default_factory=list)
    relation_ids: list[str] = Field(default_factory=list)
    schema_version: str = "v4.0"




class ConsolidationResult(BaseModel):
    model_config = {"frozen": True}
    session_id: str
    tenant_id: str
    nodes_created: int = 0
    nodes_total: int = 0
    relations_created: int = 0
    relations_total: int = 0
    already_consolidated: bool = False
    schema_version: str = "v4.0"




class HybridSearchResult(BaseModel):
    model_config = {"frozen": True}
    node_id: str
    name: str
    rrf_score: float   # Reciprocal Rank Fusion score
    sources: list[str] = Field(default_factory=list)  # ["graph", "vector"]
    neighbors: list[str] = Field(default_factory=list)
    schema_version: str = "v4.0"




class GraphQueryRequest(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    cypher: str
    params: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "v4.0"




class HybridSearchRequest(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    prompt: str
    top_k: int = Field(default=10, ge=1, le=100)
    graph_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    schema_version: str = "v4.0"