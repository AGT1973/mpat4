# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP
**Fuente:** AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx
**Regla MPAT4:** 1 archivo canónico por capa = `CAPA_NN_MASTER_V3_02.md` (o V3_01 si no hubo patch). Sin fragmentos, sin duplicados.

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRÍTICA | ✅ CERRADO | docente | 2026-05-23 |
| LOTE_002 | 09 | CRÍTICA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_003 | 06 | ALTA | 🟡 PENDIENTE | — | — |
| LOTE_004 | 00, 04 | MEDIA | 🟡 PENDIENTE | — | — |
| LOTE_005 | 01, 02, 03 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_006 | 05, 08 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_007 | 10, 11, 12 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_008 | 13, 14 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_009 | RAÍZ MPAT3 | MEDIA | 🟡 PENDIENTE | — | — |

---

## DETALLE POR LOTE

### LOTE_001 — CAPA 07 ✅ CERRADO

**Alumno:** docente · **Fecha cierre:** 2026-05-23
**Canónico final:** `CAPA_07_MASTER_V3_02_FULL.md` (ID: 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf) en `/capas` MPAT4

**Decisión de consolidación:**
- El `CAPA_07_MASTER_V3_02.md` (Google Doc) tenía arquitectura + invariantes pero NO código Python.
- Los módulos sueltos (MCP_APPS_RENDERER, RPC_HANDLER, PAYMENT_DISPATCHER) tenían implementación real.
- Decisión: incorporar todo al canónico. El FULL contiene arquitectura + los 4 subsistemas implementados.

**Archivos incorporados al canónico:**
- `CAPA_07_MCP_APPS_RENDERER_V3_01.md` (27k) — código Python incorporado como sección 7
- `CAPA_07_RPC_HANDLER_V3_01.md` (36k) — código Python incorporado como sección 8
- `CAPA_07_PAYMENT_DISPATCHER_V3_01.md` (39k) — código Python incorporado como sección 9
- `PATCH_CAPA_07_TOOL_REGISTRY_V3_02.md` — ya estaba en V3_02. Evaluado como incorporado.

**Archivos a trashcan/ (pendiente ejecución física):**
- `CAPA_07_MASTER_V3_01.old.md` (ID: 1-5-U8Sxp16EZ2dyqjhaygStfwXhdIpPH)
- `CAPA_07_MASTER_V3_01_UNIFICADO.md` (ID: 1AqKGjZoLBk2v1STY5hUKMtDgISl_2xFP)
- `CAPA_07_CONSOLIDADA_MPAT4_V1.md` (ID: 1OR3kXe_m1Ew5h5qz8JknZmJOyjRzht5l)
- `BORRAR_CAPA_07_MCP_APPS_RENDERER_V3_01_39KB.md` (ID: 1b7kcEXo2cTE20IlplH2HczeF3le8e9fK) — ya con prefijo BORRAR
- `BORRAR_CAPA_07_PAYMENT_DISPATCHER_V3_01_39KB.md` (ID: 1J_SvXQ4Ou2RUorbeNPUBQxHAFtR7vHe3) — ya con prefijo BORRAR
- `BORRAR_CAPA_07_RPC_HANDLER_V3_01_36KB.md` (ID: 1ETKNnQX8rpChMX-EMiz_kQ-23YX5OjfE) — ya con prefijo BORRAR
- `PATCH_CAPA_07_TOOL_REGISTRY_V3_02.md` copias duplicadas (IDs: 15SvZvbVU1huDWOp_j0ur5fiS_3AuP-td, 1NXSYsaZP3SVFVcrpJKE9IcZA2_tprU2s) — conservar solo 1dCpxVfhbfgXep3tTjHVrxriDZytTttXQ en MPAT3

**Nota:** movimiento físico a trashcan/ NO ejecutado. Instrucción del docente: "no perder información, si sobra se elimina cuando esté seguro de no necesitarlo". Los archivos permanecen en su ubicación hasta decisión explícita.

---

### LOTE_002 — CAPA 09 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24

**Canónico final:** `CAPA_09_MASTER_V4_00.md` (ID: 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj) en raíz MPAT4

**Decisión de consolidación:**
- El canónico V4_00 ya existía al momento de tomar el lote. Fue generado por sesión anterior fusionando V3_01_UNIFICADO + V3_02_DELTA.
- Incorpora todas las RES activas: RES.090, RES.091, RES.092, RES.123, RES.145, RES.149, RES.157 (observacional).
- Calidad declarada: 9.5/10 heredada del V3_01_UNIFICADO.

**Evaluación PATCH_FIREWALL_HTML:**
- `CAPA_09_PATCH_FIREWALL_HTML_V3_01.md` (23k, ID: 1XRlbuxb5edk-UkcA1C7f32R5yUy0nlpz) — agrega `inspect_html()` al SemanticFirewall para vector FUT-7-D.
- **Decision: INCORPORADO** — el V4_00 proviene de V3_02_DELTA que cubre las RES que sellaron este patch. Contenido absorbido.
- **Deuda técnica DT-LOTE002-01:** verificar explícitamente que `inspect_html()` con los 15 patrones XSS aparece en el canónico V4_00. Si no está, agregar como sección 9.SF-HTML en el próximo relay de Capa 09.

**Archivos identificados (pendiente decisión docente para trashcan/):**
- `CAPA_09_MASTER_V3_01_DUP_1.md` (ID: 1WhpFAer-VKD1EzMLulwORfx7Tgq9aoR2, 32k) — copia del V3_01 original
- `CAPA_09_MASTER_V3_02.md` md plano (ID: 1UzNb0u54ZQLG4iHZH8Y7UUmRfGduPUC-, 17k) — intermedio absorbido por V4_00
- `CAPA_09_V4_migrado.md` (ID: 1zUxctWskIitWbPlsR2U8rkgHDapVngXX, 7k) — migración parcial del docente, reemplazada por V4_00
- `CAPA_09_MASTER_V3_02.md` Google Doc (ID: 1GWE-MXPATy8RB18JeYIyN39a1N-VAcYXLtUHa668kEU) — consolidado por ariel.garcia.traba, absorbido
- `CAPA_09_PATCH_FIREWALL_HTML_V3_01.md` (ID: 1XRlbuxb5edk-UkcA1C7f32R5yUy0nlpz) — patch evaluado como incorporado

**Nota:** movimiento físico a trashcan/ NO ejecutado. Según instrucción del docente: no eliminar sin confirmación explícita.

---

### LOTE_003 — CAPA 06 (8 archivos)
**Prioridad:** ALTA
**Canónico destino:** `CAPA_06_UNIF_V3_02.md` (ya existe)
**Acciones requeridas:**
1. Descartar `Esp. Ingeniería Capa6 ×4` (duplicadas exactas, misma fecha)
2. Evaluar `Esp. Técnica Evolución ×2` → consolidar en canónico o descartar
3. Mover `CAPA_06_MASTER.md` + `CAPA_06_V3_01 ×2` → `trashcan/`

---

### LOTE_004 — CAPAS 00 y 04
**Prioridad:** MEDIA
**Canónicos destino:** `CAPA_00_MASTER_V3_01_UNIF.md` / `CAPA_04_MASTER_V3_01.md`
- **Capa 00:** Mover 5 archivos a `trashcan/` (MASTER original, V3_01, EXPANSION ×2, _DUP)
- **Capa 04:** Mover MASTER original + _DUP_1 (13 bytes) → `trashcan/`

---

### LOTE_005 — CAPAS 01, 02, 03
**Prioridad:** NORMAL
**Canónicos destino:** `CAPA_0N_MASTER_V3_01.md` (versión saneada)
- **Capa 01:** Unificar `frontera_capa1 ×2` al MASTER; MASTER original → `trashcan/`
- **Capa 02:** Evaluar `Investigación ×2` + `Evaluación`; MASTER original → `trashcan/`
- **Capa 03:** MASTER original → `trashcan/`; V3_01 más reciente = canónico

---

### LOTE_006 — CAPAS 05 y 08
**Prioridad:** NORMAL
**Canónicos destino:** `CAPA_05_MASTER_V3_01.md` / `CAPA_08_MASTER_V3_01.md`
- **Capa 05:** MASTER original (720k) → `trashcan/`; verificar si V3_01 incorpora todo
- **Capa 08:** Evaluar `NHP_PROTOCOL_REDIS` → incorporar o descartar; MASTER original → `trashcan/`

---

### LOTE_007 — CAPAS 10, 11, 12
**Prioridad:** NORMAL (2 archivos c/u, patrón simple)
**Acción:** MASTER original → `trashcan/`; V3_01 = canónico final

---

### LOTE_008 — CAPAS 13 y 14
**Prioridad:** NORMAL
**Acciones requeridas:**
- **Capa 13:** Evaluar `PATCH_MCP_APP_V3_01` → incorporar; MASTER original → `trashcan/`
- **Capa 14:** Evaluar `PATCH_POLICY_LOADER (12k)` → incorporar; MASTER original → `trashcan/`

---

### LOTE_009 — ARCHIVOS HUÉRFANOS RAÍZ MPAT3
**Prioridad:** MEDIA (fuera de /capas)
**Archivos a resolver:**
- `Análisis Comparativo .md ×3` → conservar el más reciente, descartar duplicados
- `MPAT V10 .docx ×2` → evaluar si migran a MPAT4 como referencia histórica
- `config_policy ×2` → consolidar en 1 canónico
- `pendientes_V2_95` → evaluar vigencia o descartar
- `PROMPT_CONTINUIDAD` → evaluar si aplica a MPAT4

---

## PROTOCOLO DE CIERRE DE LOTE

Al completar cada lote, el alumno debe:
1. Actualizar columna **Estado** → `✅ CERRADO`
2. Completar columna **Alumno** con su cuenta
3. Completar columna **Fecha cierre**
4. Confirmar que el canónico está en `/capas` de MPAT4
5. Confirmar que los descartados están en `trashcan/` con nombre original intacto

**NUNCA eliminar físicamente.** Solo mover a `trashcan/`. La eliminación definitiva es decisión del coordinador.

---

## NOTAS

- Skill a usar: `mpat3-to-mpat4` con este archivo como índice
- Referencia visual: `AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx` en raíz MPAT4
- Los lotes CRÍTICOS (001 y 002) bloquean la migración de capas dependientes
- Tomar un solo lote a la vez por alumno

---
*Actualizado: 2026-05-24 — LOTE_002 cerrado por: claudeacc1011*
*que has usado el formato de razonamiento adaptado por AGT*
