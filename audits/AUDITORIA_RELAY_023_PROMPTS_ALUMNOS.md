# MPAT4_DEST
# destino: audits
# nombre: AUDITORIA_RELAY_023_PROMPTS_ALUMNOS.md
# alumno: ai.mpat.info@gmail.com

# AUDITORIA_RELAY_023_PROMPTS_ALUMNOS.md
## Autor: ai.mpat.info@gmail.com · 2026-05-28
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida · Version: V4_14
## Fuente: RELAY_POINTER_V4_023.md + RELAY_POINTER_V4_023_PATCH1.md
## que has usado el formato de razonamiento adaptado por AGT

---

# AUDITORIA TEMA A TEMA — RELAY 23
# Cada seccion es un prompt listo para entregar al alumno responsable

---

## TEMA 01 — DEUDAS TECNICAS

```
PROMPT ALUMNO — DEUDAS TECNICAS RELAY_023

Sos el alumno responsable de resolver deudas tecnicas del sistema MPAT4.
Tu tarea en esta sesion es trabajar sobre las deudas identificadas en RELAY_023.

ESTADO AUDITADO (fuente: RELAY_POINTER_V4_023.md):

| ID             | Descripcion                                              | Prioridad | Estado          |
|----------------|----------------------------------------------------------|-----------|-----------------||
| DT-PERM-001    | Permisos escritura carpetas relay/ y cognition/          | URGENTE   | ABIERTO         |
| PROMPT-002     | teardown_all_sessions en SessionScheduler concreto       | ALTA      | ABIERTO         |
| TAREA_RT_001   | event_bus.publish real en runtime_manager                | ALTA      | ABIERTO         |
| DT-AESP-004    | BudgetWindow persistencia en Memory Fabric               | ALTA      | BLOQUEADO (MF)  |
| DT-COG-004     | cognition_engine.py en carpeta correcta                  | ALTA      | BLOQUEADO PERM  |
| DT-AESP-001    | Mock biometria en tests sin dispositivo                  | MEDIA     | ABIERTO         |
| DT-AESP-002    | Umbral optimo Cognitive Drift                            | MEDIA     | ABIERTO         |
| RIESGO-OBS-001 | event_bus.publish simulado en runtime                    | MEDIA     | ABIERTO         |
| SubsystemName  | AGENT_REGISTRY no existe en schema                       | MEDIA     | ABIERTO         |

RESUELTAS ANTES DE RELAY_023 (no tocar):
- DT-AESP-003 → RESUELTO R023
- DT-COG-005, DT-COG-006 → RESUELTO R022
- DT-COG-007b → RESUELTO R019
- DT-TEST-002 → RESUELTO R020
- DT-AESP-005 → RESUELTO R021

TU TAREA:
1. Leer el RELAY_POINTER_V4_023.md desde Drive (ID: 1ESp9KzXADbfoEvZgN0_kw3grpfpsx8_h)
2. Elegir UNA deuda tecnica ABIERTA que puedas resolver en esta sesion
3. Verificar si existe contrato para esa deuda — si no existe, crearlo primero
4. Verificar si existe schema en schemas/ — si no existe, crearlo antes del codigo
5. Producir el artefacto de resolucion
6. Documentar en RELAY_024 con tabla de conciliacion si hay conflicto de fuentes
7. Subir todo a la Drop Zone (folderId: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI)

PRECONDICION CRITICA:
DT-PERM-001 bloquea DT-COG-004 y la ubicacion correcta de varios archivos.
Si vas a trabajar en DT-PERM-001, coordinar con el docente (ai.mpat.info@gmail.com)
antes de iniciar — requiere permisos sobre carpetas del sistema.

REGLA: NUNCA resolver conflicto entre fuentes por mayoria. Tabla por fuente obligatoria.
```

---

## TEMA 02 — CONTRATOS

```
PROMPT ALUMNO — CONTRATOS RELAY_023

Sos el alumno responsable del estado contractual del sistema MPAT4 al cierre de RELAY_023.

CONTRATOS ACTIVOS AUDITADOS:

| Artefacto                              | ID Drive                          | Carpeta     | Estado |
|----------------------------------------|-----------------------------------|-------------|--------|
| CONTRACT_AESP_V4_01.md                 | 18grNkHdebd2-C82n5cXkRCNSSPVgDmhb | contracts/  | ACTIVO |
| CONTRACT_AESP_SESSION_INTEGRATION_V1.md| 1RBLDUjPeNmP_iBr6fLFomP4qXulI5013| contracts/  | ACTIVO (DT-AESP-003) |
| TAREA_RT_001 contrato                  | 1rhohqyFWKuSn-mZ54TKb97Cbmhm2s8Bf| ---         | EXISTE — sin uso aun |
| TAREA_MESH_001 contrato                | 1efyf_bMvdZHHd_gWM8aO1Czd4jsny-6U| ---         | EXISTE — sin uso aun |

CONTRATOS FALTANTES DETECTADOS:
- No hay contrato para TAREA_RT_001 en uso activo (runtime_manager event_bus.publish real)
- No hay contrato para SubsystemName.AGENT_REGISTRY
- No hay contrato para DT-AESP-004 (BudgetWindow persistencia)

TU TAREA:
1. Leer CONTRACT_AESP_SESSION_INTEGRATION_V1.md (ID: 1RBLDUjPeNmP_iBr6fLFomP4qXulI5013)
2. Auditar si el contrato cubre los invariantes INV-FREEZE-001..005
3. Si faltan INV en el contrato: producir CONTRACT_AESP_SESSION_INTEGRATION_V2.md
4. Para SubsystemName.AGENT_REGISTRY: producir CONTRACT_AGENT_REGISTRY_V1.md
5. Subir a Drop Zone con destino: contracts

FORMATO OBLIGATORIO DEL CONTRATO (10 secciones):
1. Identificacion del modulo
2. Dependencias declaradas
3. Invariantes (INV-XXX-NNN)
4. Pre/Post condiciones
5. Interfaz publica
6. Comportamiento en fallo
7. Tests requeridos
8. Esquema de datos (referencia a schemas/)
9. Historial de versiones
10. Deuda tecnica conocida

REGLA: NUNCA codigo sin contrato aprobado.
REGLA: NUNCA schema en la carpeta del modulo — siempre en schemas/
```

---

## TEMA 03 — CIERRES

```
PROMPT ALUMNO — CIERRES RELAY_023

Sos el alumno responsable de auditar el estado de cierre del RELAY_023.

AUDITORIA DE CIERRE:
El RELAY_023 fue cerrado por: ai.mpat.info@gmail.com el 2026-05-27

ARTEFACTOS DE CIERRE PRODUCIDOS:
- RELAY_023_V4.md (ID: 1L5Qje7LflSL-mMBAJ4P1meOhw9P9W7CL) — 580 bytes
  PROBLEMA: guardado en contracts/ provisional — NO esta en relay/active/
- RELAY_POINTER_V4_023.md (ID: 1ESp9KzXADbfoEvZgN0_kw3grpfpsx8_h) — 7194 bytes
- RELAY_POINTER_V4_023_PATCH1.md (ID: 1exeKoupQKkH-SsQ_w-vCtqeWvMNuli-J) — 2305 bytes

PROBLEMA CRITICO:
RELAY_023_V4.md tiene solo 580 bytes — las 10 secciones NO estan presentes.
Es un resumen, no un relay completo. DEUDA TECNICA DE DOCUMENTACION.

TU TAREA:
1. Leer RELAY_023_V4.md (ID: 1L5Qje7LflSL-mMBAJ4P1meOhw9P9W7CL)
2. Leer RELAY_POINTER_V4_023_PATCH1.md (ID: 1exeKoupQKkH-SsQ_w-vCtqeWvMNuli-J)
3. Producir RELAY_023_COMPLETO_V4.md con las 10 secciones reales reconstruidas
4. Subir a Drop Zone con destino: relay_active

SECCIONES OBLIGATORIAS (10):
1. IDENTIFICACION · 2. ESTADO AL INICIO · 3. TRABAJO REALIZADO
4. INVARIANTES · 5. CONCILIACIONES · 6. CONCILIACIONES PEND.
7. ARTEFACTOS GENERADOS · 8. ESTADO AL CIERRE
9. PROXIMO PASO · 10. DEUDA TECNICA

REGLA: Seccion vacia = relay invalido.
```

---

## TEMA 04 — CAPAS

```
PROMPT ALUMNO — CAPAS ARQUITECTONICAS RELAY_023

CAPAS IDENTIFICADAS:

CAPA 1 — SCHEMA (schemas/)
  aesp_schema.py — EN RAIZ (bloqueado DT-PERM-001)
  TEMPORAL_cognition_schema_v2.py — ubicacion sin confirmar
  observability_schema.py — ubicacion sin confirmar

CAPA 2 — ENGINE (cognition/)
  cognition_engine_V4_03.py — EN RAIZ (bloqueado DT-PERM-001)

CAPA 3 — ECOSYSTEM (ecosystem/)
  aesp_engine.py — EN RAIZ (bloqueado DT-PERM-001)

CAPA 4 — RUNTIME
  runtime_manager — SIN IMPLEMENTACION REAL (TAREA_RT_001)

CAPA 5 — AGENT_REGISTRY (agent_registry/)
  SubsystemName.AGENT_REGISTRY — NO existe en schema

INVARIANTE: INV-OBS-001 — NUNCA importar directamente de otro modulo — solo via emit()

TU TAREA:
1. Leer cognition_engine_V4_03.py (ID: 1rr1an_br0tYOSC2PfWKFNnKwW2f33H93)
2. Verificar que no tiene imports directos de aesp_engine o agent_registry
3. Leer aesp_engine.py (ID: 12WUkUwqF2eECTx0OG-3zfPjy2ubF6si0)
4. Verificar comunicacion solo via emit()
5. Producir REPORTE_CAPAS_RELAY_023.md con hallazgos y violaciones marcadas [VIOLATION]
6. Subir a Drop Zone con destino: audits
```

---

## TEMA 05 — RESOLUCIONES

```
PROMPT ALUMNO — RESOLUCIONES RELAY_023

RESOLUCIONES PRODUCIDAS EN RELAY_023:

RIESGO-SKILL-001 — CONCILIADO R023
  skill apuntaba a V4_12 en lugar de V4_14
  PENDIENTE: confirmacion docente (ai.mpat.info@gmail.com)
  SKILL_V4_14: 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6
  SKILL_V4_12: 1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD (BACKUP)

DT-AESP-003 — RESUELTO R023 (DOS implementaciones — decision pendiente)
  session_scheduler_DT_AESP_003.py (andrea) ID: 1U7Vzc91CFbWo5UcOU1dG3R0VvT25cFWQ
  TEMPORAL_session_scheduler_freeze_handler.py (claudeacc1011) ID: 1TTj-ajHfqKR5lEfYYv-2QahreG0PHN4D
  TEMPORAL_aesp_freeze_session_bridge.py (ariel) ID: 1QzlGUpupSvLnPKVS5mzWwWYJW_OzXNLE

TU TAREA:
1. Leer ambas implementaciones de session_scheduler
2. Construir tabla de conciliacion:
   | Campo        | andrea (callback) | claudeacc1011 (FreezeAwareMixin) | Confianza |
   |--------------|-------------------|----------------------------------|-----------|
   | patron       | ...               | ...                              | ...       |
   | acoplamiento | ...               | ...                              | ...       |
   | testabilidad | ...               | ...                              | ...       |
3. Razonar explicitamente — NO votar
4. Producir RESOLUCION_DT_AESP_003_CANONICA.md
5. Subir a Drop Zone con destino: resoluciones

REGLA: Sin respuesta del docente → marcar PENDIENTE_INV
```

---

## TEMA 06 — ARQUITECTURA

```
PROMPT ALUMNO — ARQUITECTURA RELAY_023

MODULOS Y ESTADO:

| Modulo           | Carpeta correcta | Estado actual       | Bloqueado por  |
|------------------|------------------|---------------------|----------------|
| cognition_engine | cognition/       | EN RAIZ             | DT-PERM-001    |
| aesp_engine      | ecosystem/       | EN RAIZ             | DT-PERM-001    |
| aesp_schema      | schemas/         | EN RAIZ             | DT-PERM-001    |
| session_scheduler| core/ o aesp/    | PENDIENTE decision  | docente        |
| agent_registry   | agent_registry/  | carpeta OK          | schema falta   |
| runtime_manager  | runtime/         | sin implementacion  | TAREA_RT_001   |

DECISION ARQUITECTONICA CRITICA PENDIENTE:
patron callback (andrea) vs FreezeAwareMixin via EventBus (claudeacc1011)
Impacta acoplamiento AESP ↔ sessiones. Resolver antes de RELAY_024.

TU TAREA:
1. Verificar INV-OBS-001 en cognition_engine_V4_03.py y aesp_engine.py
2. Documentar grafo de dependencias en DIAGRAMA_ARQUITECTURA_R023.md
3. Marcar [VIOLATION] cualquier import directo entre modulos
4. Subir a Drop Zone con destino: docs

NUNCA Docker. NUNCA subprocess Python→Rust.
```

---

## TEMA 07 — ARTEFACTOS

```
PROMPT ALUMNO — ARTEFACTOS RELAY_023

TRACK A — cognition/:
  TEMPORAL_cognition_schema_v2.py     ID: 1WW4lDj8QgKMKJ1EZpSMFOO3qPwG0Hy1E  ACTIVO
  TEMPORAL_cognition_engine_v2_DT007b.py  ID: PENDIENTE (alumno 019)
  TEMPORAL_cognition_engine_v2_V4_14_final.py  ID: PENDIENTE (alumno 022)
  test_cognition_engine_v2_DT_TEST_002.py  ID: 1bwPLvQMUvu6xom0gXLvwM4QmRj_aZq14  OK

TRACK B — AESP:
  cognition_engine_V4_03.py           ID: 1rr1an_br0tYOSC2PfWKFNnKwW2f33H93  ACTIVO
  CONTRACT_AESP_V4_01.md              ID: 18grNkHdebd2-C82n5cXkRCNSSPVgDmhb   ACTIVO
  aesp_engine.py                      ID: 12WUkUwqF2eECTx0OG-3zfPjy2ubF6si0   ACTIVO
  aesp_schema.py                      ID: 1V-P2wMaAELGtozG8cB4fO6rc6MZG0CR7   ACTIVO
  test_aesp_event_bus_DT_AESP_005.py  ID: 12Fvd6DrtKg_V8Q2cBuOgXj85H3hNFida  OK
  CONTRACT_AESP_SESSION_INTEGRATION_V1.md  ID: 1RBLDUjPeNmP_iBr6fLFomP4qXulI5013  ACTIVO
  session_scheduler_freeze_handler.py  ID: PENDIENTE (404 en R023)

NUEVOS EN PATCH1:
  session_scheduler_DT_AESP_003.py    ID: 1U7Vzc91CFbWo5UcOU1dG3R0VvT25cFWQ  andrea
  test_session_scheduler_DT_AESP_003.py  ID: 1uEwJHMAPfC9PDqV6Y6p9FDOrHtyG4T1n  andrea
  TEMPORAL_session_scheduler_freeze_handler.py  ID: 1TTj-ajHfqKR5lEfYYv-2QahreG0PHN4D  claudeacc1011
  TEMPORAL_test_session_scheduler_freeze.py  ID: 1OtmQDzGbrHecweBgsTxh-YEKqMqRTzmk  claudeacc1011
  TEMPORAL_aesp_freeze_session_bridge.py  ID: 1QzlGUpupSvLnPKVS5mzWwWYJW_OzXNLE  ariel

TU TAREA:
1. Buscar en Drive los artefactos con ID PENDIENTE (alumno 019, alumno 022)
2. Verificar que session_scheduler_freeze_handler.py (404) tiene reemplazo funcional
3. Producir INVENTARIO_ARTEFACTOS_R023_AUDITADO.md con IDs verificados
4. Marcar HUERFANO todo artefacto sin ID confirmado
5. Subir a Drop Zone con destino: audits
```

---

## TEMA 08 — SCRIPTS PYTHON

```
PROMPT ALUMNO — SCRIPTS PYTHON RELAY_023

SCRIPTS DE PRODUCCION:
  cognition_engine_V4_03.py        ID: 1rr1an_br0tYOSC2PfWKFNnKwW2f33H93
  aesp_engine.py                   ID: 12WUkUwqF2eECTx0OG-3zfPjy2ubF6si0

SCHEMAS PYDANTIC V3:
  TEMPORAL_cognition_schema_v2.py  ID: 1WW4lDj8QgKMKJ1EZpSMFOO3qPwG0Hy1E
  aesp_schema.py                   ID: 1V-P2wMaAELGtozG8cB4fO6rc6MZG0CR7
  observability_schema.py          ID: 1OE4KNTI2Vf5fVZrdJB-Pb2CPN1qj0h7T

SCRIPTS DT-AESP-003 (decision canonica pendiente):
  session_scheduler_DT_AESP_003.py  ID: 1U7Vzc91CFbWo5UcOU1dG3R0VvT25cFWQ
  TEMPORAL_session_scheduler_freeze_handler.py  ID: 1TTj-ajHfqKR5lEfYYv-2QahreG0PHN4D
  TEMPORAL_aesp_freeze_session_bridge.py  ID: 1QzlGUpupSvLnPKVS5mzWwWYJW_OzXNLE

IDs SIN CONFIRMAR:
  TEMPORAL_cognition_engine_v2_DT007b.py — pendiente alumno 019
  TEMPORAL_cognition_engine_v2_V4_14_final.py — pendiente alumno 022

TU TAREA DE AUDITORIA:
Para cognition_engine_V4_03.py y aesp_engine.py verificar:
  a. Imports — cumple INV-OBS-001?
  b. Version Pydantic (debe ser V3)
  c. Encabezado MPAT4 obligatorio
  d. Implementa DEC-053, DEC-059, DEC-060

Para session_scheduler_DT_AESP_003.py verificar:
  a. teardown_all_sessions implementado correctamente
  b. INV-FREEZE-001..005 documentados como comentarios

Producir AUDITORIA_SCRIPTS_PYTHON_R023.md
Subir a Drop Zone con destino: audits

INVARIANTES A VERIFICAR:
- INV-OBS-002: health_check() NUNCA lanza excepcion hacia arriba
- INV-OBS-003: timestamp SIEMPRE con tzinfo=timezone.utc
- INV-COG-011: reasoning_strategy en ThoughtEntry — default DIRECT
- NUNCA subprocess para Python→Rust
```

---

## TEMA 09 — SCRIPTS RUST

```
PROMPT ALUMNO — SCRIPTS RUST RELAY_023

ESTADO AL CIERRE DE RELAY_023:
  No hay artefactos Rust confirmados con ID en Drive.
  La regla NUNCA subprocess para Python→Rust existe en invariantes.
  El bridge FFI no fue implementado en ciclos 001-023.
  No hay DT-RUST-NNN abierto en el sistema.
  RES.170 (MCP 2.0) es research activa pero no cubre Rust FFI.

TU TAREA:
1. Buscar en Drive: title contains 'rust' or title contains 'ffi'
2. Si encontras artefactos no registrados: documentarlos
3. Si no encontras nada: verificar que la regla esta en algun contrato activo
4. Si no hay tarea abierta para FFI bridge: abrir DT-RUST-001
5. Producir ESTADO_RUST_R023.md
6. Subir a Drop Zone con destino: audits

CRITERIOS DE UN BRIDGE FFI CORRECTO EN MPAT4:
- NUNCA subprocess
- CONTRACT_RUST_BRIDGE_V1.md — debe existir antes del codigo
- Schema Pydantic del lado Python en schemas/
- Tipos serializables via JSON o binario definido en contrato
- health_check() que nunca lanza excepcion hacia arriba

NOTA: Documentar la ausencia es tan importante como documentar la presencia.
```

---

## TEMA 10 — AUDITORIAS

```
PROMPT ALUMNO — AUDITORIAS PREVIAS Y ESTADO RELAY_023

AUDITORIAS REFERENCIADAS:

AUDITORIA_IDS_RELAY_019_022_V2.md
  Brecha reportada: cerrada segun PATCH1 por registro de
  TEMPORAL_aesp_freeze_session_bridge.py (ID: 1QzlGUpupSvLnPKVS5mzWwWYJW_OzXNLE)
  Pendiente: verificacion en Drive

AUDITORIAS FORMALES FALTANTES:
  - No hay AUDITORIA_R023.md formal
  - No hay AUDITORIA_CAPAS.md
  - No hay AUDITORIA_CONTRATOS.md

TU TAREA:
1. Buscar AUDITORIA_IDS_RELAY_019_022_V2.md en Drive
2. Verificar que TEMPORAL_aesp_freeze_session_bridge.py existe con ese ID
3. Producir AUDITORIA_R023_FORMAL.md con:
   - Artefactos auditados
   - Estado de cada ID en Drive (EXISTE / 404 / NO VERIFICADO)
   - Brechas encontradas / cerradas / pendientes
4. Subir a Drop Zone con destino: audits

FORMATO:
| Artefacto | ID declarado | Estado Drive | Verificado por | Fecha |
|-----------|--------------|--------------|----------------|-------|

REGLA: Auditoria sin verificar IDs en Drive = lectura del relay, no auditoria.
```

---

## TEMA 11 — PENDIENTES

```
PROMPT ALUMNO — PENDIENTES RELAY_023

URGENTE (bloquea otras tareas):
  DT-PERM-001 — Permisos relay/ y cognition/ — Responsable: docente

ALTA — ABIERTOS:
  PROMPT-002 — teardown_all_sessions (precond: R023 OK)
  TAREA_RT_001 — event_bus.publish real en runtime_manager
  RIESGO-SKILL-001 — confirmacion docente pendiente

ALTA — BLOQUEADOS:
  DT-AESP-004 — BudgetWindow (bloqueado: Memory Fabric no disponible)
  DT-COG-004 — cognition_engine.py en carpeta (bloqueado: DT-PERM-001)

DECISION DOCENTE PENDIENTE (critica):
  DT-AESP-003 canonical:
    Opcion A: session_scheduler_DT_AESP_003.py (andrea — callback directo)
    Opcion B: TEMPORAL_session_scheduler_freeze_handler.py (claudeacc1011 — FreezeAwareMixin)

IDs SIN CONFIRMAR:
  TEMPORAL_cognition_engine_v2_DT007b.py — alumno 019
  TEMPORAL_cognition_engine_v2_V4_14_final.py — alumno 022
  session_scheduler_freeze_handler.py — 404 en R023

MEDIA — ABIERTOS:
  DT-AESP-001 / DT-AESP-002 / RIESGO-OBS-001 / SubsystemName.AGENT_REGISTRY

TU TAREA:
1. Ordenar pendientes por impacto tecnico (razonar, no copiar prioridad declarada)
2. Identificar cuales puedes resolver solo vs cuales necesitan coordinacion
3. Tomar UNO y documentar en RELAY_024
4. Para los que no tomas: nota en seccion 10 del relay

TRAMPA EDUCATIVA:
"Resolver PROMPT-002 es simple — solo implementar teardown_all_sessions"
INCORRECTO. Antes de implementar:
- Leer CONTRACT_AESP_SESSION_INTEGRATION_V1.md
- Verificar cual session_scheduler es canonico
- El teardown debe respetar INV-FREEZE-001..005, no solo funcionar
```

---

## TEMA 12 — SCHEMAS

```
PROMPT ALUMNO — SCHEMAS RELAY_023

SCHEMAS IDENTIFICADOS:

| Schema                          | ID Drive                          | Ubicacion actual | Destino    |
|---------------------------------|-----------------------------------|------------------|------------|
| TEMPORAL_cognition_schema_v2.py | 1WW4lDj8QgKMKJ1EZpSMFOO3qPwG0Hy1E| sin confirmar    | schemas/   |
| aesp_schema.py                  | 1V-P2wMaAELGtozG8cB4fO6rc6MZG0CR7| raiz (probable)  | schemas/   |
| observability_schema.py         | 1OE4KNTI2Vf5fVZrdJB-Pb2CPN1qj0h7T| sin confirmar    | schemas/   |

FALTANTES:
  - Schema para SubsystemName.AGENT_REGISTRY
  - Schema para BudgetWindow (DT-AESP-004)
  - Schema para session_scheduler canonico — pendiente decision

ID carpeta schemas/: 1N_u01JXjeMlMkNbk7GvV6gnQTtnpOipG
REGLA: NUNCA schema en carpeta del modulo — SIEMPRE en schemas/

TU TAREA:
1. Leer TEMPORAL_cognition_schema_v2.py — verificar:
   a. Pydantic V3 (model_config, no Config class)
   b. ReasoningStrategy definida aqui (DEC-053)
   c. ThoughtEntry con reasoning_strategy default DIRECT (INV-COG-011)
   d. Timestamps con tzinfo=timezone.utc (INV-OBS-003)
2. Leer aesp_schema.py — verificar tipos para EmergencyFreeze y SessionScheduler
3. Producir AUDITORIA_SCHEMAS_R023.md con hallazgos y gaps
4. Si schema no usa Pydantic V3: abrir deuda tecnica nueva
5. Subir a Drop Zone con destino: audits

PYDANTIC V3 CORRECTO:   model_config = ConfigDict(arbitrary_types_allowed=True)
PYDANTIC V1/V2 MALO:    class Config: arbitrary_types_allowed = True
```

---

## TEMA 13 — TEST

```
PROMPT ALUMNO — TESTS RELAY_023

TESTS CON IDs CONFIRMADOS:

| Test                                     | ID Drive                          | Cobertura          |
|------------------------------------------|-----------------------------------|--------------------|
| test_cognition_engine_v2_DT_TEST_002.py  | 1bwPLvQMUvu6xom0gXLvwM4QmRj_aZq14| 19 tests (R018)    |
| test_aesp_event_bus_DT_AESP_005.py       | 12Fvd6DrtKg_V8Q2cBuOgXj85H3hNFida| 18 tests           |
| test_session_scheduler_DT_AESP_003.py    | 1uEwJHMAPfC9PDqV6Y6p9FDOrHtyG4T1n| DT-AESP-003 andrea |
| TEMPORAL_test_session_scheduler_freeze.py| 1OtmQDzGbrHecweBgsTxh-YEKqMqRTzmk| DT-AESP-003 cc1011 |

GAPS DETECTADOS:
  - Sin test directo para cognition_engine_V4_03.py
  - Sin test directo para aesp_engine.py
  - Sin test para observability_schema.py
  - Sin test de integracion EmergencyFreeze→teardown completo
  - DT-AESP-001: Mock biometria sin dispositivo — ABIERTO

TU TAREA:
1. Leer test_cognition_engine_v2_DT_TEST_002.py — verificar:
   a. Cubre CoT y ToT
   b. Verifica DEC-059 (emit() best-effort)
   c. Verifica DEC-060 (strategy_override prioridad)
   d. Verifica INV-OBS-002 y INV-OBS-003
2. Identificar cual suite cubre INV-FREEZE-001..005
   Si no existe: abrir DT-TEST-003
3. Producir AUDITORIA_TESTS_R023.md (cobertura real vs declarada, gaps)
4. Subir a Drop Zone con destino: audits

TRAMPA EDUCATIVA:
"Los tests pasan → el codigo es correcto"
INCORRECTO. Los tests pueden pasar y el sistema violar INV-FREEZE-001
si el test no verifica ese invariante.
Pasar tests ≠ cumplir contratos. Son tareas separadas.
```

---

## TEMA 14 — RELAY PROMPT

```
PROMPT ALUMNO — RELAY PROMPT PARA RELAY_024

Sos el primer alumno en iniciar RELAY_024.

ESTADO DEL SISTEMA (fuente: RELAY_POINTER_V4_023 + PATCH1):
  RELAY ACTIVO: 024 — ABIERTO
  FUENTE CANONICA: RELAY_POINTER_V4_024_COMPLETO.md (ID: 1M__Ivl5f3PH6Dr5VxrYtAIj9Wjo_zApm)
  Si ese ID no existe en Drive: usar RELAY_POINTER_V4_023.md (ID: 1ESp9KzXADbfoEvZgN0_kw3grpfpsx8_h)

TAREA RECOMENDADA (Opcion 1):
  PROMPT-002 — teardown_all_sessions en SessionScheduler concreto
  Precondicion: FreezeAwareMixin disponible (R023)
  Contrato: CONTRACT_AESP_SESSION_INTEGRATION_V1.md (ID: 1RBLDUjPeNmP_iBr6fLFomP4qXulI5013)
  ADVERTENCIA: verificar ANTES si el docente ya definio cual session_scheduler es canonico
  Si no hay decision: tomar Opcion 3 (RES.170 MCP 2.0) que no depende de esa decision

ANTES DE EMPEZAR:
1. Leer el pointer canonico
2. Leer CONTRACT_AESP_SESSION_INTEGRATION_V1.md
3. Verificar decision docente sobre DT-AESP-003 canonical
4. Anunciar en el canal del grupo: "Tomo RELAY_024 — [nombre] — [fecha]"

PARAMETROS:
  ALUMNO_ID: ai.mpat.info@gmail.com
  DROPZONE_ID: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
  VERSION: V4_14

AL CERRAR:
  RELAY_024_V4.md — 10 secciones completas — NO resumidas
  RELAY_POINTER_V4_024.md actualizado
  Ambos a Drop Zone

ECONOMIA DE TOKENS:
  > 70%: puede tomar tarea nueva
  40-70%: solo baja complejidad
  < 40%: NO tomar nada — solo cerrar y documentar
```

---

## TEMA 15 — RESEARCH

```
PROMPT ALUMNO — RESEARCH RELAY_023

RESEARCH ACTIVA:
  RES.170 — MCP 2.0 Providers
    Estado: ABIERTO — sin precondicion dura — Complejidad: ALTA
    Destino: research/tech_radar/
    BRECHA: declarada en relay pero sin artefacto en Drive

RESEARCH IMPLICITA (no formalizada):
  - Bridge FFI Python→Rust — regla existe, investigacion no formal
  - Umbral optimo Cognitive Drift (DT-AESP-002) — empirica
  - Mock biometria (DT-AESP-001) — patron

TU TAREA:
1. Buscar: title contains 'RES_170' or title contains 'MCP_2'
2. Si no existe artefacto para RES.170: producir RES_170_MCP_2_INVESTIGACION_V1.md:
   - Pregunta de investigacion
   - Estado del arte en MPAT4
   - Hipotesis de impacto
   - Criterios de evaluacion GO/NO GO
3. Para DT-AESP-002: buscar investigacion empirica en Drive
   Si no hay: documentar como RESEARCH_PENDIENTE en RELAY_024
4. Subir a Drop Zone con destino: research

NOTA PEDAGOGICA:
Research en MPAT4 no es buscar en Google.
Es: formular la pregunta tecnica correcta, identificar que datos del sistema
necesitas para responderla, documentar la evidencia de forma auditable.
```

---

## TEMA 16 — RESOLUCIONES TECNICAS

```
PROMPT ALUMNO — RESOLUCIONES TECNICAS RELAY_023

RESOLUCIONES FORMALES ACTIVAS:

DEC-053: ReasoningStrategy en schema, importada por engine — implementada R019
DEC-059: emit() best-effort en CognitionEngine — implementada R022
DEC-060: strategy_override en reason() prioridad sobre self._strategy — R022
INV-FREEZE-001..005: ciclo EmergencyFreeze→SessionScheduler — R023
  ID contrato: 1RBLDUjPeNmP_iBr6fLFomP4qXulI5013

RESOLUCION PENDIENTE CRITICA:
  DT-AESP-003 canonical — DEC-NNN sin numero asignado aun
  Patron A (andrea): callback directo en ReviewManager
  Patron B (claudeacc1011): FreezeAwareMixin via EventBus

TU TAREA:
1. Leer CONTRACT_AESP_SESSION_INTEGRATION_V1.md
2. Extraer INV-FREEZE-001..005 en tabla:
   | INV | Descripcion | Verificable en codigo | Test que lo cubre |
3. Verificar DEC-053/059/060 implementadas en codigo real
4. Tabla de conciliacion patron A vs patron B:
   Razonar cual tiene mejor alineacion con INV-OBS-001 (solo via emit)
5. Producir RESOLUCIONES_TECNICAS_R023_AUDITADAS.md
6. Subir a Drop Zone con destino: resoluciones

TRAMPA EDUCATIVA:
"FreezeAwareMixin via EventBus es mejor porque usa el bus"
Esta afirmacion parece tecnica pero no es evidencia.
La pregunta correcta: cual patron preserva mejor INV-FREEZE-001..005
segun el CONTRATO — no segun opinion arquitectonica.
Leer el contrato ANTES de razonar, no despues.
```

---

## TEMA 17 — INFORMES

```
PROMPT ALUMNO — INFORMES DE ESTADO RELAY_023

METRICAS AL CIERRE R023:
  Relays cerrados: 023
  Deudas totales: 15 | Resueltas: 6 | Abiertas: 9 | Urgentes: 1 (DT-PERM-001)
  Artefactos ID confirmado: ~15 | ID pendiente: 3
  Decisiones docente pendientes: 2 (canonical DT-AESP-003 / RIESGO-SKILL-001)

ESTADO POR TRACK:
  Track A: 3 de 4 artefactos sin ID confirmado
  Track B: contrato + 5 artefactos DT-AESP-003 confirmados
  Track C: SKILL_V4_14 activa, V4_12 como backup

BLOQUEOS: DT-PERM-001 bloquea DT-COG-004 + movimiento TEMPORAL_ + relay/active/

TU TAREA:
1. Producir INFORME_ESTADO_R023_[tu_nombre].md:
   Seccion 1: Resumen ejecutivo (3 parrafos: logro / bloqueos / recomendacion)
   Seccion 2: Tabla de deudas tecnicas actualizada
   Seccion 3: Tabla de artefactos (ID Drive o PENDIENTE)
   Seccion 4: Decisiones de docente requeridas
   Seccion 5: Riesgo tecnico actual (P7: valor mas restrictivo en conflicto)
   Seccion 6: Proximo sprint recomendado

2. Audiencia: ai.mpat.info@gmail.com — no es un relay, es un documento de estado
3. Subir a Drop Zone con destino: docs

REGLA: Un informe que no puede leerse en 5 minutos no es un informe.
Es un relay con otro nombre.
```

---

# FIN DE LA AUDITORIA RELAY_023

Fuentes utilizadas:
- RELAY_POINTER_V4_023.md (ID: 1ESp9KzXADbfoEvZgN0_kw3grpfpsx8_h)
- RELAY_POINTER_V4_023_PATCH1.md (ID: 1exeKoupQKkH-SsQ_w-vCtqeWvMNuli-J)
- RELAY_023_V4.md (ID: 1L5Qje7LflSL-mMBAJ4P1meOhw9P9W7CL)

Temas auditados: 17 · Prompts producidos: 17
Drop Zone: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI

---
*AUDITORIA_RELAY_023_PROMPTS_ALUMNOS.md · ai.mpat.info@gmail.com · 2026-05-28*
*que has usado el formato de razonamiento adaptado por AGT*
