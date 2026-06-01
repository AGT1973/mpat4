# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23
**Actualización:** 2026-05-24 — DT-LOTE003-01 CERRADA
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP
**Regla MPAT4:** 1 archivo canónico por capa = .md o código. NUNCA Google Docs como canónico.

**NOTA METODOLOGICA:** Las capas 04, 06, 07, 08, 09, 10, 14 fueron consolidadas
directamente desde los MASTERs canónicos sin informe intermedio. Los .md en /capas
de MPAT4 son los canónicos definitivos. Google Docs = fuente intermedia, nunca canónico.

---

## ESTADO DE LOTES

| Lote | Capas | Prioridad | Estado | Alumno | Fecha cierre |
|------|-------|-----------|--------|--------|--------------|
| LOTE_001 | 07 | CRÍTICA | ✅ CERRADO | docente | 2026-05-23 |
| LOTE_002 | 09 | CRÍTICA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_003 | 06 | ALTA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_004 | 00, 04 | MEDIA | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_005 | 01, 02, 03 | NORMAL | ✅ CERRADO | Claude Sonnet 4.6 | 2026-05-23 |
| LOTE_006 | 05, 08 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_007 | 10, 11, 12 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_008 | 13, 14 | NORMAL | ✅ CERRADO | claudeacc1011 | 2026-05-24 |
| LOTE_009 | RAÍZ MPAT3 | MEDIA | ✅ CERRADO | Claude Sonnet 4.6 | 2026-05-23 |

---

## ✅ MIGRACIÓN COMPLETA — TODOS LOS LOTES CERRADOS

---

## CANÓNICOS CONFIRMADOS POR CAPA

| Capa | Canónico .md | ID | Owner | Nota |
|---|---|---|---|---|
| CAPA_00 | CAPA_00_MASTER_V3_02.md | — | ariel | Ver LOTE_004 |
| CAPA_01 | CAPA_01_MASTER_V3_01_V4_migrado.md | 1DeC036KdIVxDz0VambwV59VT96gsGVIz | ai.mpat.designer | Ver LOTE_005 |
| CAPA_02 | CAPA_02 — pendiente consolidar en .md | 16HzSi4UXc7m61WpgqrojhIVNNXib_v2p | — | Solo encabezado; GDoc origen no es canónico |
| CAPA_03 | CAPA_03_MASTER_V3_02.md | 17SHUlTMHfUdQ_EOTFjhhJmgbmiqvMHe7 | ai.mpat.tech | Ver LOTE_005 |
| CAPA_04 | CAPA_04_MASTER_V3_02.md | — | ariel | Ver LOTE_004 |
| CAPA_05 | pendiente verificar ID | — | — | Ver DT-LOTE006-01 |
| CAPA_06 | CAPA_06_MASTER_V4_00.md | 1GAJOsjcOWDdy_zT1bo1OQJyou8kT_fKP | agt1973 | V4_00 migrado desde V3_02_FINAL ✅ |
| CAPA_07 | CAPA_07_MASTER_V3_02_FULL.md | 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf | — | Ver LOTE_001 |
| CAPA_08 | pendiente verificar ID | — | — | Ver DT-LOTE006-01 |
| CAPA_09 | CAPA_09_MASTER_V4_00.md | 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj | — | Ver LOTE_002 |
| CAPA_10 | CAPA_10_MASTER_V3_02.md | 1O4GHbDC4U71VxVtBCaTetOXkLpoigd-sqlt3G0_ZMaU | ariel | Ver LOTE_007 |
| CAPA_11 | pendiente verificar ID | — | — | Ver DT-LOTE007-01 |
| CAPA_12 | pendiente verificar ID | — | — | Ver DT-LOTE007-01 |
| CAPA_13 | pendiente verificar ID | — | — | Ver DT-LOTE008-01 |
| CAPA_14 | CAPA_14_MASTER_V3_02.md | 1doPbx0LcHFsUupt2KjBgAAQbMACs4KaC57khAAR9PLo | ariel | Ver LOTE_008 |

---

## DEUDAS TECNICAS

| ID | Descripción | Estado | Tipo |
|---|---|---|---|
| DT-LOTE002-01 | Verificar `inspect_html()` con 15 patrones XSS en CAPA_09_MASTER_V4_00.md | 🟡 ABIERTA | Verificación |
| DT-LOTE003-01 | Canónico CAPA_06: FINAL.md vs GDoc | ✅ CERRADA | Decisión |
| DT-LOTE005-01 | Integración SSEHandler + SemanticFirewall sin RES formal | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-02 | WebSocketHandler + unikernel destruido mid-session | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-03 | Planner sin RES formal asignada | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-04 | Sección eBPF ausente en CAPA_01 | 🟡 ABIERTA | Documentación |
| DT-LOTE005-05 | Python 3.14 No-GIL en CAPA_01 (asyncio + NHP) | 🟡 ABIERTA | Compatibilidad |
| DT-LOTE006-01 | Registrar IDs canónicos .md de CAPA_05 y CAPA_08 | 🟡 ABIERTA | Registro |
| DT-LOTE007-01 | Registrar IDs canónicos .md de CAPA_11 y CAPA_12 | 🟡 ABIERTA | Registro |
| DT-LOTE008-01 | Registrar ID canónico .md de CAPA_13 | 🟡 ABIERTA | Registro |
| DT-LOTE009-01 | Verificar que módulos MPAT4 referencian config_policy_V4_02.yaml | 🟡 ABIERTA | Verificación |

---

## DETALLE DT-LOTE003-01 — CERRADA 2026-05-24

**Pregunta original:** ¿CAPA_06_MASTER_V3_02_FINAL.md (21KB, cursos.agt) o Google Doc como canónico?

**Regla confirmada:** NUNCA Google Docs como canónico. Siempre .md o código.

**Cadena de producción reconstruida:**
1. `CAPA_06_MASTER_V3_02_UNIFICADO.md` (andrea.bio, 11KB, RELAY_033) — Fuente A
2. GDoc ariel (ID: 1gGJeIngFjv...) — Fuente B del merge (no es canónico)
3. `CAPA_06_MASTER_V3_02_FINAL.md` v1 (19.8KB, 22:17) — error en CAPA_01 vs CAPA_11
4. `CAPA_06_MASTER_V3_02_FINAL.md` v2 (21KB, 23:00, ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU) — corrección aplicada, canónico V3
5. `CAPA_06_MASTER_V4_00.md` (agt1973, 7.1KB, ID: 1GAJOsjcOWDdy_zT1bo1OQJyou8kT_fKP) — migración V4 desde el FINAL ✅

**Canónico V3:** CAPA_06_MASTER_V3_02_FINAL.md (ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU, 21KB)
**Canónico V4 (operacional):** CAPA_06_MASTER_V4_00.md (ID: 1GAJOsjcOWDdy_zT1bo1OQJyou8kT_fKP)

**Candidatos a trashcan (decisión docente):**
- CAPA_06_MASTER_V3_02_FINAL.md v1 con error (ID: 167QxyXHjXEzP-CrXWs5dJw6WWx4DCOg3, 19.8KB)
- CAPA_06_MASTER_V3_02_FINAL.md duplicado (ID: 1_o8Pidm9C8pa9urYrX-cQNqePO1UJU3L, 21KB, 22:56)
- GDoc ariel (ID: 1gGJeIngFjv-rbsFq4nPcUII-rHYwGckMuUiF6qkfA-U) — fue Fuente B, absorbido

**Diferencia clave entre el 5KB en /capas y el FINAL 21KB:**
El CAPA_06_MASTER_V3_02.md (5KB, ai.mpat.tech) en /capas es resumen condensado — útil para referencia rápida pero omite schema completo de GRPOState, QUICConnectionState, ECSManager, DbC extendido y resolución formal CAPA_01 vs CAPA_11. El FINAL (21KB) es la versión completa. El V4_00 (7.1KB) es la migración operacional.

---

## REGLA ACTUALIZADA — CANÓNICOS MPAT4

> NUNCA Google Docs como canónico de capa.
> El canónico es siempre el archivo .md más completo y reciente en /capas de MPAT4,
> o el archivo de código (.py, .yaml, .rs) en su módulo correspondiente.
> Los Google Docs son fuentes intermedias de trabajo — se absorben en el .md final.

---

## PENDIENTES PARA DECISIÓN DEL DOCENTE (actualizados)

1. **Trashcan CAPA_06:** confirmar mover a trashcan los 3 candidatos listados arriba.
2. **Análisis Comparativo duplicado** (ID: 1ppOtBRBgXLIynGpWcqhePCopW9ZKzw5h) — copia exacta del canónico. ¿Trashcan?
3. **config_policy V4_01 x2** — absorbidas por V4_02. ¿Trashcan?
4. **CAPA_02:** el encabezado actual apunta a un GDoc como origen. Según regla, necesita consolidarse en .md completo. ¿Se genera en próximo relay?

---
*Actualizado: 2026-05-24 — DT-LOTE003-01 CERRADA*
*Regla canónico confirmada: NUNCA GDoc — siempre .md o código*
*que has usado el formato de razonamiento adaptado por AGT*
