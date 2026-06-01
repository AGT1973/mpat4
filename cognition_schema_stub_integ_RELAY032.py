# MPAT4_DEST
# destino: artifacts
# nombre: cognition_schema_stub_integ_RELAY032.py
# alumno: cursos.agt.ia@gmail.com
# *que has usado el formato de razonamiento adaptado por AGT*

# cognition_schema_stub_integ_RELAY032.py — STUB V2 para tests de integracion
# Autor: cursos.agt.ia@gmail.com · 2026-05-31
# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
# Resuelve: DT-STUB-FIDELIDAD-001
# Cambios vs RELAY030:
#   ThoughtEntry ahora incluye entry_id, timestamp, metadata
#   para fidelidad con cognition_schema.py V4_01 canonico (Pydantic BaseModel).
#   Se mantiene @dataclass (sin dep Pydantic) por ser stub de test.
#   Compatibilidad: 100% — todos los campos nuevos tienen defaults.
#   Los 15 tests RELAY030 no tocan entry_id/timestamp/metadata directamente.
# *que has usado el formato de razonamiento adaptado por AGT*

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# ENUMS — identicos al schema canonico
# ---------------------------------------------------------------------------

class ReasoningMode(str, Enum):
    FULL             = "full"
    DEGRADED         = "degraded"
    BUDGET_EXHAUSTED = "budget_exhausted"


class ThoughtStepType(str, Enum):
    OBSERVE  = "observe"
    PLAN     = "plan"
    EXECUTE  = "execute"
    EVALUATE = "evaluate"
    FINAL    = "final"


# ---------------------------------------------------------------------------
# THOUGHT ENTRY — frozen + campos completos (INV-COG-003)
# DT-STUB-FIDELIDAD-001: agregados entry_id, timestamp, metadata
# Estrategia: @dataclass frozen=True (compatible con object.__setattr__ del engine)
#             sin dependencia Pydantic para mantener tests ligeros
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_entry_id() -> str:
    return str(uuid.uuid4())


@dataclass(frozen=True)
class ThoughtEntry:
    """
    Paso de razonamiento. Frozen e inmutable post-generacion (INV-COG-003).
    V2 RELAY032: fiel al schema canonico Pydantic — incluye entry_id, timestamp, metadata.
    """
    agent_id:     str
    step_type:    ThoughtStepType
    content:      str
    tokens_used:  int                = 0
    # Campos nuevos — fidelidad DT-STUB-FIDELIDAD-001
    entry_id:     str                = field(default_factory=_new_entry_id)
    timestamp:    datetime           = field(default_factory=_utc_now)
    metadata:     dict[str, Any]     = field(default_factory=dict)


# ---------------------------------------------------------------------------
# THOUGHT TRACE — append-only list (INV-COG-002 preservado)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ThoughtTrace:
    agent_id: str
    entries:  list[ThoughtEntry] = field(default_factory=list)

    @property
    def step_count(self) -> int:
        return len(self.entries)

    @property
    def total_tokens(self) -> int:
        return sum(e.tokens_used for e in self.entries)


# ---------------------------------------------------------------------------
# ECS SNAPSHOT — subset minimo que cognition/ necesita
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ECSSnapshot:
    agent_id:                str
    session_id:              str
    budget_tokens_total:     int
    budget_tokens_remaining: int
    context_summary:         str = ""
    history_summary:         str = ""
    tenant_id:               str = ""


# ---------------------------------------------------------------------------
# COGNITION RESULT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CognitionResult:
    agent_id:      str
    mode:          ReasoningMode
    response:      str
    thought_trace: ThoughtTrace
    tokens_used:   int
    warning:       str = ""


# ---------------------------------------------------------------------------
# COGNITION CONFIG
# ---------------------------------------------------------------------------

@dataclass
class CognitionConfig:
    max_reasoning_steps:        int   = 5
    thought_trace_max_entries:  int   = 20
    degraded_mode_enabled:      bool  = True
    degraded_response_template: str   = (
        "Sistema en modo degradado. Consulta procesada: {summary}"
    )
    budget_tokens_warning_pct:  float = 0.2
