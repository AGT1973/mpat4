# MPAT4_DEST
# destino: artifacts
# nombre: test_stub_fidelidad_RELAY032.py
# alumno: cursos.agt.ia@gmail.com
# *que has usado el formato de razonamiento adaptado por AGT*

# test_stub_fidelidad_RELAY032.py
# Autor: cursos.agt.ia@gmail.com · 2026-05-31
# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
# Resuelve: DT-STUB-FIDELIDAD-001
# Proposito: verificar que el stub V2 (RELAY032) es fiel al schema canonico Pydantic.
# Tests INTEG-16..INTEG-20 — complementan los 15 tests de RELAY030.
# Resultado: 5/5 PASS
# *que has usado el formato de razonamiento adaptado por AGT*

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from cognition_schema_stub_integ_RELAY032 import (
    ThoughtEntry,
    ThoughtStepType,
    ThoughtTrace,
    ReasoningMode,
    ECSSnapshot,
    CognitionResult,
    CognitionConfig,
)


def test_integ_16_thought_entry_campos_completos():
    """INTEG-16: ThoughtEntry stub V2 tiene entry_id, timestamp, metadata — DT-STUB-FIDELIDAD-001."""
    e = ThoughtEntry(
        agent_id="agent-fidelidad",
        step_type=ThoughtStepType.OBSERVE,
        content="Verificacion de fidelidad de campos.",
        tokens_used=5,
    )
    assert hasattr(e, "entry_id"), "entry_id ausente en ThoughtEntry stub V2"
    parsed = uuid.UUID(e.entry_id)
    assert str(parsed) == e.entry_id, "entry_id no es UUID canonico"
    assert hasattr(e, "timestamp"), "timestamp ausente en ThoughtEntry stub V2"
    assert isinstance(e.timestamp, datetime), "timestamp no es datetime"
    assert e.timestamp.tzinfo is not None, "timestamp debe tener tzinfo (INV-COG-001)"
    assert e.timestamp.tzinfo == timezone.utc, "timestamp debe ser UTC"
    assert hasattr(e, "metadata"), "metadata ausente en ThoughtEntry stub V2"
    assert isinstance(e.metadata, dict), "metadata debe ser dict"
    assert e.metadata == {}, "metadata default debe ser dict vacio"


def test_integ_17_entry_id_unico_por_instancia():
    """INTEG-17: Cada ThoughtEntry tiene entry_id distinto."""
    entries = [
        ThoughtEntry(agent_id="a", step_type=ThoughtStepType.PLAN, content=f"paso {i}")
        for i in range(10)
    ]
    ids = [e.entry_id for e in entries]
    assert len(set(ids)) == 10, f"entry_id no son unicos: {ids}"


def test_integ_18_metadata_payload_arbitrario():
    """INTEG-18: metadata acepta dict[str, Any] arbitrario."""
    payload = {
        "model": "phi4-mini",
        "confidence": 0.95,
        "latency_ms": 42,
        "tags": ["cognition", "mpat4"],
        "nested": {"key": "value"},
    }
    e = ThoughtEntry(
        agent_id="agent-meta",
        step_type=ThoughtStepType.EXECUTE,
        content="Ejecucion con metadata.",
        metadata=payload,
    )
    assert e.metadata["model"] == "phi4-mini"
    assert e.metadata["confidence"] == 0.95
    assert e.metadata["tags"] == ["cognition", "mpat4"]
    assert e.metadata["nested"]["key"] == "value"


def test_integ_19_frozen_campos_nuevos():
    """INTEG-19: entry_id, timestamp, metadata son inmutables (frozen=True)."""
    e = ThoughtEntry(
        agent_id="agent-frozen",
        step_type=ThoughtStepType.EVALUATE,
        content="Test frozen campos nuevos.",
    )
    try:
        e.entry_id = str(uuid.uuid4())
        raise AssertionError("FAIL: entry_id permite mutacion")
    except (AttributeError, TypeError):
        pass
    try:
        e.timestamp = datetime.now(timezone.utc)
        raise AssertionError("FAIL: timestamp permite mutacion")
    except (AttributeError, TypeError):
        pass
    try:
        e.metadata = {"hack": True}
        raise AssertionError("FAIL: metadata permite mutacion de referencia")
    except (AttributeError, TypeError):
        pass


def test_integ_20_compatibilidad_regresion_relay030():
    """INTEG-20: ThoughtEntry V2 preserva compatibilidad con 15 tests RELAY030."""
    e = ThoughtEntry(
        agent_id="agent-integ-001",
        step_type=ThoughtStepType.FINAL,
        content="Respuesta sintetizada por LLM de test.",
        tokens_used=30,
    )
    assert e.agent_id == "agent-integ-001"
    assert e.step_type == ThoughtStepType.FINAL
    assert e.content == "Respuesta sintetizada por LLM de test."
    assert e.tokens_used == 30
    ecs = ECSSnapshot(
        agent_id="agent-integ-001",
        session_id="session-integ-001",
        budget_tokens_total=2000,
        budget_tokens_remaining=2000,
        context_summary="Contexto de prueba",
        history_summary="Sin historial previo.",
        tenant_id="tenant-test",
    )
    assert ecs.budget_tokens_remaining <= ecs.budget_tokens_total


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        test_integ_16_thought_entry_campos_completos,
        test_integ_17_entry_id_unico_por_instancia,
        test_integ_18_metadata_payload_arbitrario,
        test_integ_19_frozen_campos_nuevos,
        test_integ_20_compatibilidad_regresion_relay030,
    ]

    passed = 0
    failed = 0
    errors = []

    print(f"\n{'='*60}")
    print(f"MPAT4 — test_stub_fidelidad_RELAY032 — DT-STUB-FIDELIDAD-001")
    print(f"{'='*60}\n")

    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception:
            print(f"  FAIL  {name}")
            errors.append((name, traceback.format_exc()))
            failed += 1

    print(f"\n{'='*60}")
    print(f"Resultado: {passed} PASS / {failed} FAIL / {passed + failed} TOTAL")
    print(f"{'='*60}\n")

    if errors:
        for name, tb in errors:
            print(f"--- {name} ---")
            print(tb)

    sys.exit(0 if failed == 0 else 1)
