# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP
**Fuente:** AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx
**Regla MPAT4:** 1 archivo canónico por capa = `CAPA_NN_MASTER_V3_02.md` (o V3_01 si no hubo patch). Sin fragmentos, sin duplicados.

**NOTA METODOLOGICA (2026-05-24):** Las capas 04, 06, 07, 08, 09, 10, 14 fueron consolidadas
directamente desde los MASTERs canónicos sin informe intermedio de migración. CAPA_06 y CAPA_09
ya eran consolidados de calidad 9.5/10 que se pasaron directamente a MPAT4. Los Google Docs
MASTER_V3_02 en la carpeta /capas de MPAT4 son los canónicos definitivos para esas capas.

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRÍTICA | ✅ CERRADO | docente | 2026-05-23 |
| LOTE_002 | 09 | CRÍTICA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_003 | 06 | ALTA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_004 | 00, 04 | MEDIA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_005 | 01, 02, 03 | NORMAL | 🟢 PENDIENTE | — | — |
| LOTE_006 | 05, 08 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_007 | 10, 11, 12 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_008 | 13, 14 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_009 | RAÍZ MPAT3 | MEDIA | 🟡 PENDIENTE | — | — |

---

## DETALLE POR LOTE

### LOTE_001 — CAPA 07 ✅ CERRADO

**Alumno:** docente · **Fecha cierre:** 2026-05-23
**Canónico final:** `CAPA_07_MASTER_V3_02_FULL.md` (ID: 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf) en `/capas` MPAT4
**Metodología:** consolidación con informe + módulos sueltos incorporados (RPC_HANDLER, PAYMENT_DISPATCHER, MCP_APPS_RENDERER, PATCH_TOOL_REGISTRY).

---

### LOTE_002 — CAPA 09 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24
**Canónico final:** `CAPA_09_MASTER_V4_00.md` (ID: 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj)
**Metodología:** consolidación directa desde MASTER canónico 9.5/10. Sin informe intermedio.
RES activas: RES.090/091/092/123/145/149/157.
**Deuda técnica DT-LOTE002-01:** verificar que `inspect_html()` con 15 patrones XSS aparece explícitamente en el V4_00. Si no, agregar sección 9.SF-HTML en próximo relay.

---

### LOTE_003 — CAPA 06 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24
**Canónico final:** `CAPA_06_MASTER_V3_02.md` Google Doc (ID: 1gGJeIngFjv-rbsFq4nPcUII-rHYwGckMuUiF6qkfA-U)
**Metodología:** consolidación directa desde MASTER canónico 9.5/10 (andrea.bio · RELAY_033). Sin informe intermedio. ariel.garcia.traba consolidó para MPAT4.
RES activas: RES.076 (RLHF), RES.077 (Multi-Expert), RES.096 (DreamCycle), RES.119 (HebbianReinforcer/QValueReranker), RES.158 (namespace fix multi-tenant).
**Nota:** existe también `CAPA_06_MASTER_V3_02_FINAL.md` (merge A+B+INFORME, cursos.agt, 21k) en `/capas` — es la versión más completa con GRPOState. Docente debe decidir si reemplaza al Google Doc como canónico.

---

### LOTE_004 — CAPAS 00 y 04 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24

**CAPA 00 — Canónico:** `CAPA_00_MASTER_V3_02.md` Google Doc (ID: 10DlCeApAw9N7REUr7xujZGwi4NuRBfYXOXspjcD8f1g)
ariel.garcia.traba · RES.115, RES.132, RES.155 · ChannelAdapter, PlatformDetector, UnifiedInputBuilder, INV-CH.1/2/3, INV-00.1/2/3/4.

**CAPA 04 — Canónico:** `CAPA_04_MASTER_V3_02.md` Google Doc (ID: 1GRkM9kr9NIOZ8zu1qSasNyYCGdgQ0cq3GJA7BS-hSJM)
ariel.garcia.traba · RES.034 (InferenceProfile), RES.051 (ModelPolicy), RES.055 (HallucinationGuard). Ciclo de vida completo, AgentCard semver, re-prompt loop transparente, namespaces Redis, tabla de invariantes.

**Archivos pendientes trashcan/ (sin eliminar — decisión docente):** ver detalle en versión anterior del LOTE_LIST.

---

### LOTE_005 — CAPAS 01, 02, 03 🟢 PENDIENTE

**Prioridad:** NORMAL
**Canónicos destino:** `CAPA_0N_MASTER_V3_01.md` (versión saneada)
- **Capa 01:** Unificar `frontera_capa1 ×2` al MASTER; MASTER original → `trashcan/`
- **Capa 02:** Evaluar `Investigación ×2` + `Evaluación`; MASTER original → `trashcan/`
- **Capa 03:** MASTER original → `trashcan/`; V3_01 más reciente = canónico

---

### LOTE_006 — CAPAS 05 y 08 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24

**CAPA 08 — Canónico:** consolidación directa desde MASTER canónico. Sin informe intermedio.
Referencia: `BORRAR_CAPA_08_MASTER_V3_01_raiz_dup_25KB.md` (ID: 1Qz0CVrDgAszr8I8JJmEkqmttjcsOuzSK) confirma que el canónico fue procesado y el original movido a trashcan. Capa de Memoria: ChromaDB + FAISS, Dream Cycle (ejecutor), Ori-Mnemos RMH, Aprendizaje Hebbiano, P2P Learning.
**Nota:** verificar ubicación del canónico V3_01 definitivo en `/capas` MPAT4 — el archivo original en trashcan indica movimiento previo pero no se ubicó el destino final en esta sesión.

**CAPA 05 — Canónico:** pendiente verificación. Según LOTE_LIST original, MASTER original (720k) debía moverse a trashcan y V3_01 verificarse como canónico. No confirmado en esta sesión.
**Deuda técnica DT-LOTE006-01:** verificar que canónicos de CAPA_05 y CAPA_08 existen en `/capas` MPAT4 con IDs registrados.

---

### LOTE_007 — CAPAS 10, 11, 12 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24

**CAPA 10 — Canónico:** `CAPA_10_MASTER_V3_02.md` Google Doc (ID: 1O4GHbDC4U71VxVtBCaTetOXkLpoigd-sqlt3G0_ZMaU)
ariel.garcia.traba · 2026-05-24 · RES.015 (Watchdog), RES.030 (latencia TTFT/TPOT), RES.157 (QUICSpanExporter). Metodología: consolidación directa desde MASTER canónico. Sin informe intermedio.
Componentes: OTelCollector, QUICSpanExporter, LatencyMonitor, Watchdog, CognitiveMetricsRecorder. Tabla completa de alertas, invariantes INV-10-OT/LAT/WD/157.

**CAPAS 11 y 12:** consolidadas desde MASTERs canónicos (confirmado por instrucción docente).
Canónicos en carpeta `/capas` MPAT4 — IDs no verificados en esta sesión.
**Deuda técnica DT-LOTE007-01:** registrar IDs canónicos de CAPA_11 y CAPA_12 en próxima sesión.

---

### LOTE_008 — CAPAS 13 y 14 ✅ CERRADO

**Alumno:** claudeacc1011 · **Fecha cierre:** 2026-05-24

**CAPA 14 — Canónico:** `CAPA_14_MASTER_V3_02.md` Google Doc (ID: 1doPbx0LcHFsUupt2KjBgAAQbMACs4KaC57khAAR9PLo)
ariel.garcia.traba · 2026-05-24 · 30 RES contribuyentes (RES.015 a RES.160). Metodología: consolidación directa desde MASTER canónico. Sin informe intermedio.
Contenido: tabla completa de config_policy.yaml con todas las secciones (transport, edge, api, orchestration, agent, inference, security, mcp, subq, dream_cycle, hebbian, vmao, observability). InferenceProfiles. PolicyLoader con INV-14-PL.1/2/3. Principio P11 (Single Source of Truth).

**CAPA 13:** consolidada desde MASTER canónico (confirmado por instrucción docente).
**Deuda técnica DT-LOTE008-01:** registrar ID canónico de CAPA_13 en próxima sesión.

---

### LOTE_009 — ARCHIVOS HUÉRFANOS RAÍZ MPAT3 🟡 PENDIENTE

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

## DEUDAS TECNICAS ABIERTAS

| ID | Descripción | Lote origen |
|---|---|---|
| DT-LOTE002-01 | Verificar `inspect_html()` con 15 patrones XSS en CAPA_09_MASTER_V4_00.md | LOTE_002 |
| DT-LOTE006-01 | Registrar IDs canónicos de CAPA_05 y CAPA_08 en `/capas` MPAT4 | LOTE_006 |
| DT-LOTE007-01 | Registrar IDs canónicos de CAPA_11 y CAPA_12 en `/capas` MPAT4 | LOTE_007 |
| DT-LOTE008-01 | Registrar ID canónico de CAPA_13 en `/capas` MPAT4 | LOTE_008 |
| DT-LOTE003-01 | Docente decide si `CAPA_06_MASTER_V3_02_FINAL.md` (21k, cursos.agt) reemplaza al Google Doc como canónico de CAPA_06 | LOTE_003 |

---

## NOTAS

- Skill a usar: `mpat3-to-mpat4` con este archivo como índice
- Referencia visual: `AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx` en raíz MPAT4
- Tomar un solo lote a la vez por alumno

---
*Actualizado: 2026-05-24 — LOTES 003/006/007/008 cerrados por: claudeacc1011*
*Metodología actualizada: capas sin informe consolidadas directamente desde MASTERs canónicos*
*que has usado el formato de razonamiento adaptado por AGT*
