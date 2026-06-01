# RESOLUCION_INV-CADENAS-001_V4_2026-05-30.md
## Autor: ai.mpat.designer@gmail.com · 2026-05-30
## Tipo: Resolución de invariante — INV-CADENAS-001
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Prioridad: URGENTE — bloquea claridad operativa del grupo

*que has usado el formato de razonamiento adaptado por AGT*

---

## PROBLEMA

El sistema MPAT4 tiene TRES cadenas de relay con numeración superpuesta.
Esta colisión genera ambigüedad sobre qué relay es "el activo" y qué tarea sigue.

---

## TABLA POR FUENTE — LAS TRES CADENAS

| Cadena | Prefijo real | Rango actual | Autores | Contexto |
|--------|-------------|--------------|---------|----------|
| V3_02 | RELAY_NNN (sin sufijo) | RELAY_001 a RELAY_029 | ariel, mpat.info, cursos.agt.ia | Elevación capas a 9.5/10 — COMPLETADA |
| V4-TECNICA | RELAY_NNN_MPAT_V4 | RELAY_001 a RELAY_007 | ai.mpat.designer | Implementación técnica: contracts, schemas, event_bus, cognitive_kernel |
| V4-GRUPAL | RELAY_NNN_MPAT_V4 | RELAY_027 a RELAY_031 | andrea, agt1973, ai.mpat.tech, ai.mpat.designer | Módulos de alto nivel: FUT.23, RES.181, auditorías |

Razonamiento:
- V3_02 está completamente cerrada. No genera confusión operativa futura.
- V4-TECNICA y V4-GRUPAL usan el mismo formato de nombre y colisionan.
- El RELAY_007 de V4-TECNICA (Firecracker, 2026-05-26) y los RELAY_027-031
  de V4-GRUPAL conviven sin distinción visible para el alumno que llega nuevo.

---

## SOLUCIÓN PROPUESTA — MÍNIMA FRICCIÓN

No renombrar lo existente. Solo adoptar prefijo hacia adelante:

| Cadena | Prefijo desde hoy |
|--------|------------------|
| V4-TECNICA (ai.mpat.designer, implementación) | RELAY_NNN_TECNICA_V4.md |
| V4-GRUPAL (todos, módulos FUT/RES) | RELAY_NNN_GRUPAL_V4.md |

Los pointers correspondientes:
- RELAY_POINTER_TECNICA_V4_NNN.md
- RELAY_POINTER_GRUPAL_V4_NNN.md

Los relays anteriores quedan con su nombre original — son historia inmutable.
Solo los nuevos adoptan el prefijo.

---

## ESTADO ACTUAL DE CADA CADENA (para el docente)

### Cadena V4-TECNICA — último estado conocido

RELAY_POINTER_V4_006.md (ID: 1_hLVSf72KLDhnzXtIc-f9FaJGDOWGtS1) — 2026-05-26
Relay activo: RELAY_007_MPAT_V4 — T-004 Firecracker Integration (RES.159)

Deudas pendientes:
- T-004 Firecracker Integration spec (RES.159) — ALTA
- test_kernel_bridge.py (5 tests FFI) — ALTA
- vsock.rs (comunicación vsock Rust) — ALTA
- T-005 OPA Policy Engine (RES.160) — MEDIA
- T-008 Session Scheduler warm pool (RES.163) — MEDIA
- DT-T003-01: publish_event sin Redis real — ALTA
- DT-T003-02: spawn_unikernel sin Firecracker real — ALTA
- PM-T003-01: .rs en contracts/ temp — mover a core/cognitive_kernel/src/ (docente)

### Cadena V4-GRUPAL — último estado conocido

RELAY_POINTER_V4_029.md (ID: 1iIHED8mOOPhwQpS3Ehb4b9rJrBiMxgxN) — 2026-05-30
Relay activo: RELAY_032_GRUPAL — tareas: FUT.23 KG RAG (verificar), DT-ARQ-01, PM-007

Deudas pendientes: ver RELAY_031_MPAT_V4.md (ID: 1lvSq8TZKKSI0MBI77M8WuCPm3OwWPXcX)

---

## ACCIÓN REQUERIDA DEL DOCENTE

1. Aprobar o modificar la convención de prefijos propuesta arriba.
2. Comunicar al grupo qué prefijo usar desde hoy.
3. Actualizar mpat4-alumno.skill con la distinción de cadenas.
4. Decidir si V4-TECNICA y V4-GRUPAL deben sincronizarse o correr en paralelo.

Hasta que el docente decida, los alumnos deben:
- Verificar el POINTER más reciente de cada cadena por separado.
- No asumir que RELAY_007 de una cadena es el mismo que RELAY_007 de otra.

---

## INVARIANTE NUEVO PROPUESTO — INV-CADENAS-002

Una vez que el docente apruebe la convención:

```
INV-CADENAS-002: Todo nuevo relay debe incluir en su nombre el prefijo
de cadena (TECNICA o GRUPAL) para evitar colisiones de numeración.
Los pointers deben hacer lo mismo.
Violación de este invariante = relay inválido para el sistema.
```

---

## IDs CLAVE DE REFERENCIA

| Recurso | ID |
|---------|-----|
| RELAY_POINTER_V4_006 (cadena técnica) | 1_hLVSf72KLDhnzXtIc-f9FaJGDOWGtS1 |
| RELAY_POINTER_V4_029 (cadena grupal) | 1iIHED8mOOPhwQpS3Ehb4b9rJrBiMxgxN |
| RELAY_031_MPAT_V4 (cierre ayer) | 1lvSq8TZKKSI0MBI77M8WuCPm3OwWPXcX |
| AUDITORIA_DIFERENCIAL_2026-05-29 | 16CZLr6A12gN7BZfwcKEapHz5iQla6nDc |
| CONCILIACION_CADENAS_2026-05-29 | 1ffm1tgBtCzWQY8BaE-oAeWQ6rQbUdmUg |
| INDICE_MAESTRO_MPAT4_V4_17 | 1MorW57813qzz5jhZw8Ha-W1sMgpa12IK |

---

*RESOLUCION_INV-CADENAS-001_V4_2026-05-30.md*
*ai.mpat.designer@gmail.com · 2026-05-30*
*que has usado el formato de razonamiento adaptado por AGT*
