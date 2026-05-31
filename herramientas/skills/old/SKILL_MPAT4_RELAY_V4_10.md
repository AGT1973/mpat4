---
name: mpat4-relay
description: >
  Skill de trabajo colaborativo relay para MPAT4 — Infraestructura Cognitiva Distribuida.
  Activar SIEMPRE cuando el alumno diga '.', 'continuar', 'continuar con mpat4', 'seguimos',
  'siguiente pendiente mpat4', 'retomar mpat4', o al inicio de sesión si hay archivos
  RELAY_POINTER en contexto o Drive. La skill accede a Google Drive (carpeta MPAT4 raíz
  1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI), lee el RELAY_POINTER activo, determina el módulo
  pendiente, verifica siempre contra Drive (Drive siempre gana), genera los artefactos
  correspondientes, los guarda firmados con ALUMNO_ID, actualiza el RELAY_POINTER y genera
  el prompt para el siguiente alumno. NUNCA sobreescribe. NUNCA código sin contrato.
  NUNCA Google Doc. SIEMPRE 10 secciones en el relay. SIEMPRE actualizar RELAY_POINTER al cerrar.
  Usar aunque el usuario no mencione la skill explícitamente si el contexto es claramente MPAT4.
compatibility: Google Drive MCP requerido
---

# MPAT4 — Skill Relay Colaborativo · V4_10

## REGLAS ABSOLUTAS — INVIOLABLES

- **NUNCA** formato Google Doc (mimeType `application/vnd.google-apps.document`)
- **NUNCA** sobreescribir un archivo — crear versión nueva que consolide; renombrar el original a `<nombre>.old.<ext>`
- **NUNCA** código sin contrato aprobado (lenguajes ok: Python, JSON, YAML, TOML, Rust, JS, HTML, CSS, PHP)
- **NUNCA** schema sin contrato
- **NUNCA** Docker — solo UNIKERNEL: NanoVMs / Unikraft / Firecracker
- **NUNCA** cerrar sesión sin los 3 artefactos de cierre (RELAY_NNN+1 + RELAY_POINTER + PROMPT_ALUMNO)
- **NUNCA** relay sin las 10 secciones obligatorias
- **SIEMPRE** `contentMimeType: "text/plain"` para .md/.yaml/.skill y `disableConversionToGoogleType: true`
- **SIEMPRE** `contentMimeType: "text/x-python"` para .py
- **SIEMPRE** `contentMimeType: "application/json"` para .json
- Si al guardar .py largo aparece "No approval received": dividir en partes. Si persiste: guardar como .md provisional + nota en relay.

---

## CONFIGURACIÓN

```
FOLDER_ID_ROOT:   1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI   ← MPAT4 raíz
MCP requerido:    Google Drive
```

### IDs clave de MPAT4 (estructura nueva — verificada 2026-05-19)

```json
{
  "relay/":             "1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte",
  "relay/temporal/":    "1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu",
  "docs/":              "1FlL7ACOo7o-KANItFWIBuJ62ULIHF_Oz",
  "contracts/":         "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0",
  "schemas/":           "1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG",
  "resoluciones/":      "1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU",
  "core/":              "1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC",
  "core/cognition/":    "1rexYAfWICisZs4B51V3nmh3gOStK6rWJ",
  "core/event_bus/":    "1lsaMPtDRFcXPGdBrZ8fAilsCNhpXZZiG",
  "core/governance/":   "1nK9zcVKHoMx_qe16B_Lu4SyKZZPkS06S",
  "core/memory/":       "1CtYQRsZGh6r8UZPySpoHcnXbp0rLWgks",
  "core/observability/":"1r_cyX_YHtvLwzQZU59jZmkFh4e3MDjqf",
  "core/federation/":   "1XZ_M7ShjoVYTAS-5foL6-dElFTzJywW7",
  "core/execution_graph/":"1XY8JEOFPc-scoUCGgBkwEpVann64MvA3",
  "core/runtime_core/": "14tSLEH9_Ekt2VkXM8e-UDnej_WX1a80f",
  "core/sandboxing/":   "1Vw4UP8u6SgXh_fAG8CeEWKfmotV4lBpL",
  "providers/":         "17LCBYsOzjqnCYvru38FnytqH3E8h6Okl",
  "ecosystem/":         "170be8bj51aAvByQO-fc7GYDkIKKAwPrM",
  "relay_system/":      "1lrbtg7M7FAZ5Dqwij-dZ2fn4LFllItJz",
  "education/":         "1wSoBpZi8pl22n9a4oisFp5vjCXGTcNab",
  "tests/":             "1WjhY2Ch5YHsKlmVNFczFyownqOkfbnRO",
  "research/":          "1lrgXcd_s3CxF766lYkTwdoRIeJeUqsHk",
  "system_state/":      "1RaDO7KViCevZXlw0rEwdCaTlt17aMUgx",
  "deprecated/":        "14b47yd91-ebxV_rp_HVkndp0JKKthF2m"
}
```

Para el mapa completo de sub-carpetas con IDs consultar `MPAT4_STRUCTURE_WITH_IDS.json` (ID: `1DfKY71XFelKTaZKpnuUVLOWTEH3Egf9h`) en la raíz de Drive.

---

## FLUJO DE SESIÓN — 6 PASOS

### PASO 0 — IDENTIFICACIÓN DEL ALUMNO

Preguntar: "¿Nombre o email para registrar tu autoría en MPAT4?"  
Guardar como **ALUMNO_ID**. Se usa en el encabezado de TODOS los archivos generados.  
Si el alumno no sabe su email, aceptar cualquier identificador único (apodo, nombre).  
Registrar ALUMNO_ID en el `RELAY_NNN+1.md` y en el `RELAY_POINTER`.

---

### PASO 1 — LEER ESTADO Y TOMAR CONTROL

1. Buscar el `RELAY_POINTER_V4*.md` **más reciente** en `relay/` (ID: `1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte`).
2. Actualizar el RELAY_POINTER: colocar **ALUMNO_ID** como "trabajando" y estado "EN_PROGRESO".
3. Copiar el trabajo a realizar a `relay/temporal/` (ID: `1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu`). Esta es la mesa de trabajo limpia.
4. **Verificar firma del relay anterior:**
   - Si el RELAY_NNN anterior está firmado → continuar normalmente.
   - Si el RELAY_NNN anterior **NO está firmado** → asumir que el alumno anterior quedó sin tokens. Continuar desde `relay/temporal/`, cerrar ese relay, informar al alumno: "⚠️ RELAY_[NNN] anterior sin firma — alumno previo sin tokens. Continuando y cerrando desde temporal/."
5. Leer el `RELAY_NNN.md` activo en `relay/`.
6. Informar: **"Relay activo: RELAY_[NNN] — [descripción breve de tarea]"**

---

### PASO 2 — VERIFICAR ESTADO REAL EN DRIVE

- Listar archivos en la **carpeta del módulo activo** indicado por el RELAY_POINTER.
- **NO confiar en lo que dice el relay** — verificar Drive siempre.
- Si Drive difiere del relay → **creer a Drive**, documentar la discrepancia en la sección 10 del relay de cierre.
- Anotar qué existe realmente: contratos, schemas, implementaciones, tests.

---

### PASO 3 — CARGAR SOLO LO NECESARIO

Leer en este orden y **nada más**:

1. `RELAY_POINTER` (qué módulo trabajar)
2. `RELAY_NNN.md` activo (tarea exacta)
3. Contrato del módulo activo (si existe)
4. Schemas relacionados (si existen)

No cargar módulos no relacionados con el relay activo — economía de tokens.

---

### PASO 4 — GENERAR ARTEFACTO SEGÚN ESTADO

| Estado del módulo | Artefacto a generar |
|---|---|
| Sin contrato | `CONTRACT_V1.md` — 10 secciones obligatorias |
| Sin schema | `schema.py` — Pydantic V3, sin Docker |
| Sin implementación | Módulo Python con invariantes, sin Docker |
| Todo completo | Investigación o resolución de pendiente |

**Encabezado obligatorio en CADA archivo generado:**
```
# [NOMBRE_ARCHIVO]
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [módulo] · Versión: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
```

**Leyes arquitecturales que aplican a todo código:**
- Todo runtime: Firecracker / NanoVMs / Unikraft — NUNCA Docker
- Todo es evento → subsistema → Event Bus → subsistema
- Toda memoria es externa (Memory Fabric, no en runtime)
- Todo skill es sandboxeable
- Todo relay es serializable

---

### PASO 5 — GUARDAR EN DRIVE

- Guardar **solo** en la carpeta del módulo activo + `relay/`.
- Usar siempre `disableConversionToGoogleType: true`.
- Si el archivo ya existe: crear versión nueva → renombrar el original a `<nombre>.old.<ext>`.
- Registrar ID de Drive de cada archivo guardado — se usará en la sección 2 del relay de cierre.

---

### PASO 6 — CIERRE — 3 ARTEFACTOS OBLIGATORIOS

#### Token check antes de cerrar:
- **> 60% tokens restantes** → continuar con sub-tarea del mismo relay
- **< 60% tokens restantes** → preparar cierre
- **< 40% tokens restantes** → **CERRAR AHORA**, nada más

#### Los 3 artefactos obligatorios:

**6a. `relay/RELAY_NNN+1.md`** — 10 secciones (ver estructura abajo)  
**6b. `RELAY_POINTER_V4_ACTUALIZADO_[FECHA].md`** — en raíz MPAT4  
**6c. `docs/PROMPT_ALUMNO_RELAY_NNN+1.md`** — prompt listo para copiar al grupo

---

## ESTRUCTURA DEL RELAY — 10 SECCIONES OBLIGATORIAS

```markdown
# RELAY_NNN.md
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [módulo] · Sistema: MPAT4

[APERTURA] — módulo, prioridad, situación al iniciar

[INFO_ALUMNO] — qué leer primero, qué NO tocar

1. OBJETIVO DE ESTA SESIÓN
   Qué se hizo efectivamente.

2. ARTEFACTOS CREADOS
   archivo | carpeta | ID Drive | estado

3. SCHEMAS DEFINIDOS
   archivo | clases | ID Drive | invariantes

4. EVENTOS DEFINIDOS
   tipo_evento | clase | cuándo se emite

5. DECISIONES ARQUITECTURALES
   DEC-NNN: decisión → razón → consecuencia

6. RIESGOS DETECTADOS
   RIESGO-NNN: descripción → impacto → mitigación
   Estado: Activo | Heredado | Resuelto

7. PRÓXIMA PRIORIDAD
   Módulo + tarea exacta + precondiciones

8. ARCHIVOS CRÍTICOS A LEER PRIMERO
   Lista con IDs de Drive — no solo nombres

9. INVARIANTES — NO ROMPER
   Lista completa — no "ver contrato"

10. DEUDA TÉCNICA
    Qué quedó incompleto · por qué · quién lo resuelve

[TRASPASO → RELAY_NNN+1]
  Mensaje listo para copiar al grupo.
  Firmado: [ALUMNO_ID]
```

---

## ESTRUCTURA DEL CONTRATO — 10 SECCIONES OBLIGATORIAS

```markdown
1. OBJETIVO
2. MOTIVACIÓN ARQUITECTURAL
3. CAMPOS / INTERFACE (tabla con tipos)
4. EVENTOS QUE EMITE (tipo | payload mínimo)
5. EVENTOS QUE CONSUME
6. FLUJO OPERACIONAL (pasos numerados + ramas de error)
7. INVARIANTES (INV-XXX-NNN)
8. RIESGOS (tabla)
9. OBSERVABILIDAD (Redis + OTel + métricas)
10. SIGUIENTE ALUMNO (tarea + archivos + qué no tocar)
```

---

## PROTOCOLO DE TRASPASO

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MPAT4 · TRASPASO AL SIGUIENTE ALUMNO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sesión cerrada por: [ALUMNO_ID]
  RELAY ejecutado:    RELAY_[NNN]
  Tarea completada:   [descripción]
  Próximo relay:      RELAY_[NNN+1] — [descripción]
  Archivos críticos:  [IDs de Drive]

  COPIAR AL GRUPO:
  "Terminé RELAY_[NNN] en MPAT4.
   Completé: [tarea].
   Próximo: RELAY_[NNN+1].
   Firmado: [ALUMNO_ID] · [FECHA]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ESTADO DEL SISTEMA (verificado 2026-05-19)

El RELAY_POINTER activo es `RELAY_POINTER_V4_ACTUALIZADO_2026_05_19_R2.md`.  
**RELAY activo: RELAY_016_V4** — integration test CognitionEngine.

| P | Módulo | Estado |
|---|---|---|
| 1 | contracts/ | COMPLETO ✓ |
| 2 | schemas/ | COMPLETO ✓ (9 schemas) |
| 3 | event_bus/ | COMPLETO ✓ |
| 4 | governance_engine/ | COMPLETO ✓ |
| 5 | memory_fabric/ | COMPLETO ✓ |
| 6 | session_scheduler/ | COMPLETO ✓ |
| 7 | runtimes/ | COMPLETO ✓ |
| 8 | observability/ | COMPLETO ✓ |
| 9 | agent_registry/ | COMPLETO ✓ |
| 10 | cognition/ | COMPLETO ✓ |

**Deuda técnica abierta:**
- `DT-COG-002`: `integration_test_cognition.py` — ALTA
- `DT-REG-001`: `sync_memory_to_redis()` en `agent_registry_v2.py` — MEDIA
- `IC-02` (V3): Duplicados TEST_SUITE en Drive — ALTA — requiere coordinador

> ⚠️ Este estado puede haber cambiado. Siempre leer el RELAY_POINTER real en Drive antes de asumir el estado.

---

## REGLAS DE CALIDAD

| Regla | Consecuencia si se viola |
|---|---|
| Nunca sobreescribir versiones anteriores | Detener, avisar, no guardar |
| Siempre registrar ALUMNO_ID y fecha en cada archivo | Sin firma = no válido |
| Solo cargar lo necesario para el relay activo | Economía de tokens |
| Drive siempre gana sobre lo que dice el relay | Documentar discrepancia |
| NUNCA Docker — solo Firecracker/NanoVMs/Unikraft | Violación arquitectural |
| NUNCA cerrar sin los 3 artefactos de cierre | Interrumpe trabajo de otros alumnos |
| NUNCA relay sin las 10 secciones | Relay inválido |
| NUNCA archivo sin encabezado firmado | Autoría perdida |
| Relay anterior sin firma → continuarlo antes de avanzar | No dejar trabajo incompleto flotando |

---

## NOTAS DE MIGRACIÓN V3 → MPAT4

El alumno que viene de V3 debe saber:

- En V3 el centro era archivos físicos por capas (CAPA_01 a CAPA_14).
- En MPAT4 el centro es la **Infraestructura Cognitiva**: contratos, eventos, runtime efímero, memoria soberana.
- **No existe migración por equivalencia directa** de carpetas V3 → V4.
- El orden inmutable por módulo es: Contrato → Schema → Implementación → Persistencia en Memory Fabric.
- Sin contrato aprobado, el sistema rechaza el deploy del componente.
- Los runtimes son efímeros: nacen, hidratan memoria, ejecutan, exportan relay, mueren. La memoria NO vive en el runtime.
