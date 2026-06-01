# MPAT4_DEST
# destino: schemas
# nombre: schema_res189.py
# alumno: ariel.garcia.traba@gmail.com

"""
schema_res189.py
RES.189 — Edge AI Federation
Sistema: MPAT4 · Infraestructura Cognitiva Distribuida
Autor: ariel.garcia.traba@gmail.com · 2026-05-31
VOL1 Item 33 · Carpeta destino: providers/edge/

que has usado el formato de razonamiento adaptado por AGT
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, Field, model_validator, field_validator
import uuid
from datetime import datetime


# ---------------------------------------------------------------------------
# Constantes canonicas — INV-RES189
# ---------------------------------------------------------------------------

MIN_NODES_FOR_ROUND: int = 2           # INV-RES189.2
CLOUD_THRESHOLD: float = 0.7           # INV-RES189.4
VALID_QUANTIZATION_BITS: set[int] = {4, 8}  # INV-RES189.1


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class HardwareTarget(str, Enum):
    RASPBERRY_PI = "raspberry_pi"
    JETSON_NANO = "jetson_nano"
    JETSON_ORIN = "jetson_orin"
    SMARTPHONE_ARM = "smartphone_arm"
    LAPTOP_CPU = "laptop_cpu"
    LAPTOP_GPU = "laptop_gpu"


class RoutingDecisionType(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    MESH_PEER = "mesh_peer"


class FederatedRoundStatus(str, Enum):
    WAITING_NODES = "waiting_nodes"
    COLLECTING_GRADIENTS = "collecting_gradients"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# EdgeNode — INV-RES189.6 (frozen, singleton por dispositivo)
# ---------------------------------------------------------------------------

class EdgeNode(BaseModel):
    """
    Nodo fisico de inferencia edge.
    INV-RES189.6: un EdgeNode por dispositivo fisico.
    INV-RES189.1: quantization_bits en {4, 8}.
    """
    model_config = {"frozen": True}

    node_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_name: str
    hardware_target: HardwareTarget
    quantization_bits: Annotated[int, Field(ge=4, le=8)]
    model_path: str
    max_tokens: int = Field(default=512, ge=1)
    tenant_id: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    port: Optional[int] = None

    @field_validator("quantization_bits")
    @classmethod
    def validate_quantization(cls, v: int) -> int:
        # INV-RES189.1
        if v not in VALID_QUANTIZATION_BITS:
            raise ValueError(
                f"INV-RES189.1: quantization_bits debe ser uno de {VALID_QUANTIZATION_BITS}, got {v}"
            )
        return v


# ---------------------------------------------------------------------------
# EdgeQuery y EdgeResult
# ---------------------------------------------------------------------------

class EdgeQuery(BaseModel):
    """Consulta enviada al sistema de federacion edge."""
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = Field(min_length=1)
    tenant_id: str
    complexity_score: Annotated[float, Field(ge=0.0, le=1.0)]
    budget_tokens: int = Field(ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EdgeResult(BaseModel):
    """
    Resultado de inferencia edge.
    Immutable: append-only.
    """
    model_config = {"frozen": True}

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    node_id: str
    routing_type: RoutingDecisionType
    output_text: str
    tokens_used: int = Field(ge=0)
    latency_ms: float = Field(ge=0.0)
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# RoutingDecision — INV-RES189.4
# ---------------------------------------------------------------------------

class RoutingDecision(BaseModel):
    """
    Decision de routing: local, cloud o mesh peer.
    INV-RES189.4: cloud solo si complexity_score > CLOUD_THRESHOLD.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    complexity_score: Annotated[float, Field(ge=0.0, le=1.0)]
    decision: RoutingDecisionType
    target_node_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_cloud_threshold(self) -> "RoutingDecision":
        # INV-RES189.4
        if self.decision == RoutingDecisionType.CLOUD:
            if self.complexity_score <= CLOUD_THRESHOLD:
                raise ValueError(
                    f"INV-RES189.4: routing CLOUD solo si complexity_score > {CLOUD_THRESHOLD}, "
                    f"got {self.complexity_score}"
                )
        return self


# ---------------------------------------------------------------------------
# FederatedRound — INV-RES189.2
# ---------------------------------------------------------------------------

class FederatedRound(BaseModel):
    """
    Ronda de aprendizaje federado.
    INV-RES189.2: requiere minimo MIN_NODES_FOR_ROUND nodos activos.
    """
    round_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participating_node_ids: list[str]
    status: FederatedRoundStatus = FederatedRoundStatus.WAITING_NODES
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_min_nodes(self) -> "FederatedRound":
        # INV-RES189.2
        if len(self.participating_node_ids) < MIN_NODES_FOR_ROUND:
            raise ValueError(
                f"INV-RES189.2: federated_round requiere minimo {MIN_NODES_FOR_ROUND} nodos, "
                f"got {len(self.participating_node_ids)}"
            )
        return self


# ---------------------------------------------------------------------------
# NodeGradient — INV-RES189.3 (privacy-preserving)
# ---------------------------------------------------------------------------

class NodeGradient(BaseModel):
    """
    Gradiente de un nodo para federated learning.
    INV-RES189.3: los gradientes NO contienen datos raw del usuario.
    El campo differential_privacy_applied certifica que se aplico noise.
    """
    gradient_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    round_id: str
    node_id: str
    gradient_data: list[float]  # gradientes post-privacy
    differential_privacy_applied: bool
    epsilon: float = Field(ge=0.0)
    delta: float = Field(ge=0.0)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_privacy(self) -> "NodeGradient":
        # INV-RES189.3
        if not self.differential_privacy_applied:
            raise ValueError(
                "INV-RES189.3: differential_privacy_applied debe ser True — "
                "los gradientes raw no pueden compartirse"
            )
        return self


# ---------------------------------------------------------------------------
# AggregatedModel — resultado de FedAvg
# ---------------------------------------------------------------------------

class AggregatedModel(BaseModel):
    """
    Modelo agregado resultado de una ronda de federated learning.
    Immutable: append-only.
    """
    model_config = {"frozen": True}

    aggregation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    round_id: str
    node_count: int = Field(ge=MIN_NODES_FOR_ROUND)
    model_version: str
    aggregated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# MeshTopology
# ---------------------------------------------------------------------------

class MeshNode(BaseModel):
    node_id: str
    hardware_target: HardwareTarget
    is_online: bool
    latency_to_cloud_ms: Optional[float] = None


class MeshTopology(BaseModel):
    """Topologia actual de la mesh de nodos edge."""
    topology_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nodes: list[MeshNode]
    queried_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def online_count(self) -> int:
        return sum(1 for n in self.nodes if n.is_online)

    @property
    def can_start_federated_round(self) -> bool:
        # INV-RES189.2
        return self.online_count >= MIN_NODES_FOR_ROUND


# ---------------------------------------------------------------------------
# NodeRegistration
# ---------------------------------------------------------------------------

class NodeRegistration(BaseModel):
    """Confirmacion de registro de un nodo en la federation."""
    model_config = {"frozen": True}

    registration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str
    accepted: bool
    rejection_reason: Optional[str] = None
    registered_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# PIPELINE_ORDER — constante de orden canonico (similar a RES.188)
# ---------------------------------------------------------------------------

PIPELINE_ORDER: list[str] = [
    "register_node",
    "infer_local",        # INV-RES189.5: deduct_budget() primero
    "route_task",         # INV-RES189.4: threshold check
    "start_federated_round",  # INV-RES189.2: min nodes check
    "aggregate_gradients",    # INV-RES189.3: privacy check
]
