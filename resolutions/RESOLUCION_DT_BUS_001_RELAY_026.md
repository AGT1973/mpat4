# MPAT4_DEST
# destino: resoluciones
# nombre: RESOLUCION_DT_BUS_001_RELAY_026.md
# alumno: ai.mpat.info@gmail.com

# RESOLUCION_DT_BUS_001_RELAY_026.md
## Autor: ai.mpat.info@gmail.com · 2026-05-29
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida · V4_14
## Resuelve: DT-BUS-001
## RELAY: RELAY_026
## que has usado el formato de razonamiento adaptado por AGT

---

## PROBLEMA

`event_schema.py` V4_12 no contenia `RuntimeStartedPayload` ni `RuntimeStoppedPayload`.
Ambas clases existian como `@dataclass` en `runtime_manager_V4_14.py` usando
`json.dumps(asdict(dc)).encode("utf-8")` para serializar.

INV-BUS-008 exige que todos los payloads del bus usen `model_dump_json()` (Pydantic V3).
Sin clases Pydantic V3 en `schemas/`, el bus no podia validar los payloads contra el
schema y RIESGO-025-02 era real: si el bus validara tipos contra `event_schema.py`,
`runtime.started` seria rechazado con INV-BUS-002.

---

## RAZONAMIENTO — DECISION DE DISENO

### Opcion A: agregar las clases en `event_schema_v4.py`
Descartada. `_v4.py` pertenece a otro alumno/relay. Modificarlo desde RELAY_026
viola P1 (modularidad) y crea acoplamiento entre relays. Ademas, `_v4.py` es el
modulo canonico versionado — sus cambios requieren un relay propio.

### Opcion B: crear un nuevo archivo `runtime_payloads.py` en schemas/
Innecesario. `event_schema.py` ya es el punto de entrada canonico y re-exporta
todo el modulo. Agregar un archivo nuevo fragmentaria el contrato publico.

### Opcion C (ELEGIDA — SOTA): definir las clases directamente en `event_schema.py`
Correcto porque:
- `event_schema.py` es el re-exportador canonico — ya es el contrato publico.
- Agrega logica propia SOLO para las clases que no existen en `_v4`.
- No toca `_v4` (P1 respetado).
- No toca `runtime_manager_V4_14.py` — DT-BUS-001 tiene dos fases:
    Fase 1 (esta sesion): clases Pydantic V3 en schemas/ + ALL_EVENT_TYPES
    Fase 2 (proxima): migrar runtime_manager para importar desde schemas.event_schema

---

## SOLUCION IMPLEMENTADA

### Archivo: `schemas/event_schema.py` V4_13

1. `RuntimeStartedPayload(BaseModel)` con `model_config = ConfigDict(frozen=True)`
   Campos exactos del contrato EVENT_BUS_CONTRACT_V4_02.md seccion 4b:
   - runtime_id, tenant_id, runtime_type, started_at, latency_ms, metadata

2. `RuntimeStoppedPayload(BaseModel)` con `model_config = ConfigDict(frozen=True)`
   Campos exactos del contrato seccion 4b:
   - runtime_id, tenant_id, runtime_type, stopped_at, latency_ms, reason, uptime_secs

3. `ALL_EVENT_TYPES` extendido via frozenset union:
   `_ALL_EVENT_TYPES_V4 | frozenset({"runtime.started", "runtime.stopped"})`
   Razon del union: no mutar el frozenset de _v4. INV-ET-006 dice inmutable.
   El alias `_ALL_EVENT_TYPES_V4` es el import con alias para permitir la extension.

4. `__all__` actualizado con `RuntimeStartedPayload` y `RuntimeStoppedPayload`.

---

## INVARIANTES VERIFICADAS

| INV | Descripcion | Estado |
|---|---|---|
| INV-SCHEMA-004 | frozen=True en todos los schemas | CUMPLE — ConfigDict(frozen=True) |
| INV-BUS-008 | serializacion via model_dump_json() | CUMPLE — documentado en docstring |
| INV-BUS-011 | runtime.started/stopped en ALL_EVENT_TYPES | CUMPLE |
| INV-BUS-012 | contrato es fuente canonica | CUMPLE — campos de seccion 4b |
| INV-ET-006 | ALL_EVENT_TYPES es frozenset inmutable | CUMPLE — frozenset union |
| INV-BUS.1 | tenant_id obligatorio | CUMPLE — Field(min_length=1) |
| P1 | modularidad absoluta | CUMPLE — no toca _v4 ni runtime_manager |

---

## DEUDA RESIDUAL ABIERTA DESDE ESTA RESOLUCION

| ID | Descripcion | Prioridad |
|---|---|---|
| DT-BUS-001-F2 | Migrar runtime_manager_V4_14.py para importar RuntimeStartedPayload y RuntimeStoppedPayload desde schemas.event_schema y usar model_dump_json() | ALTA |
| DT-BUS-003 | Verificar si lamport.tick esta en event_schema.py | MEDIA |

---

*RESOLUCION_DT_BUS_001_RELAY_026.md · ai.mpat.info@gmail.com · 2026-05-29 · MPAT4 V4_14*
*que has usado el formato de razonamiento adaptado por AGT*
