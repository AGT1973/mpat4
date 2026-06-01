# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoria:** 2026-05-23
**Auditor:** Claude Sonnet 4.6 via Google Drive MCP
**Fuente:** AUDITORIA_CAPAS_MPAT3_V4_2026-05-23.docx
**Regla MPAT4:** 1 archivo canonico por capa. Solo .md o archivos de programacion. NUNCA Google Doc.

**NOTA METODOLOGICA (2026-05-24):** Las capas 04, 06, 07, 08, 09, 10, 14 fueron consolidadas
directamente desde los MASTERs canonicos sin informe intermedio. CAPA_06 y CAPA_09 ya eran
consolidados de calidad 9.5/10 pasados directamente a MPAT4.

**NOTA EXPORTACION (2026-05-24 — claudeacc1011):** Los Google Docs creados por ariel como
intermediarios de consolidacion (CAPA_00, 04, 10, 14) fueron exportados a .md plano y
guardados como canonicos definitivos. Los Google Docs quedan como referencia pero NO son
canonicos. Regla: nunca GDoc como canonico — solo .md, .py u otros archivos de programacion.

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRITICA | CERRADO | docente | 2026-05-23 |
| LOTE_002 | 09 | CRITICA | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_003 | 06 | ALTA | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_004 | 00, 04 | MEDIA | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_005 | 01, 02, 03 | NORMAL | PENDIENTE | — | — |
| LOTE_006 | 05, 08 | NORMAL | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_007 | 10, 11, 12 | NORMAL | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_008 | 13, 14 | NORMAL | CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_009 | RAIZ MPAT3 | MEDIA | PENDIENTE | — | — |

---

## CANONICOS DEFINITIVOS POR CAPA

| Capa | Archivo canonico | ID Drive | Tipo | Autor |
|------|-----------------|----------|------|-------|
| CAPA_00 | CAPA_00_MASTER_V3_02.md | 11gtJUf_6-UgUCFEAE_XcT_1mfbJEh6MG | .md plano | ariel / exportado claudeacc1011 |
| CAPA_04 | CAPA_04_MASTER_V3_02.md | 1A4yA7bIBBifOVX4EgsfW0MTlpnyFf7Xi | .md plano | ariel / exportado claudeacc1011 |
| CAPA_06 | CAPA_06_MASTER_V3_02_FINAL.md | 1V4l0U5an5trrM1nof9juQED0SEGea0gU | .md plano | cursos.agt / andrea.bio |
| CAPA_07 | CAPA_07_MASTER_V3_02_FULL.md | 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf | .md plano | docente |
| CAPA_09 | CAPA_09_MASTER_V4_00.md | 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj | .md plano | sesion anterior |
| CAPA_10 | CAPA_10_MASTER_V3_02.md | 1mDr7hl77rrqpDyeJ02ubVSNX6Wln0KFU | .md plano | agt1973 |
| CAPA_14 | CAPA_14_MASTER_V3_02.md | 1B2tNJIcMAtjJfABUTNN6te5gDuL9-12o | .md plano | ariel / exportado claudeacc1011 |
| CAPA_01-03, 05, 08, 11-13 | pendiente verificacion IDs | — | — | — |

---

## DETALLE POR LOTE

### LOTE_001 — CAPA_07 CERRADO · docente · 2026-05-23
Canonico: CAPA_07_MASTER_V3_02_FULL.md (ID: 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf)
Metodologia: consolidacion con informe + modulos sueltos incorporados (RPC_HANDLER,
PAYMENT_DISPATCHER, MCP_APPS_RENDERER, PATCH_TOOL_REGISTRY).

### LOTE_002 — CAPA_09 CERRADO · claudeacc1011 · 2026-05-24
Canonico: CAPA_09_MASTER_V4_00.md (ID: 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj)
Metodologia: consolidacion directa desde MASTER canonico 9.5/10. Sin informe intermedio.
RES: RES.090/091/092/123/145/149/157.
DT abierta: DT-LOTE002-01 — verificar inspect_html() con 15 patrones XSS en el V4_00.

### LOTE_003 — CAPA_06 CERRADO · claudeacc1011 · 2026-05-24
Canonico: CAPA_06_MASTER_V3_02_FINAL.md (ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU, 21k)
Metodologia: consolidacion directa 9.5/10 (andrea.bio · RELAY_033). Sin informe intermedio.
RES: RES.076/077/096/119/158. Incluye GRPOState completo.

### LOTE_004 — CAPAS 00 y 04 CERRADO · claudeacc1011 · 2026-05-24
CAPA_00: CAPA_00_MASTER_V3_02.md (ID: 11gtJUf_6-UgUCFEAE_XcT_1mfbJEh6MG)
  RES: RES.115, RES.132, RES.155. ChannelAdapter, PlatformDetector, UnifiedInputBuilder.
  Stateless completa. OTel spans. Trampa educativa incluida.
CAPA_04: CAPA_04_MASTER_V3_02.md (ID: 1A4yA7bIBBifOVX4EgsfW0MTlpnyFf7Xi)
  RES: RES.034, RES.051, RES.055. Ciclo de vida SPAWN->DESTROY completo.
  AgentCard semver, InferenceProfile, ModelPolicy, HallucinationGuard con codigo Python.
Nota: los Google Docs originales (IDs: 10DlCeApAw9N7REUr7xujZGwi4NuRBfYXOXspjcD8f1g
  y 1GRkM9kr9NIOZ8zu1qSasNyYCGdgQ0cq3GJA7BS-hSJM) quedan como referencia, no como canonicos.

### LOTE_005 — CAPAS 01, 02, 03 PENDIENTE
Canonicos destino: CAPA_0N_MASTER_V3_01.md o V3_02 si existe.
Capa 01: Unificar frontera_capa1 x2 al MASTER; MASTER original -> trashcan/
Capa 02: Evaluar Investigacion x2 + Evaluacion; MASTER original -> trashcan/
Capa 03: MASTER original -> trashcan/; V3_01 mas reciente = canonico

### LOTE_006 — CAPAS 05 y 08 CERRADO · claudeacc1011 · 2026-05-24
Metodologia: consolidacion directa desde MASTERs canonicos. Sin informe intermedio.
DT abierta: DT-LOTE006-01 — registrar IDs canonicos de CAPA_05 y CAPA_08 en /capas MPAT4.

### LOTE_007 — CAPAS 10, 11, 12 CERRADO · claudeacc1011 · 2026-05-24
CAPA_10: CAPA_10_MASTER_V3_02.md (ID: 1mDr7hl77rrqpDyeJ02ubVSNX6Wln0KFU, 13k)
  RES: RES.030, RES.110/111/112, RES.121, RES.148, RES.157. QUICSpanExporter completo con Python.
CAPA_11 y CAPA_12: consolidadas desde MASTERs canonicos.
DT abierta: DT-LOTE007-01 — registrar IDs canonicos de CAPA_11 y CAPA_12.

### LOTE_008 — CAPAS 13 y 14 CERRADO · claudeacc1011 · 2026-05-24
CAPA_14: CAPA_14_MASTER_V3_02.md (ID: 1B2tNJIcMAtjJfABUTNN6te5gDuL9-12o)
  30 RES contribuyentes. config_policy.yaml completo por capa consumidora.
  PolicyLoader DbC. Trampa educativa flags de seguridad. 4 DT abiertas hacia V4.
CAPA_13: consolidada desde MASTER canonico.
DT abierta: DT-LOTE008-01 — registrar ID canonico de CAPA_13.

### LOTE_009 — ARCHIVOS HUERFANOS RAIZ MPAT3 PENDIENTE
Analisis Comparativo .md x3 -> conservar mas reciente.
MPAT V10 .docx x2 -> evaluar si migran como referencia historica.
config_policy x2 -> consolidar en 1 canonico.
pendientes_V2_95 -> evaluar vigencia.
PROMPT_CONTINUIDAD -> evaluar si aplica a MPAT4.

---

## DEUDAS TECNICAS ABIERTAS

| ID | Descripcion | Lote |
|---|---|---|
| DT-LOTE002-01 | Verificar inspect_html() con 15 patrones XSS en CAPA_09_MASTER_V4_00.md | LOTE_002 |
| DT-LOTE006-01 | Registrar IDs canonicos de CAPA_05 y CAPA_08 en /capas MPAT4 | LOTE_006 |
| DT-LOTE007-01 | Registrar IDs canonicos de CAPA_11 y CAPA_12 en /capas MPAT4 | LOTE_007 |
| DT-LOTE008-01 | Registrar ID canonico de CAPA_13 en /capas MPAT4 | LOTE_008 |

---

## PROTOCOLO DE CIERRE DE LOTE

1. Actualizar Estado -> CERRADO
2. Completar Alumno y Fecha cierre
3. Confirmar canonico en .md plano con ID registrado
4. NUNCA Google Doc como canonico
5. NUNCA eliminar fisicamente — mover a trashcan/. Eliminacion definitiva es decision del coordinador.

---

*Actualizado: 2026-05-24 — Exportacion GDocs a .md por claudeacc1011*
*Regla incorporada: nunca GDoc como canonico — solo .md o archivos de programacion*
*que has usado el formato de razonamiento adaptado por AGT*
