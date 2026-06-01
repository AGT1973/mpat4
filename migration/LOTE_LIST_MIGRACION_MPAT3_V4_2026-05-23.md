# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23  
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP  
**Fuente:** AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx  
**Regla MPAT4:** 1 archivo canónico por capa = `CAPA_NN_MASTER_V3_02.md` (o V3_01 si no hubo patch). Sin fragmentos, sin duplicados.

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRÍTICA | 🔴 PENDIENTE | — | — |
| LOTE_002 | 09 | CRÍTICA | 🔴 PENDIENTE | — | — |
| LOTE_003 | 06 | ALTA | 🟡 PENDIENTE | — | — |
| LOTE_004 | 00, 04 | MEDIA | 🟡 PENDIENTE | — | — |
| LOTE_005 | 01, 02, 03 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_006 | 05, 08 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_007 | 10, 11, 12 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_008 | 13, 14 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_009 | RAÍZ MPAT3 | MEDIA | 🟡 PENDIENTE | — | — |

---

## DETALLE POR LOTE

### LOTE_001 — CAPA 07 ⚠ MÁS FRAGMENTADA
**Prioridad:** CRÍTICA (9 archivos, 4 módulos funcionales sueltos)  
**Canónico destino:** `CAPA_07_MASTER_V3_02.md`  
**Acciones requeridas:**
1. Evaluar `RPC_HANDLER (37k)` → incorporar sección al MASTER o descartar
2. Evaluar `PAYMENT_DISPATCHER (40k)` → incorporar o descartar
3. Evaluar `MCP_APPS_RENDERER (27k)` → incorporar o descartar
4. Evaluar `PATCH_TOOL_REGISTRY` → incorporar o descartar
5. Mover `CAPA_07_V3_01 ×3` + `.old renombrado` → `trashcan/`
6. Confirmar `CAPA_07_V3_02` como canónico final en `/capas` MPAT4

---

### LOTE_002 — CAPA 09 ⚠ 8 VARIANTES
**Prioridad:** CRÍTICA (8 archivos, 5 copias del mismo contenido)  
**Canónico destino:** `CAPA_09_MASTER_V3_01_UNIFICADO.md`  
**Acciones requeridas:**
1. Confirmar `V3_01_UNIFICADO` como canónico
2. Evaluar `PATCH_FIREWALL_HTML (23k)` → incorporar o descartar
3. Mover `V3_01 ×4 copias` + `V3_02 ×2` + `.old` + `_DUP_1` → `trashcan/`

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
**Acciones requeridas:**
- **Capa 00:** Mover 5 archivos a `trashcan/` (MASTER original, V3_01, EXPANSION ×2, _DUP)
- **Capa 04:** Mover MASTER original + _DUP_1 (13 bytes) → `trashcan/`

---

### LOTE_005 — CAPAS 01, 02, 03
**Prioridad:** NORMAL  
**Canónicos destino:** `CAPA_0N_MASTER_V3_01.md` (versión saneada)  
**Acciones requeridas:**
- **Capa 01:** Unificar `frontera_capa1 ×2` al MASTER; MASTER original → `trashcan/`
- **Capa 02:** Evaluar `Investigación ×2` + `Evaluación`; MASTER original → `trashcan/`
- **Capa 03:** MASTER original → `trashcan/`; V3_01 más reciente = canónico

---

### LOTE_006 — CAPAS 05 y 08
**Prioridad:** NORMAL  
**Canónicos destino:** `CAPA_05_MASTER_V3_01.md` / `CAPA_08_MASTER_V3_01.md`  
**Acciones requeridas:**
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
- Tomar un solo lote a la vez por alumno (ver skill `relay-lifecycle`)
