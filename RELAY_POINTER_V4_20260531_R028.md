# MPAT4_DEST
# destino: relay_active
# nombre: RELAY_POINTER_V4_20260531_R028.md
# alumno: ai.mpat.info@gmail.com
# que has usado el formato de razonamiento adaptado por AGT

# RELAY_POINTER_V4_20260531_R028.md
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Para copiar al grupo de alumnos
## Reemplaza: RELAY_POINTER_V4_20260531_R027.md (ID: 1fxB3E9EwdpPqvDrC8RE9C4LYWeJ5CBZf)
## que has usado el formato de razonamiento adaptado por AGT

---

Termine RELAY_028 en MPAT4.

Complete:
- DT-BUS-003 — LamportTickPayload Pydantic V3 en event_schema.py V4_14 (CERRADA)
- EVENT_BUS_CONTRACT_V4_03 — lamport.tick movido de PENDIENTE_REGISTRO a ACTIVO, seccion 4c completa
- INV-BUS-014 nueva: el schema NO calcula tick — logica en dispatcher
- Nota arquitectura lamport.tick vs mesh.clock_tick documentada (NO unificar)
- DT-BUS-004 stub — bus_policy.py + config_policy.yaml generados (integracion pendiente)

Proximo: RELAY_029

Leer en orden:
1. MAPA_UNIFICADO_SISTEMA_2026-05-29.md (ID: 1sXmKgMJD_ITuyy2Ls18EkaqMUvF6j3gO)
2. _TECNICA_RELAY_028_MPAT_V4.md (ID: 1AXOIEpxnnN3YyZT_lv778EwJGcAHzKeD)
3. EVENT_BUS_CONTRACT_V4_03.md (ID: 1UbCqRwvZCFR9zywa69v--cJAMo-oJhH6) — contrato actual
4. event_schema_V4_14_RELAY028.py (ID: 1LX7bAhW5BRA98KL94yDhsWGyh9ZBYhuO) — base a extender
5. event_bus_schema_V4_02.py (ID: 145LEB4uWjzfIkPq7VmDXSlARGAkPFVsy) — KG payloads DT-BUS-002
6. event_bus_v4.py (ID: 1pMu_-qIc5hjWGh8BaPlQ6bZCZvbeI1Uq) — integrar BusPolicy
7. bus_policy_V1_00_RELAY028.py (ID: 1i6PA7VwTqn5X_52tp0ApV-TFiQt_myqp)

Tarea RELAY_029 — dos acciones (elegir segun tokens):

ACCION A — DT-BUS-002 (MEDIA, ~40% tokens):
  Modulo: schemas/event_schema.py
  Accion: agregar KGNodeUpsertedPayload y KGGroundingCompletePayload desde event_bus_schema_V4_02.py
  Agregar kg.node_upserted y kg.grounding_complete a ALL_EVENT_TYPES
  Mover tipos KG de PENDIENTE_REGISTRO a ACTIVO en EVENT_BUS_CONTRACT_V4_04
  Verificar que test T-V402-25 pasa (exactamente 23+ tipos)

ACCION B — DT-BUS-004 integracion (ALTA, ~30% tokens):
  Modulo: event_bus/event_bus_v4.py
  Accion: agregar parametro policy: BusPolicy = None a EventBusV4.__init__
  Si policy es None: usar BusPolicy.from_yaml()
  Usar policy.loop_timeout_secs, policy.critical_events, policy.default_tokens
  Verificar que todos los tests existentes pasan sin modificacion (retro-compat garantizada)
  Generar tests BusPolicy: test_bus_policy_defaults(), test_bus_policy_from_yaml(), test_inv_bus1_violation(), test_inv_bus5_violation()

Si tokens > 60%: hacer ambas acciones en orden A → B.
Si tokens 30-60%: solo ACCION A.
Si tokens < 30%: NO tomar — solo documentar y generar relay.

Recordar: Drop Zone unica carpeta de guardado.
ID Drop Zone: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
Cabecera MPAT4_DEST obligatoria en todo archivo.

---

## IDs CLAVE — ACTUALIZADOS R028

| Archivo | ID |
|---|---|
| _TECNICA_RELAY_028_MPAT_V4.md | 1AXOIEpxnnN3YyZT_lv778EwJGcAHzKeD |
| EVENT_BUS_CONTRACT_V4_03.md | 1UbCqRwvZCFR9zywa69v--cJAMo-oJhH6 |
| EVENT_BUS_CONTRACT_V4_02.md | 1f8MOu1ohJYnw4FgpULVqGFTB4YJae0Ru |
| event_schema_V4_14_RELAY028.py | 1LX7bAhW5BRA98KL94yDhsWGyh9ZBYhuO |
| event_schema_V4_13 | 1ypdJjtbex9i5B2QYLHRbLZXgb2whhu_U |
| event_bus_schema_V4_02.py | 145LEB4uWjzfIkPq7VmDXSlARGAkPFVsy |
| event_bus_v4.py | 1pMu_-qIc5hjWGh8BaPlQ6bZCZvbeI1Uq |
| bus_policy_V1_00_RELAY028.py | 1i6PA7VwTqn5X_52tp0ApV-TFiQt_myqp |
| config_policy_V1_00_RELAY028.yaml | 1Sn-bYZ4UdH-mDr-Qy_46t-fYyKZpP8uo |
| test_lamport_tick_RELAY028.py | 1RPs1LYPQ_gAtdfmTe2p_Brnf8pkxza2d |
| RELAY_027 resolucion | 1q3E8eQnPJx22WDUPZX7s2F4Cb1WdQIef |
| MAPA_UNIFICADO_SISTEMA | 1sXmKgMJD_ITuyy2Ls18EkaqMUvF6j3gO |
| schemas/ carpeta | 1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG |
| contracts/ carpeta | 1nK9zcVKHoMx_qe16B_Lu4SyKZZPkS06S |
| relay/ carpeta | 1DN0-L3tjW0TVPy2EaAU40aUsUpcJ2aXQ |
| Drop Zone | 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI |

---

## DEUDAS TECNICAS ABIERTAS — R028

| ID | Descripcion | Prioridad | Estado |
|---|---|---|---|
| DT-PERM-001 | canAddChildren=false | URGENTE | Docente |
| DT-BUS-002 | KG payloads en event_schema.py | MEDIA | RELAY_029 |
| DT-BUS-004 | integracion BusPolicy en event_bus_v4.py | ALTA | RELAY_029 |
| DT-AESP-004-INT | BudgetWindow + Memory Fabric | ALTA | Proximo >40% tokens |
| BRECHA-CONT-RUNTIME-001 | runtime_core sin contrato | ALTA | Docente |
| BRECHA-CARPETA-RUNTIME-001 | 3 carpetas runtime_core | ALTA | Docente |

Firmado: ai.mpat.info@gmail.com · 2026-05-31