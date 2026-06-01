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
| LOTE_002 | 09 | CRÍTICA | ✅ CERRADO | cursos.agt@gmail.com | 2026-05-24 |
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
**Canónico final:** `CAPA_07_MASTER_V3_02_FULL.md` (ID: 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf) en `/capas/` MPAT4

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
- `BORRAR_CAPA_07_MCP_APPS_RENDERER_V3_01_39KB.md` (ID: 1b7kcEXo2cTE20IlplH2HczeF3le8e9fK)
- `BORRAR_CAPA_07_PAYMENT_DISPATCHER_V3_01_39KB.md` (ID: 1J_SvXQ4Ou2RUorbeNPUBQxHAFtR7vHe3)
- `BORRAR_CAPA_07_RPC_HANDLER_V3_01_36KB.md` (ID: 1ETKNnQX8rpChMX-EMiz_kQ-23YX5OjfE)

**Nota:** movimiento físico a trashcan/ NO ejecutado. Instrucción del docente: no borrar hasta estar seguro.

---

### LOTE_002 — CAPA 09 ✅ CERRADO

**Alumno:** cursos.agt@gmail.com · **Fecha cierre:** 2026-05-24
**Canónico final:** `CAPA_09_MASTER_V3_02_FINAL.md` (ID: 1kzOamGrWO1jWDGW99eCYA94bgt68JAA-) en `/capas/` MPAT4

**Decisión de consolidación:**
- El LOTE_LIST original decía canónico: V3_01_UNIFICADO. Fue creado antes de que existiera V3_02.
- Al auditar: existían V3_02 base (Google Doc ariel.garcia.traba) + V3_02_UNIFICADO (agt1973, adds QUIC-REF).
- El UNIFICADO era un wrapper (referenciaba el base, no era self-contained).
- PATCH_FIREWALL_HTML (23KB) resuelve DT-012-001 CRÍTICO, requerido por INV-7D-001 → INCORPORAR.
- Decisión: crear FINAL self-contained que incorpora base + QUIC-REF + §9.4-HTML.

**Archivos incorporados al canónico:**
- `CAPA_09_MASTER_V3_02.md` (Google Doc, ariel.garcia.traba) — base completa
- `CAPA_09_MASTER_V3_02_UNIFICADO.md` (agt1973) — §9.QUIC-REF + invariantes
- `CAPA_09_PATCH_FIREWALL_HTML_V3_01.md` (cursos.agt) — §9.4-HTML (DT-012-001)

**Archivos para trashcan/ (pendiente movimiento físico):**
- `CAPA_09_MASTER_V3_01.md` (ID: 1HGmuk3oskmZiLsV-9AnK-bOCBc1gZpwH) — superado
- `CAPA_09_MASTER_V3_02_DELTA.md` (ID: 1-5ZJOtvvgeOzXehs9yXGw8_sbgvd-IVP) — incorporado
- `CAPA_09_MASTER_V3_02_UNIFICADO.md` (ID: 1RK3HcOLFxTzN7jGMUYSHaEoZoYhHx7Iu) — superado por FINAL
- `CAPA_09_PATCH_FIREWALL_HTML_V3_01.md` (ID: 1FaLNQaju7a3-4PrISnina3ASi1zCivwc) — incorporado

**DTs abiertas heredadas al canónico:** DT-013-001/002/003/004 (SemanticFirewall HTML parser).

---

### LOTE_003 — CAPA 06 (8 archivos)
**Prioridad:** ALTA
**Canónico destino:** `CAPA_06_MASTER_V3_02_FINAL.md` (ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU) — YA EXISTE
**Acciones requeridas:**
1. Confirmar FINAL como canónico (merge A+B+INFORME ya ejecutado por cursos.agt@gmail.com · 2026-05-23)
2. Verificar que `Esp. Técnica Evolución ×2` quedaron incorporadas o descartadas
3. Mover `CAPA_06_MASTER.md` + `CAPA_06_V3_01 ×2` + `Esp. Ingeniería Capa6 ×4` → `trashcan/`

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
**Prioridad:** MEDIA (fuera de /capas/)
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
4. Agregar sección de detalle con: canónico final (ID), archivos incorporados, archivos para trashcan
5. Actualizar este LOTE_LIST en Drive

---

*LOTE_LIST_MIGRACION_MPAT3_V4.md · Actualizado por cursos.agt@gmail.com · 2026-05-24*
*LOTE_001: CERRADO (docente) · LOTE_002: CERRADO (cursos.agt) · LOTE_003..009: PENDIENTES*
*que has usado el formato de razonamiento adaptado por AGT*
