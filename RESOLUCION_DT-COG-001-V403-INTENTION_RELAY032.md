# MPAT4_DEST
# destino: resoluciones
# nombre: RESOLUCION_DT-COG-001-V403-INTENTION_RELAY032.md
# alumno: cursos.agt.ia@gmail.com
# *que has usado el formato de razonamiento adaptado por AGT*

# RESOLUCION_DT-COG-001-V403-INTENTION_RELAY032.md
# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
# Fecha: 2026-05-31 · Relay: 032

---

## Conciliacion de fuentes — DT-COG-001-V403-INTENTION

### Pregunta
El parametro `intention: str` se pasa a `CognitionEngine.reason()` pero NO existe en `ECSSnapshot`.
¿Debe agregarse `intention` a `ECSSnapshot` en V4_04?

### Evidencia por fuente

| Fuente | Valor / Posicion | Evidencia de respaldo | Confianza |
|--------|------------------|-----------------------|-----------|
| cognition_schema.py V4_01 (canonico) | ECSSnapshot SIN intention | Vista minima del ECS. Solo campos que cognition/ necesita del estado persistente. | ALTA |
| ecs_schema.py V4_01 (canonico) | ECSSSchema tiene `intent_normalized: str | None` (Capa 1) | El intent se normaliza en Capa 1 y vive en el ECS completo. | ALTA |
| cognition_engine.py V4_03 (comportamiento) | `intention` como arg de `reason(intention: str)` | Es parametro de invocacion, no estado persistente. | ALTA |
| RELAY_031 (deuda abierta) | DT-COG-001-V403-INTENTION ABIERTA | Sin evidencia a favor de agregar — solo registrada como pendiente. | BAJA |

### Razonamiento

`intention` tiene dos roles conceptualmente distintos:

1. **Como parametro de invocacion** (`reason(ecs, prompt, emit, intention="...")`): le dice al engine qué tipo de tarea resolver, para seleccionar el modelo via ModelRouter. Es efimero — no necesita persistirse en ECSSnapshot porque es parte de la llamada, no del estado cognitivo.

2. **Como estado normalizado** (`ECSSSchema.intent_normalized`): es el output de Capa 1 (normalizacion), persistido en el ECS completo para trazabilidad y critiquing. Este campo ya existe en ecs_schema.py.

Agregar `intention` a `ECSSnapshot` crearía duplicacion semántica con `intent_normalized` y expandiría la vista minima con un campo que cognition/ no necesita para operar (lo tiene como argumento directo).

### Decision

**NO agregar `intention` a `ECSSnapshot`.**

El diseño actual es correcto:
- `intention` llega como argumento de `reason()` → usado por `_resolve_router_cfg()`.
- `intent_normalized` vive en el ECS completo (`ecs_schema.py`), no en la vista minima.
- La vista minima (`ECSSnapshot`) debe permanecer con el minimo necesario.

Fuente canonica: ecs_schema.py V4_01 (ID: 1ClblpieWW79fxHvYskz_NpJZus6ezoLp)

**Estado: RESUELTO — decision: NO CAMBIO — arquitectura correcta**

---

*RESOLUCION_DT-COG-001-V403-INTENTION_RELAY032.md · cursos.agt.ia@gmail.com · 2026-05-31*
*que has usado el formato de razonamiento adaptado por AGT*
