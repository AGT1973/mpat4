---
name: mpat4-relay
version: V4_14
description: >
  Skill de trabajo colaborativo relay para MPAT4 — Infraestructura Cognitiva Distribuida.
  Activar SIEMPRE cuando el alumno diga '.', 'continuar', 'continuar con mpat4', 'seguimos',
  'siguiente pendiente', 'retomar mpat4', o al inicio de sesión si hay archivos RELAY_POINTER
  en contexto o en Drive. La skill accede a Google Drive (carpeta MPAT4 raíz
  1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI), lee el RELAY_POINTER activo, determina el módulo
  pendiente, verifica siempre contra Drive (Drive siempre gana), genera los artefactos
  correspondientes con ruteo exacto de carpeta, los guarda firmados con ALUMNO_ID, actualiza
  el RELAY_POINTER y genera el prompt para el siguiente alumno.
  NUNCA sobreescribe. NUNCA código sin contrato. NUNCA Google Doc.
  SIEMPRE 10 secciones en el relay. SIEMPRE actualizar RELAY_POINTER al cerrar.
  SIEMPRE usar la ROUTING_MATRIX para decidir en qué carpeta guardar cada artefacto.
  Usar aunque el usuario no mencione la skill explícitamente si el contexto es claramente MPAT4.
compatibility: Google Drive MCP requerido
stack: Python · Rust · Node.js (investigación) · FastAPI · PyO3 (FFI)
structure_ref: tree_vfolders_v2.json (reorganización 2026-05-20)
changelog_v4_14: Runtime local registrado (FastAPI:8000 + MCP-SSE:5001) · run.bat en ROUTING_MATRIX · PASO 1b verificación de entorno · 2026-05-25 · agt1973@gmail.com
---

# MPAT4 — Skill Relay Colaborativo · V4_14

---

## REGLAS ABSOLUTAS — INVIOLABLES

- **NUNCA** formato Google Doc (mimeType `application/vnd.google-apps.document`)
- **NUNCA** sobreescribir un archivo — crear versión nueva; renombrar el original a `<nombre>.old.<ext>`
- **NUNCA** código sin contrato aprobado
- **NUNCA** schema sin contrato
- **NUNCA** Docker — solo UNIKERNEL: NanoVMs / Unikraft / Firecracker
- **NUNCA** cerrar sesión sin los 3 artefactos de cierre (RELAY_NNN+1 + RELAY_POINTER + PROMPT_ALUMNO)
- **NUNCA** relay sin las 10 secciones obligatorias
- **NUNCA** guardar un artefacto sin consultar primero la ROUTING_MATRIX
- **NUNCA** código Rust sin su `CONTRACT_RUST_[MODULO].md` y su `types.rs`
- **SIEMPRE** `contentMimeType: "text/plain"` para `.md` / `.yaml` / `.skill`
- **SIEMPRE** `disableConversionToGoogleType: true` en cada llamada a Drive
- **SIEMPRE** `contentMimeType: "text/x-python"` para `.py`
- **SIEMPRE** `contentMimeType: "application/json"` para `.json`
- **SIEMPRE** `contentMimeType: "text/x-rustsrc"` para `.rs`
- Si al guardar `.py` o `.rs` largo aparece "No approval received": dividir en partes. Si persiste: guardar como `.md` provisional + nota en relay.

---

## CONFIGURACION

```
FOLDER_ID_ROOT: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI  → MPAT4 raíz
MCP requerido:  Google Drive
MCP opcional:   MCP MPAT4 (resuelve rutas semánticas → IDs)
Stack:          Python 3.14 No-GIL · Rust (stable) · Node.js (investigación)
FFI:            PyO3 (Python ↔ Rust)
Front (en evaluación): FastAPI · Django · Flask · Node.js

RUNTIME_LOCAL — activo en todas las PCs de alumnos desde 2026-05-25:
  FastAPI:        http://127.0.0.1:8000       (API principal del proyecto)
  MCP MPAT4 SSE:  http://127.0.0.1:5001       (servidor MCP propio — SSE)
  MCP health:     http://127.0.0.1:5001/health → {"status":"ok","server":"mcp-mpat4","version":"V4_15","sse_url":"http://localhost:5001/sse"}
  Launcher:       run.bat  (inicia iniciar_mcp.bat + uvicorn + Brave)
  MCP script:     D:/__proyectos 2026/MPAT/herramientas/mcps/mcp_mpat4_v4_15.py
  MCP launcher:   D:/__proyectos 2026/MPAT/herramientas/mcps/iniciar_mcp.bat
```

---

## IDs DE DRIVE — ESTRUCTURA V4_14

```json
{
  "MPAT4/":                              "1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI",
  "herramientas/":                       "1bj3eHn0CSuE_CTGjJ3pG0lGtcVXYmtPg",
  "herramientas/skills/":                "1rrDNblne6P_IwpCnDfmAHKen4KUuua4f",
  "herramientas/mcps/":                  "1kNWfVtJ2MSLyG7pgYXeIP-oipOCVdC-b",

  "contracts/":                          "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0",
  "schemas/":                            "1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG",
  "resoluciones/":                       "1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU",
  "deprecated/":                         "14b47yd91-ebxV_rp_HVkndp0JKKthF2m",

  "relay/":                              "1DN0-L3tjW0TVPy2EaAU40aUsUpcJ2aXQ",
  "relay/active/":                       "1rE7k0i8x_vD0sNSa8z_66zGEeKunvwG_",
  "relay/temporal/":                     "1UkdGMjAIuWGBYiuJ_w7CDa173FD1Rk3N",
  "relay/pointer/":                      "1uC3StJMvPpOizTZOa_OyKPt12oIzTLe_",
  "relay/docs/":                         "1MoV0ExVrl1ymlZ3dnt3gPUJsrlQ3zfiW",

  "core/":                               "1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC",
  "core/cognition/":                     "1rexYAfWICisZs4B51V3nmh3gOStK6rWJ",
  "core/cognition/agents/":              "1FoQYxO9aBhpRGh8PEbiPG1Tblm1HbFTU",
  "core/cognition/context/":             "1jh50caSvu7M2iSgrvw50oliPWBb-S7yN",
  "core/cognition/kernel/":              "1x4y8ijc6bybDOQlU1KwyXNevjLODax5g",
  "core/cognition/orchestration/":       "16XisYAfWICisZs4B51V3nmh3gOStK6rWJ",
  "core/cognition/planning/":            "1dzhGpyFfc6OBAcyZfJV9min3pZQsu718",
  "core/cognition/reasoning/":           "1yIN_cbk2xOcNzhDJFySleJ-9VPYNkGdy",

  "core/event_bus/":                     "1lsaMPtDRFcXPGdBrZ8fAilsCNhpXZZiG",
  "core/federation/":                    "1XZ_M7ShjovYYTAS-5foL6-dElFTzJywW7",
  "core/execution_graph/":              "1XY8JEOFPc-scoUCGgBkwEpVann64MvA3",
  "core/governance/":                    "1nK9zcVKHoMx_qe16B_Lu4SyKZZPkS06S",
  "core/memory/":                        "1CtYQRsZGh6r8UZPySpoHcnXbp0rLWgks",
  "core/observability/":                 "1r_cyX_YHtvLwzQZU59jZmkFh4e3MDjqf",
  "core/runtime/":                       "14tSLEH9_Ekt2VkXM8e-UDnej_WX1a80f",
  "core/sandboxing/":                    "1Vw4UP8u6SgXh_fAG8CeEWKfmotV4lBpL",

  "core/rust/":                          "PENDIENTE_CREAR",
  "core/rust/parsers/":                  "PENDIENTE_CREAR",
  "core/rust/codecs/":                   "PENDIENTE_CREAR",
  "core/rust/hot_paths/":               "PENDIENTE_CREAR",
  "core/rust/ffi_bridges/":             "PENDIENTE_CREAR",
  "core/rust/types/":                    "PENDIENTE_CREAR",

  "core/node_research/":                 "PENDIENTE_CREAR",

  "providers/":                          "17LCBYsOzjqnCYvru38FnytqH3E8h6Okl",
  "ecosystem/":                          "170be8bj51aAvByQO-fc7GYDkIKKAwPrM",
  "education/":                          "1wSoBpZi8pl22n9a4oisFp5vjCXGTcNab",
  "education/student_relays/":           "1SiT9S3vUYR6TlFvsryXKTEiSyg7LaTu_",
  "tests/":                              "1WjhY2Ch5YHsKlmVNFczFyownqOkfbnRO",
  "tests/unit/":                         "1Ngc-824Is0PUEFuJV6v9PoHgzNa7ONKO",
  "research/":                           "1lrgXcd_s3CxF766lYkTwdoRIeJeUqsHk",
  "research/benchmarks/":               "1R0grNq4D42LeNtigOFiu-QHkElaWQ8-_",
  "research/experiments/":              "1ooeCILfKqnavAi6aeEkkKHoF2LdStLRn",
  "research/futures/":                   "1E4i5Dc_JqMGZfF2LsVFPtxL2WIAqURw",
  "research/papers/":                    "1Yi5Erc1drlLqqQe9gID2mmOMSYyrC9EV",
  "research/tech_radar/":               "PENDIENTE_CREAR",
  "deployment/":                         "1F_S5O18VpC8Zg_VFPtxL2WIAqURwA1Z",
  "scripts/":                            "17Fy3Ya8TQWh2uzhSHkusRh577InU_Bvl",
  "docs/":                               "1FlL7ACOo7o-KANItFWIBuJ62ULIHFOz",
  "docs/public/":                        "1Dv_zPx2NLe0lbZvIodIdZsM_2U0uxn7C",
  "system_state/":                       "1RaDO7KViCevZXlw0rEwdCaTlt17aMUgx"
}
```

> Las rutas marcadas `PENDIENTE_CREAR` deben ser creadas por el docente o
> el primer alumno que trabaje Rust/Node. Usar `Google Drive:create_file` con
> `mimeType: "application/vnd.google-apps.folder"` y parentId correspondiente.

---

## STACK MULTILENGUAJE — PRINCIPIO DE CLASIFICACION

Antes de escribir una sola línea de código, clasificar el módulo:

```
¿Es un hot path, parser, codec o manejo crítico de memoria?
  → Rust  (core/rust/[subcarpeta]/)

¿Es lógica de agentes, orquestación, schema, API?
  → Python  (core/[modulo]/)

¿Es interfaz de usuario o integración web?
  → FastAPI (Python) · Investigar Node.js/Django/Flask en research/tech_radar/

¿Cruza la frontera Python ↔ Rust?
  → FFI con PyO3  (core/rust/ffi_bridges/)
```

### Orden inmutable por módulo Rust:
`CONTRACT_RUST → types.rs → implementación.rs → tests → FFI_BRIDGE.md`

### Lenguajes válidos en esta versión:
Python · JSON · YAML · TOML · Rust · JavaScript (solo investigación) · HTML · CSS

---

## ROUTING_MATRIX — DÓNDE GUARDAR CADA ARTEFACTO

> Consultar ANTES de guardar cualquier archivo. Si el tipo no está: preguntar.

| Tipo de artefacto | Nombre típico | Carpeta destino | ID |
|---|---|---|---|
| CONTRACT Python | `CONTRACT_[MODULO]_V1.md` | `contracts/` | `1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0` |
| CONTRACT Rust | `CONTRACT_RUST_[MODULO]_V1.md` | `contracts/` | `1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0` |
| SCHEMA Pydantic | `schema_[modulo].py` | `schemas/` | `1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG` |
| TYPES Rust | `types_[modulo].rs` | `core/rust/types/` | PENDIENTE_CREAR |
| IMPL Python | `[modulo].py` | `core/[modulo]/[submodulo]/` | ver IDs arriba |
| IMPL Rust | `[modulo].rs` | `core/rust/[subcarpeta]/` | PENDIENTE_CREAR |
| FFI BRIDGE | `FFI_[modulo]_BRIDGE.md` | `core/rust/ffi_bridges/` | PENDIENTE_CREAR |
| RELAY activo | `RELAY_NNN.md` | `relay/active/` | `1rE7k0i8x_vD0sNSa8z_66zGEeKunvwG_` |
| RELAY_POINTER | `RELAY_POINTER_V4_*.md` | `relay/pointer/` | `1uC3StJMvPpOizTZOa_OyKPt12oIzTLe_` |
| RELAY temporal | borrador WIP | `relay/temporal/` | `1UkdGMjAIuWGBYiuJ_w7CDa173FD1Rk3N` |
| PROMPT_ALUMNO | `PROMPT_ALUMNO_RELAY_NNN.md` | `relay/docs/` | `1MoV0ExVrl1ymlZ3dnt3gPUJsrlQ3zfiW` |
| TEST unitario | `test_[modulo].py` | `tests/unit/` | `1Ngc-824Is0PUEFuJV6v9PoHgzNa7ONKO` |
| TEST Rust | `[modulo]_test.rs` | `core/rust/[subcarpeta]/` | PENDIENTE_CREAR |
| RESOLUCION | `RES_NNN_*.md` | `resoluciones/` | `1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU` |
| TECH RADAR | `TECH_RADAR_[FECHA].md` | `research/tech_radar/` | PENDIENTE_CREAR |
| RESEARCH futuro | `FUT_NNN_*.md` | `research/futures/` | `1E4i5Dc_JqMGZfF2LsVFPtxL2WIAqURw` |
| RELAY educativo | `RELAY_*.md` (copia) | `education/student_relays/` | `1SiT9S3vUYR6TlFvsryXKTEiSyg7LaTu_` |
| SKILL herramienta | `*.skill` / `*.md` | `herramientas/skills/` | `1rrDNblne6P_IwpCnDfmAHKen4KUuua4f` |
| MCP herramienta | `*.py` (servidor MCP) | `herramientas/mcps/` | `1kNWfVtJ2MSLyG7pgYXeIP-oipOCVdC-b` |
| LAUNCHER bat | `run.bat` / `iniciar_mcp.bat` | `herramientas/mcps/` | `1kNWfVtJ2MSLyG7pgYXeIP-oipOCVdC-b` |
| DOC pública | `*.md` | `docs/public/` | `1Dv_zPx2NLe0lbZvIodIdZsM_2U0uxn7C` |

### Regla de desambiguación:
1. ¿Contrato? → `contracts/` sin excepción.
2. ¿Schema Pydantic? → `schemas/` sin excepción.
3. ¿Types Rust? → `core/rust/types/` sin excepción.
4. ¿Código implementación? → clasificar por lenguaje → `core/[modulo]/` (Python) o `core/rust/[sub]/` (Rust).
5. ¿Herramienta del proyecto (MCP, bat, skill)? → `herramientas/mcps/` o `herramientas/skills/`.
6. ¿Duda? → Preguntar. No asumir.

---

## FLUJO DE SESION — 7 PASOS

### PASO 0 — IDENTIFICACION DEL ALUMNO

Preguntar: "¿Nombre o email para registrar tu autoría en MPAT4?"
Guardar como **ALUMNO_ID**. Se usa en el encabezado de TODOS los archivos.
Registrar ALUMNO_ID en el `RELAY_NNN+1.md` y en el `RELAY_POINTER`.

---

### PASO 1 — LEER ESTADO Y TOMAR CONTROL

1. Buscar `RELAY_POINTER_V4*.md` más reciente en `relay/pointer/` (ID: `1uC3StJMvPpOizTZOa_OyKPt12oIzTLe_`).
2. Actualizar RELAY_POINTER: ALUMNO_ID como "trabajando", estado "EN_PROGRESO".
3. Copiar trabajo a `relay/temporal/` (ID: `1UkdGMjAIuWGBYiuJ_w7CDa173FD1Rk3N`).
4. **Verificar firma del relay anterior:**
   - Firmado → continuar normalmente.
   - Sin firma → alumno anterior sin tokens. Informar: "RELAY_[NNN] sin firma — cerrando desde temporal/ antes de avanzar."
5. Leer `RELAY_NNN.md` activo.
6. Informar: "Relay activo: RELAY_[NNN] — [descripción breve]"

---

### PASO 1b — VERIFICAR RUNTIME LOCAL *(nuevo en V4_14)*

```
GET http://127.0.0.1:5001/health

RESULTADO OK → {"status":"ok","server":"mcp-mpat4","version":"V4_15",...}
  Informar: "MCP MPAT4 local activo — V4_15"
  Continuar a PASO 2.

RESULTADO ERROR o sin respuesta:
  Informar al alumno:
  ┌──────────────────────────────────────────────────────┐
  │ El runtime local no está activo.                     │
  │ Ejecutar run.bat antes de continuar.                 │
  │                                                      │
  │ Ubicación:                                           │
  │   D:/__proyectos 2026/MPAT/run.bat                   │
  │                                                      │
  │ Esto inicia:                                         │
  │   - MCP MPAT4 SSE en :5001                           │
  │   - FastAPI en :8000                                 │
  │   - Brave con ambas URLs                             │
  └──────────────────────────────────────────────────────┘

  EXCEPCION — no bloquear si:
    El alumno trabaja solo en Drive (sin código ni API).
    Ejemplo: redactar contrato, auditar estructura, revisar relay.
    En ese caso: informar "Runtime no detectado — continuando en modo Drive."
```

---

### PASO 2 — VERIFICAR ESTADO REAL EN DRIVE

- Listar archivos en la carpeta del módulo activo.
- **NO confiar en el relay — Drive siempre gana.**
- Si Drive difiere → creer a Drive, documentar discrepancia en sección 10.
- Verificar: contratos, schemas, types.rs, implementaciones, tests.

---

### PASO 3 — CARGAR SOLO LO NECESARIO

1. RELAY_POINTER → qué módulo trabajar
2. RELAY_NNN.md activo → tarea exacta
3. Contrato del módulo (si existe)
4. Schemas o types.rs relacionados (si existen)

No cargar módulos no relacionados — economía de tokens.

---

### PASO 4 — GENERAR ARTEFACTO SEGÚN ESTADO

| Estado del módulo | Artefacto | Lenguaje |
|---|---|---|
| Sin contrato | `CONTRACT_[MODULO]_V1.md` | — |
| Sin schema / types | `schema_[modulo].py` o `types_[modulo].rs` | Python / Rust |
| Sin implementación | módulo con invariantes | Python o Rust según clasificación |
| Sin FFI bridge | `FFI_[modulo]_BRIDGE.md` + código PyO3 | Python + Rust |
| Todo completo | investigación tech_radar o resolución de deuda | — |

**Encabezado obligatorio en CADA archivo:**
```
# [NOMBRE_ARCHIVO]
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [modulo] · Lenguaje: [Python|Rust|FFI] · Versión: V4_14
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
```

**Leyes arquitecturales — aplican a todo código:**
- Todo runtime: Firecracker / NanoVMs / Unikraft — NUNCA Docker
- Comunicación: subsistema → Event Bus → subsistema — NUNCA directa
- Memoria: siempre externa (Memory Fabric) — NUNCA en el runtime
- Todo skill: sandboxeable
- Todo relay: serializable
- Rust ↔ Python: solo via PyO3 — NUNCA subprocess

---

### PASO 5 — GUARDAR EN DRIVE CON RUTEO EXACTO

1. Identificar tipo de artefacto.
2. Consultar ROUTING_MATRIX → carpeta destino + ID.
3. Si la carpeta es PENDIENTE_CREAR: crearla y registrar el ID nuevo en el relay.
4. Confirmar con el alumno si hay ambigüedad.
5. Guardar con `disableConversionToGoogleType: true`.
6. Si el archivo ya existe: crear versión nueva → renombrar original a `<nombre>.old.<ext>`.
7. Registrar en sección 2 del relay: `archivo | carpeta | ID Drive | estado`.

---

### PASO 6 — CIERRE — 3 ARTEFACTOS OBLIGATORIOS

#### Control de tokens — ejecutar ANTES de cada acción:

| Tokens libres | Acción permitida |
|---|---|
| > 80% | Tareas grandes · módulos nuevos · lotes de migración ALTA |
| > 60% | Tareas medias · sub-tarea del relay · rescate de huérfanos |
| > 40% | Preparar cierre · artefactos · documentar mejoras · próximo relay |
| > 20% | Solo evaluación · auditoría · informe · prompt relay · responder dudas |
| ≤ 20% | CERRAR AHORA — solo los 3 artefactos de cierre, nada más |

> Siempre se generan los 3 artefactos de cierre.
> Si la tarea terminó → limpiar temporal/ antes de cerrar.
> Si la tarea no terminó → dejar en temporal/ como huérfano con ESTADO_PARCIAL.md.

#### Los 3 artefactos obligatorios:

**6a.** `relay/active/RELAY_NNN+1.md` — 10 secciones completas — ID carpeta: `1rE7k0i8x_vD0sNSa8z_66zGEeKunvwG_`
**6b.** `relay/pointer/RELAY_POINTER_V4_[FECHA].md` — estado global actualizado — ID carpeta: `1uC3StJMvPpOizTZOa_OyKPt12oIzTLe_`
**6c.** `relay/docs/PROMPT_ALUMNO_RELAY_NNN+1.md` — prompt listo para copiar al grupo — ID carpeta: `1MoV0ExVrl1ymlZ3dnt3gPUJsrlQ3zfiW`

---

### PASO 7 — VERIFICACION FINAL DE RUTEO

Antes de cerrar sesión, confirmar que cada archivo guardado:
- Tiene encabezado firmado con ALUMNO_ID, fecha y lenguaje.
- Está en la carpeta correcta según ROUTING_MATRIX.
- Tiene su ID de Drive registrado en sección 2 del RELAY_NNN+1.
- Si hay carpetas PENDIENTE_CREAR que se crearon: registrar los nuevos IDs en el relay y en el MCP (avisar al docente para actualizar mcp_mpat4.py).

---

## ESTRUCTURA DEL RELAY — 10 SECCIONES OBLIGATORIAS

```markdown
# RELAY_NNN.md
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [modulo] · Lenguaje: [Python|Rust|FFI|Multi] · Sistema: MPAT4 V4_14

[APERTURA] — módulo, prioridad, situación al iniciar

[INFO_ALUMNO] — qué leer primero, qué NO tocar

1. OBJETIVO DE ESTA SESION
   Qué se hizo efectivamente.

2. ARTEFACTOS CREADOS
   archivo | tipo | lenguaje | carpeta | ID Drive | estado

3. SCHEMAS / TYPES DEFINIDOS
   archivo | lenguaje | clases/structs | ID Drive | invariantes

4. EVENTOS DEFINIDOS
   tipo_evento | clase | cuándo se emite

5. DECISIONES ARQUITECTURALES
   DEC-NNN: decisión → razón → consecuencia

6. RIESGOS DETECTADOS
   RIESGO-NNN: descripción → impacto → mitigación
   Estado: Activo | Heredado | Resuelto

7. PROXIMA PRIORIDAD
   Módulo + tarea exacta + lenguaje + precondiciones

8. ARCHIVOS CRITICOS A LEER PRIMERO
   archivo | lenguaje | carpeta | ID Drive

9. INVARIANTES — NO ROMPER
   Lista completa — no "ver contrato"

10. DEUDA TECNICA
    ítem | lenguaje | motivo | prioridad | quién resuelve

[TRASPASO → RELAY_NNN+1]
  Mensaje listo para copiar al grupo.
  Firmado: [ALUMNO_ID]
```

---

## PROTOCOLO DE TRASPASO

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MPAT4 · TRASPASO AL SIGUIENTE ALUMNO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Sesión cerrada por:  [ALUMNO_ID]
 RELAY ejecutado:     RELAY_[NNN]
 Tarea completada:    [descripción]
 Lenguaje(s) usado(s): [Python|Rust|FFI]
 Próximo relay:       RELAY_[NNN+1] — [descripción]
 Archivos críticos:   [IDs de Drive]
 IDs nuevos creados:  [si se crearon carpetas PENDIENTE_CREAR]

 COPIAR AL GRUPO:
 "Terminé RELAY_[NNN] en MPAT4.
  Completé: [tarea] ([lenguaje]).
  Próximo: RELAY_[NNN+1].
  Firmado: [ALUMNO_ID] · [FECHA]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## SKILLS DISPONIBLES EN EL ECOSISTEMA

| Skill | Activar cuando | Archivo |
|---|---|---|
| `mpat4-relay` (este) | trabajo general MPAT4 | `SKILL_V4_14_en_gdrive.md` |
| `relay-lifecycle` | gestión de ciclo de vida de tareas en grupo | `relay-lifecycle.skill` |
| `mpat3-to-mpat4` | migración por lotes MPAT3 → MPAT4 | `mpat3-to-mpat4.skill` |
| `tech-research` | investigación de nuevas tecnologías para V4/V5 | `tech-research.skill` |
| `python-rust-production` | producción de código multilenguaje | `python-rust-production.skill` |

---

## CAMBIOS V4_13 → V4_14

| Qué cambió | Detalle |
|---|---|
| RUNTIME_LOCAL registrado | FastAPI `:8000` + MCP MPAT4 SSE `:5001` documentados en CONFIGURACION |
| MCP health confirmado | `{"status":"ok","server":"mcp-mpat4","version":"V4_15","sse_url":"http://localhost:5001/sse"}` |
| PASO 1b agregado | Verificación de entorno local antes de trabajar — con excepción para trabajo solo-Drive |
| ROUTING_MATRIX actualizada | `run.bat` / `iniciar_mcp.bat` → `herramientas/mcps/` |
| Versión en encabezados | V4_13 → V4_14 |
| Autor corrección | agt1973@gmail.com · 2026-05-25 |

---

*SKILL_V4_14_en_gdrive.md · AGT 2026-05-25 · agt1973@gmail.com*
*que has usado el formato de razonamiento adaptado por AGT*
