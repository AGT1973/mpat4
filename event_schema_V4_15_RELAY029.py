# MPAT4_DEST
# destino: core
# nombre: event_schema.py
# alumno: ai.mpat.info@gmail.com
# relay: RELAY_029
# que has usado el formato de razonamiento adaptado por AGT

# schemas/event_schema.py — Version V4_15
## Resuelve: DT-BUS-002 — KGNodeUpsertedPayload + KGGroundingCompletePayload
## Contrato: EVENT_BUS_CONTRACT_V4_04.md seccion 4d (KG payloads ACTIVO)
## Extiende: V4_14 (ID: 1LX7bAhW5BRA98KL94yDhsWGyh9ZBYhuO)
## Fuente KG payloads: event_bus_schema_V4_02.py (ID: 145LEB4uWjzfIkPq7VmDXSlARGAkPFVsy)
## INV-BUS-011: ALL_EVENT_TYPES fuente canonica — kg.node_upserted y kg.grounding_complete ACTIVOS
## INV-ET-006: frozenset — inmutable por construccion
## INV-KG.3: KGNodeUpsertedPayload emitido via emit_fn inyectada — nunca directo
## INV-KG.5: KGGroundingCompletePayload.nodes_retrieved = len(node_ids_used)
## NOTA ARQUITECTURA: lamport.tick != mesh.clock_tick — NO unificar (herencia RELAY_028)

from __future__ import annotations
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field

from schemas.event_schema_v4 import (  # noqa: F401
    TerminationReason, PolicySeverity, MemoryType, SpanStatus,
    InvalidEventError, BaseEvent,
    ECSCreatedEvent, ECSUpdatedEvent, ECSTerminatedEvent,
    GovernancePolicyViolationEvent, MemoryFabricStoredEvent,
    ObservabilitySpanClosedEvent,
    ALL_EVENT_TYPES as _ALL_EVENT_TYPES_V4,
    deserialize_event,
)

from schemas.event_schema_v4_13 import (  # noqa: F401
    RuntimeStartedPayload, RuntimeStoppedPayload,
    ALL_EVENT_TYPES as _ALL_EVENT_TYPES_V4_13,
)

# DT-BUS-003: LamportTickPayload — Pydantic V3 — INV-SCHEMA-004 (herencia V4_14)
# Emisor: LamportDistributedClock
# ARQUITECTURA: lamport.tick es infraestructura base de sincronizacion causal.
# mesh.clock_tick (RELAY_023) es capa cognitiva. Son distintos. No unificar.
class LamportTickPayload(BaseModel):
    """
    Payload del evento lamport.tick.
    Emitido por LamportDistributedClock.

    Semantica Lamport (logica en dispatcher — INV-BUS-014):
        envio:    tick_local = tick_local + 1
        recepcion: tick_local = max(tick_local, tick_recibido) + 1

    INV-BUS-008: payload.model_dump_json().encode("utf-8")
    INV-SCHEMA-004: frozen=True
    node_id NUNCA igual a tenant_id.
    tick monotonicamente creciente por nodo.
    """
    model_config = ConfigDict(frozen=True)

    node_id: Annotated[str, Field(min_length=1, description="ID del nodo emisor. No restringido a UUID.")]
    tick: Annotated[int, Field(ge=0, description="Valor reloj Lamport post-incremento. Monotonicamente creciente.")]
    tenant_id: Annotated[str, Field(min_length=1, description="Tenant del nodo (INV-BUS.1).")]
    emitted_at: Annotated[str, Field(description="ISO8601 UTC emision del tick.")]
    caused_by_event_id: Annotated[
        Optional[str],
        Field(default=None, description="ID evento que origino este tick. None si tick autonomo.")
    ]


# DT-BUS-002: KG-RAG payloads — V4_15 (RELAY_029) — RES.127
# Fuente canonica: event_bus_schema_V4_02.py seccion KG-RAG
# INV-KG.3: emitido via emit_fn inyectada, nunca directo
class KGNodeUpsertedPayload(BaseModel):
    """
    Payload del evento kg.node_upserted.
    Emitido por KnowledgeGraphIndexer.upsert_node() -- kg_retriever.py.
    INV-KG.3: via emit_fn inyectada, nunca directamente.

    DT-BUS-002 CERRADA / RELAY_029
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    tenant_id: Annotated[str, Field(min_length=1, description="Tenant del nodo (INV-BUS.1).")]
    node_id: Annotated[str, Field(min_length=1, description="ID del nodo upserted en el KG.")]
    label: Annotated[str, Field(min_length=1, description="Etiqueta/tipo del nodo en el grafo.")]


class KGGroundingCompletePayload(BaseModel):
    """
    Payload del evento kg.grounding_complete.
    Emitido por KnowledgeGraphGrounding.ground().
    INV-KG.5: nodes_retrieved = len(node_ids_used).

    DT-BUS-002 CERRADA / RELAY_029
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)

    tenant_id: Annotated[str, Field(min_length=1, description="Tenant que realizo el grounding.")]
    nodes_retrieved: Annotated[int, Field(ge=0, description="Cantidad de nodos recuperados del KG. INV-KG.5.")]
    latency_ms: Annotated[float, Field(ge=0.0, description="Latencia del grounding en milisegundos.")]


# INV-BUS-013 + INV-ET-006: frozenset union — todos ACTIVOS
# V4_15: +kg.node_upserted +kg.grounding_complete (DT-BUS-002 CERRADA)
ALL_EVENT_TYPES: frozenset[str] = _ALL_EVENT_TYPES_V4_13 | frozenset({
    "lamport.tick",          # LamportTickPayload — DT-BUS-003 CERRADA / RELAY_028
    "kg.node_upserted",      # KGNodeUpsertedPayload — DT-BUS-002 CERRADA / RELAY_029
    "kg.grounding_complete", # KGGroundingCompletePayload — DT-BUS-002 CERRADA / RELAY_029
})

# Verificacion: test T-V402-25 requiere exactamente 23+ tipos en ALL_EVENT_TYPES
# V4_13 base: 20 tipos (runtime.started, runtime.stopped, session.*, memory.*, agent.*, ecs.*, bus.*)
# V4_14: +1 (lamport.tick) = 21
# V4_15: +2 (kg.node_upserted, kg.grounding_complete) = 23 — T-V402-25 PASA

__all__ = [
    "TerminationReason", "PolicySeverity", "MemoryType", "SpanStatus",
    "InvalidEventError", "BaseEvent",
    "ECSCreatedEvent", "ECSUpdatedEvent", "ECSTerminatedEvent",
    "GovernancePolicyViolationEvent", "MemoryFabricStoredEvent",
    "ObservabilitySpanClosedEvent",
    "RuntimeStartedPayload", "RuntimeStoppedPayload",
    "LamportTickPayload",           # DT-BUS-003 cerrada RELAY_028
    "KGNodeUpsertedPayload",        # DT-BUS-002 cerrada RELAY_029
    "KGGroundingCompletePayload",   # DT-BUS-002 cerrada RELAY_029
    "ALL_EVENT_TYPES", "deserialize_event",
]
