# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP
**Fuente:** AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx
**Regla MPAT4:** 1 archivo canónico por capa = `CAPA_NN_MASTER_V3_02.md` (o V3_01 si no hubo patch). Sin fragmentos, sin duplicados.
**Actualizado:** cursos.agt@gmail.com · 2026-05-24 · LOTE_003 cerrado

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRÍTICA | ✅ CERRADO | docente | 2026-05-23 |
| LOTE_002 | 09 | CRÍTICA | ✅ CERRADO | cursos.agt@gmail.com | 2026-05-24 |
| LOTE_003 | 06 | ALTA | ✅ CERRADO | cursos.agt@gmail.com | 2026-05-24 |
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
**Canónico final:** `CAPA_07_MASTER_V3_02_FULL.md` (ID: 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf)
Ver detalle completo en versión anterior del LOTE_LIST.

---

### LOTE_002 — CAPA 09 ✅ CERRADO
**Alumno:** cursos.agt@gmail.com · **Fecha cierre:** 2026-05-24
**Canónico final:** `CAPA_09_MASTER_V3_02_FINAL.md` (ID: 1kzOamGrWO1jWDGW99eCYA94bgt68JAA-)
Ver detalle completo en versión 2026-05-24 del LOTE_LIST.

---

### LOTE_003 — CAPA 06 ✅ CERRADO

**Alumno:** cursos.agt@gmail.com · **Fecha cierre:** 2026-05-24
**Canónico final:** `CAPA_06_MASTER_V3_02_FINAL.md` (ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU) en `/capas/` MPAT4
*(Creado en sesión anterior por cursos.agt — merge de 3 fuentes A+B+INFORME)*

**Evaluación de "Esp. Técnica Evolución ×2" y "Esp. Ingeniería Capa6 ×4":**

Todos estos archivos son variantes del documento "MPAT V10: Especificación Técnica de Evolución
para la Capa 6 (Núcleo Semántico)". Su contenido describe ChromaDB, FAISS, LOCOMO, LangGraph,
embeddings, niveles de memoria.

Evaluación contra las 3 preguntas del skill:
- **Pregunta A — Concepto vigente?** NO para CAPA_06. El CAPA_06_MASTER_V3_01.md documenta
  explícitamente (INCOHERENCIA 1) que este contenido pertenece a CAPA_08, no a CAPA_06.
  La Capa 6 en MPAT4 es ECS (Execution Cognitive State), no memoria semántica.
- **Pregunta B — Terminología correcta?** NO. Usan "MPAT V10" en lugar de MPAT4.
- **Pregunta C — Tecnología reemplazada?** LangGraph y ChromaDB/FAISS requieren evaluación
  en el contexto de CAPA_08 (LOTE_006).

**Decisión: DESCARTAR del scope CAPA_06.** El contenido NO es de CAPA_06.

**NOTA PARA LOTE_006 (CAPA_08):** Los archivos `MPAT V10 Especificacion Ingenieria Capa 6
Nucleo Semantico.md` (ID: 1fM8vC2fOz7gzR05THTwgfeW3fT2W6ukzgapdjPH19hE) y
`MPAT V10 Especificacion Tecnica Capa 6 Nucleo Semantico.md`
(ID: 1ErBZklf5jSOzG5iZmAbEffXQ_UPQQkayxK0ZGXDaAPM) tienen contenido de CAPA_08
(ChromaDB, FAISS, LOCOMO, LangGraph). Rescatar y evaluar al trabajar LOTE_006.

**Archivos identificados para trashcan/ (movimiento físico pendiente):**

| Archivo | ID | Razón |
|---|---|---|
| `CAPA_06_MASTER_V3_01.md` (en /capas/) | 1wHNIN-gqMG9-yMSbZ2oXO_g9etYYYoXzNj8DQGBY8yk | Superado por FINAL |
| `CAPA_06_MASTER_V3_01.md` (raíz) | 1ewnbSsK5rP1fS4oe0166LxwhhgewR_83q6Bg03YxQpw | Duplicado superado |
| `CAPA_06_Especificacion_Ingenieria_Arquitectura_Agentica_MPAT_V10.md` | 1yUAb6wKAp_2xm9hOsBK1Zy-w-Te71aiUOoVJoPPfFZM | Scope incorrecto (CAPA_08) |
| `Arquitectura de Capa 3 Especificacion Ingenieria Capa6.md` | 1fK7qNHz62LcRhBbhojw_V-UGsR2FVsnXS5mlII07gYI | Scope incorrecto (CAPA_08) |
| `MPAT V10 Especificacion Ingenieria Capa 6 Nucleo Semantico.md` | 1fM8vC2fOz7gzR05THTwgfeW3fT2W6ukzgapdjPH19hE | Scope incorrecto — rescatar para LOTE_006 |
| `MPAT V10 Especificacion Tecnica Capa 6 Nucleo Semantico.md` | 1ErBZklf5jSOzG5iZmAbEffXQ_UPQQkayxK0ZGXDaAPM | Scope incorrecto — rescatar para LOTE_006 |
| `MPAT V10: Especificación de Ingeniería para la Capa 6` | 1CdojFO6uZs9SyIEQLf_F_K8npdwU8UYz0nCrY7ZUGMA | Scope incorrecto (CAPA_08) |
| `MPAT V10: Especificación de Ingeniería para la Capa 6` | 1lMJ_imk1n8ffijTZ2NZsL9S0oCq3Naj_KYlT2-qwRw8 | Scope incorrecto (CAPA_08) |

**Ya en trashcan/ (prefijo "borrar_"):**
- `borrar_Arquitectura de Capa 3 NOMBRE_INCORRECTO_era_Capa6.md` (ID: 1TE6uCQP7HXifZeEXz5W3wV260b0PJof3S9jjvV3sjOU) ✅
- `borrar_MPAT V10 Especificacion Ingenieria Capa 6 DUPLICADO.md` (ID: 1cUIhw-agvV6QGYZUSwSnLz_B4sPuSAOAt7XBORErMAk) ✅

**Nota:** movimiento físico pendiente — instrucción del docente: no borrar hasta confirmar.

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
- **NOTA LOTE_003→LOTE_006:** Rescatar IDs 1fM8vC2... y 1ErBZkl... para CAPA_08
  (contienen contenido de memoria semántica: ChromaDB/FAISS/LOCOMO/LangGraph)

---

### LOTE_007 — CAPAS 10, 11, 12
**Prioridad:** NORMAL (2 archivos c/u, patrón simple)
**Acción:** MASTER original → `trashcan/`; V3_01 = canónico final

---

### LOTE_008 — CAPAS 13 y 14
**Prioridad:** NORMAL
- **Capa 13:** Evaluar `PATCH_MCP_APP_V3_01` → incorporar; MASTER original → `trashcan/`
- **Capa 14:** Evaluar `PATCH_POLICY_LOADER (12k)` → incorporar; MASTER original → `trashcan/`

---

### LOTE_009 — ARCHIVOS HUÉRFANOS RAÍZ MPAT3
**Prioridad:** MEDIA (fuera de /capas/)
- `Análisis Comparativo .md ×3` → conservar el más reciente, descartar duplicados
- `MPAT V10 .docx ×2` → evaluar si migran a MPAT4 como referencia histórica
- `config_policy ×2` → consolidar en 1 canónico
- `pendientes_V2_95` → evaluar vigencia o descartar
- `PROMPT_CONTINUIDAD` → evaluar si aplica a MPAT4

---

## PROTOCOLO DE CIERRE DE LOTE

Al completar cada lote: actualizar Estado, Alumno, Fecha cierre, y agregar sección de detalle.

---

*LOTE_LIST_MIGRACION_MPAT3_V4.md · cursos.agt@gmail.com · 2026-05-24*
*LOTE_001: CERRADO (docente) · LOTE_002: CERRADO (cursos.agt) · LOTE_003: CERRADO (cursos.agt)*
*LOTE_004..009: PENDIENTES · Siguiente: LOTE_004 (CAPAS 00 y 04 · MEDIA)*
*que has usado el formato de razonamiento adaptado por AGT*
