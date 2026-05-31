# CONVERGENCIA_V4_V3_02.md
## DEC-045 — Mapa de convergencia entre cadenas MPAT4 (V4) y MPAT V3_02
## Autor: cursos.agt.ia@gmail.com (docente_AGT_2026) · 2026-05-19
## Módulo: docs/ · Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Relay: RELAY_017_V4

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. PROBLEMA QUE ESTE DOCUMENTO RESUELVE

La carpeta `relay/` contiene archivos de DOS sistemas distintos que coexisten:

**Cadena V4** (MPAT4 infra): `RELAY_001.md` → `RELAY_014.md` → `RELAY_015_V4.md` → `RELAY_016_V4.md` → ...
**Cadena V3_01/02** (MPAT V3): `RELAY_015.md`, `RELAY_016.md`, ... `RELAY_028.md`

Un alumno nuevo que lee `relay/` ve dos `RELAY_015.md` y no sabe cual es el activo. Este documento resuelve esa ambiguedad de forma permanente y define las reglas de nomenclatura para V4 en adelante.

---

## 2. MAPA DE LAS DOS CADENAS

### Cadena V4 — MPAT4 Infraestructura (la activa)

| Relay | Módulo | Autor | Fecha | ID Drive |
|---|---|---|---|---|
| RELAY_001 | contracts/ — ECS_CONTRACT_V1 | cursos.agt.ia | 2026-05-12 | (en relay/) |
| RELAY_002 | schemas/ base — ecs, event | cursos.agt.ia | 2026-05-12 | (en relay/) |
| RELAY_003 | event_bus/ schemas | andrea.proyect | 2026-05-12 | (en relay/) |
| RELAY_004 | event_bus.py | ariel.garcia.traba | 2026-05-13 | (en relay/) |
| RELAY_005 | governance_engine/ — config + budget_engine | clases.andrea | 2026-05-13 | (en relay/) |
| RELAY_006 | memory_fabric/ | cursos.agt.ia | 2026-05-13 | (en relay/) |
| RELAY_007 | session_scheduler/ | cursos.agt.ia | 2026-05-13 | (en relay/) |
| RELAY_008 | runtimes/ — runtime_manager | (completado) | 2026-05-13 | (en relay/) |
| RELAY_009 | observability/ — observability_collector | clases.andrea | 2026-05-14 | (en relay/) |
| RELAY_010 | agent_registry/ — agent_registry V1 | ariel.garcia.traba | 2026-05-14 | (en relay/) |
| RELAY_011–014 | cognition/ — cognition_engine + DEC-044 | cursos.ai.agt | 2026-05-14/17 | (en relay/) |
| RELAY_015_V4 | governance/ config_policy_V4_02 + apertura V4 post-V3 | docente_AGT_2026 | 2026-05-19 | 1tfPf9g5Yg5Os1G-MzbGCSXwiSZIHP-Vs |
| RELAY_016_V4 | cognition/ integration_test_cognition (DT-COG-002) | docente_AGT_2026 | 2026-05-19 | 11191jfdgd_ThErzYGAxaaev2GfcR4B0G |
| RELAY_017_V4 | agent_registry/ sync + docs/ CONVERGENCIA (DT-REG-001 + DEC-045) | docente_AGT_2026 | 2026-05-19 | este relay |

### Cadena V3_01/02 — MPAT V3 (CERRADA — solo lectura)

| Relay | Contenido | Fecha | Estado |
|---|---|---|---|
| RELAY_015.md | V3_01 — contenido de ciclo V3 | 2026-05-17 | CERRADO |
| RELAY_016.md – RELAY_025.md | V3_02 investigaciones, RES, saneamiento | 2026-05-18 | CERRADO |
| RELAY_026.md – RELAY_028.md | V3_02 consolidacion final: RES.155-157, DT-004, cierre V3 | 2026-05-19 | CERRADO |

**La cadena V3 esta SELLADA.** RELAY_028 es el ultimo relay de V3. No se generaran mas archivos RELAY_NNN.md sin sufijo _V4 en relay/.

---

## 3. REGLA DE NOMENCLATURA — DEFINITIVA

A partir de RELAY_015_V4 (2026-05-19) rige esta regla para la cadena V4:

```
RELAY_{NNN}_V4.md   →   relay de la cadena V4 (MPAT4 infra)
RELAY_{NNN}.md      →   relay historico de V3_01/02 (CERRADO, solo lectura)
```

El sufijo `_V4` es obligatorio para todos los relays de la cadena V4 a partir de RELAY_015. Los relays 001–014 no tienen el sufijo porque se crearon antes de que existiera la collision. Estan igualmente en la cadena V4.

El RELAY_POINTER activo siempre apunta a un archivo con sufijo `_V4`. Si un POINTER apunta a un archivo sin sufijo, es de la cadena V3 y esta cerrado.

---

## 4. GUIA PARA EL ALUMNO NUEVO

Al llegar a relay/ vas a ver archivos mezclados de ambas cadenas. Para saber cual es tu punto de partida:

1. Leer el RELAY_POINTER mas reciente en relay/ (nombre: `RELAY_POINTER_V4_ACTUALIZADO_*`).
2. El POINTER te dice exactamente que RELAY_NNN_V4.md leer.
3. Si el POINTER apunta a un archivo sin `_V4` en el nombre, reportarlo — es un error de configuracion.
4. Los archivos sin sufijo `_V4` son V3 historico. Se pueden leer para contexto pero NUNCA modificar.

---

## 5. MODULOS V4 — ESTADO AL DIA DE HOY

Todos los modulos P1-P10 del ciclo V4 estan completos. Lo que sigue es extension, integracion y mejoras:

| P | Módulo | Implementacion | Schema | Contrato | DT abiertas |
|---|---|---|---|---|---|
| 1 | contracts/ | — (solo doc) | — | ECS_CONTRACT_V1.md ✓ | — |
| 2 | schemas/ | — | 9 schemas ✓ | heredado | — |
| 3 | event_bus/ | event_bus.py ✓ | event_bus_schema.py ✓ | EVENT_BUS_CONTRACT ✓ | — |
| 4 | governance_engine/ | governance_engine.py + budget_engine.py ✓ | governance_schema ✓ | GOVERNANCE_CONTRACT ✓ | — |
| 5 | memory_fabric/ | memory_fabric.py ✓ | memory_fabric_schema.py ✓ | MEMORY_FABRIC_CONTRACT ✓ | — |
| 6 | session_scheduler/ | session_scheduler.py ✓ | session_scheduler_schema.py ✓ | SESSION_SCHEDULER_CONTRACT ✓ | — |
| 7 | runtimes/ | runtime_manager.py ✓ | (en schema base) | RUNTIME_CONTRACT ✓ | — |
| 8 | observability/ | observability_collector.py ✓ | observability_schema.py ✓ | OBSERVABILITY_CONTRACT ✓ | — |
| 9 | agent_registry/ | agent_registry_v2.py ✓ + sync patch ✓ | agent_registry_schema_v2.py ✓ | AGENT_REGISTRY_CONTRACT ✓ | DT-REG-004 (schema) |
| 10 | cognition/ | cognition_engine.py ✓ + integration test ✓ | cognition_schema.py ✓ | COGNITION_CONTRACT ✓ | — |

---

## 6. HERENCIA ARQUITECTURAL V3 → V4

V4 no descarta V3. Hereda sus decisiones criticas:

| Principio V3 | Equivalente en V4 | Donde vive en V4 |
|---|---|---|
| P1 (MCP universal) | P1 (Modularidad — no imports directos) | INV-COG-002, INV-REG-004 |
| P3 (Zero Trust) | P3 (Zero Trust) | INV-GOV-001 a INV-GOV-005 |
| P7 (Budget conservation law) | P7 (Budget inviolable) | BudgetEngine.check() + deduct() |
| P13 (AI Specifiers Rule) | INV-P13.1 a INV-P13.5 | agent_registry, cognition, governance |
| RES.115 (unikernel por tenant) | config_policy_V4_02.yaml: allowed_runtime_types | runtimes/ |
| RES.155 (eBPF/QUIC) | No migrado a V4 aun | DT pendiente — primer relay que lo necesite |
| RES.157 (OpenInference+QUIC) | observability_schema.py + observability_collector | observability/ |

---

## 7. DEUDA TECNICA QUE CRUZA LA FRONTERA V3→V4

| ID | Descripcion | Origen | Estado en V4 |
|---|---|---|---|
| DT-016-001 (V3) | tool_call delegacion via SubQ — path async completo | V3 | Pendiente |
| DT-QUIC-001 (V3) | RTT real post-handshake en QUICConnectionState | V3 | Pendiente |
| DT-02-001 (V3) | SchemaValidator strict=True para inputs con PII | V3 | Pendiente |
| DT-REG-004 (V4) | AgentDiscoveryResult schema: agregar next_page_token | V4 RELAY_013 | Pendiente |
| IC-02 (V3) | Duplicados TEST_SUITE en Drive | V3 | PENDIENTE COORDINADOR |

---

## 8. IDs CLAVE DE REFERENCIA

| Recurso | ID Drive |
|---|---|
| ESTADO_CIERRE_V3_DEFINITIVO_R028.md | 1QA4k7PjnkcGIok0m3rG1C_vnfZpuzNKH |
| ARQUITECTURA_base_V3_02_INC03.md | 1m8DLHltKpI8wrL8nn3_6Z-7W4KXlYgqm |
| config_policy_V4_02.yaml | 101maG_O0AeskOdoAm9o9RZGthNWHrghB |
| cognition_engine.py | 1wVyHrAvL0ZEYdgE7-hkqSKbdVIEzDz4R |
| integration_test_cognition.py | 188qPD8uGtkxZthOrH9PkGbRZo8t6ye7b |
| agent_registry_v2.py | 12ND59zwPVdsVXQ6QXBrw8IbaebGNJctw |
| agent_registry_v2_sync.py | 1qFOj-vw4eF_dV5moN3SmC7MiUQ5NJoJu |
| memory_fabric.py | 1Nl8sZnR7R19w7dV0b_vTKMpPrDRqldbc |
| relay/ (carpeta) | 1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte |
| docs/ (carpeta) | 1FlL7ACOo7o-KANItFWIBuJ62ULIHF_Oz |
| MPAT4 raiz | 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI |

---

*CONVERGENCIA_V4_V3_02.md · MPAT4 · 2026-05-19*
*cursos.agt.ia@gmail.com (docente_AGT_2026) · DEC-045 CERRADO · RELAY_017_V4*
*que has usado el formato de razonamiento adaptado por AGT*
