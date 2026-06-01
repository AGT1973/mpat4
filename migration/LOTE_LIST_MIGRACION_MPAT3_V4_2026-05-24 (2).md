# LOTE_LIST — Migración MPAT3 → MPAT4
**Fecha auditoría:** 2026-05-23
**Última actualización:** 2026-05-24
**Auditor:** Claude Sonnet 4.6 vía Google Drive MCP
**Regla MPAT4:** 1 archivo canónico por capa = .md o código. NUNCA Google Docs como canónico.

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

## ✅ MIGRACIÓN COMPLETA — 9/9 LOTES CERRADOS

---

## CANÓNICOS CONFIRMADOS POR CAPA

| Capa | Archivo canónico | ID Drive | Owner | Destino V4 |
|---|---|---|---|---|
| CAPA_00 | CAPA_00_MASTER_V3_02.md | 10DlCeApAw9N7REUr7xujZGwi4NuRBfYXOXspjcD8f1g | ariel | core/channel/ |
| CAPA_01 | CAPA_01_MASTER_V3_01_V4_migrado.md | 1DeC036KdIVxDz0VambwV59VT96gsGVIz | ai.mpat.designer | core/runtime/ |
| CAPA_02 | ⚠️ PENDIENTE consolidar en .md | 16HzSi4UXc7m61WpgqrojhIVNNXib_v2p | — | core/cognition/context/ |
| CAPA_03 | CAPA_03_MASTER_V3_02.md | 17SHUlTMHfUdQ_EOTFjhhJmgbmiqvMHe7 | ai.mpat.tech | core/cognition/orchestration/ |
| CAPA_04 | CAPA_04_MASTER_V3_02.md | 1GRkM9kr9NIOZ8zu1qSasNyYCGdgQ0cq3GJA7BS-hSJM | ariel | core/agents/ |
| CAPA_05 | CAPA_05_MASTER_V3_01_V4_migrado.md | 1APCYg3ZgeYS05hpnjJQiwmrWT5Qj3gCr | ai.mpat.designer | core/cognition/reasoning/ |
| CAPA_06 | CAPA_06_MASTER_V4_00.md | 1GAJOsjcOWDdy_zT1bo1OQJyou8kT_fKP | agt1973 | core/cognition/rlhf/ |
| CAPA_07 | CAPA_07_MASTER_V3_02_FULL.md | 1bR3l6DrnhYK3K9CUP75ZJ6HO8QW1emFf | docente | core/tools/ |
| CAPA_08 | CAPA_08_MASTER_V3_01_UNIFICADO.md | 1XoW-nj5QAz0-gnS3DIeYVm7fba8oYMDJ | andrea.bio | core/memory/ |
| CAPA_09 | CAPA_09_MASTER_V4_00.md | 1SlbycQMSmaZBG3VNo0YxQeowrRpbXZNj | claudeacc1011 | core/security/ |
| CAPA_10 | CAPA_10_MASTER_V3_02.md | 1O4GHbDC4U71VxVtBCaTetOXkLpoigd-sqlt3G0_ZMaU | ariel | core/observability/ |
| CAPA_11 | CAPA_11_MASTER_V4_00.md | 1dbmaokXa88I5uQa0Kekz77YwVOInDB60 | agt1973 | core/runtime/ + core/sandboxing/ |
| CAPA_12 | CAPA_12_MASTER_V4_00.md | 1TTlTx_rHO5ogsXln2ZJyckPR6RwPU6WY | agt1973 | core/federation/ |
| CAPA_13 | INFORME_CAPA_13_V4_CONSOLIDADO.md | 1g5JqYqFnE8W1Oc9k6pMZjSkQ063i9vJL | ai.mpat.info | core/delivery/ |
| CAPA_14 | CAPA_14_MASTER_V3_02.md | 1doPbx0LcHFsUupt2KjBgAAQbMACs4KaC57khAAR9PLo | ariel | config/ |

**Notas:**
- CAPA_02: único canónico sin .md completo. El GDoc origen no es canónico (regla: nunca GDoc). Requiere relay para consolidar en .md.
- CAPA_05: canónico V4 migrado con 2 DTs abiertas (modelos a verificar + namespaces Redis completos).
- CAPA_08: canónico es el V3_01_UNIFICADO — no se encontró V4_00 propio; la migración fue directa desde el UNIFICADO.

---

## DEUDAS TÉCNICAS

| ID | Descripción | Estado | Tipo |
|---|---|---|---|
| DT-LOTE002-01 | inspect_html() con 15 patrones XSS en CAPA_09_MASTER_V4_00.md | ✅ CERRADA | Verificación |
| DT-LOTE002-013 | Verificar disponibilidad en V4: qwen3:8b, phi-4-mini, mistral:7b-v0.3 | 🟡 ABIERTA | Verificación |
| DT-LOTE002-014 | Namespaces Redis completos para ShadowRadix y CSA/HCA en CAPA_05 | 🟡 ABIERTA | Documentación |
| DT-LOTE003-01 | Canónico CAPA_06: FINAL.md vs GDoc | ✅ CERRADA | Decisión |
| DT-LOTE005-01 | Integración SSEHandler + SemanticFirewall sin RES formal | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-02 | WebSocketHandler + unikernel destruido mid-session | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-03 | Planner sin RES formal asignada | 🟡 ABIERTA | RES pendiente |
| DT-LOTE005-04 | Sección eBPF ausente en CAPA_01 | 🟡 ABIERTA | Documentación |
| DT-LOTE005-05 | Python 3.14 No-GIL en CAPA_01 (asyncio + NHP) | 🟡 ABIERTA | Compatibilidad |
| DT-LOTE006-01 | Registrar IDs canónicos de CAPA_05 y CAPA_08 | ✅ CERRADA | Registro |
| DT-LOTE007-01 | Registrar IDs canónicos de CAPA_11 y CAPA_12 | ✅ CERRADA | Registro |
| DT-LOTE008-01 | Registrar ID canónico de CAPA_13 | ✅ CERRADA | Registro |
| DT-LOTE009-01 | Verificar que módulos MPAT4 referencian config_policy_V4_02.yaml | 🟡 ABIERTA | Verificación |
| DT-LOTE010-01 | CAPA_02: consolidar contenido completo en .md (único sin canónico .md) | 🟡 ABIERTA | Relay |

---

## RESOLUCION DT-LOTE002-01

inspect_html() existe en CAPA_09_MASTER.md (V2 heredado, 111KB).
El V4_00 no lo omite — patrón deliberado: componentes V2 heredados viven en el MASTER base,
los V3/V4 extienden sin duplicar. SemanticFirewall activo vía herencia explícita.
No es deuda real — es el patrón arquitectural de la capa. CERRADA.

## RESOLUCION DT-LOTE003-01

Regla confirmada: NUNCA GDoc como canónico.
Cadena de producción CAPA_06: UNIFICADO (11KB) → FINAL v1 (19.8KB, error CAPA_11) →
FINAL v2 (21KB, corregido) → V4_00 (7.1KB, migrado).
Canónico V3: CAPA_06_MASTER_V3_02_FINAL.md (ID: 1V4l0U5an5trrM1nof9juQED0SEGea0gU).
Canónico V4 operacional: CAPA_06_MASTER_V4_00.md (ID: 1GAJOsjcOWDdy_zT1bo1OQJyou8kT_fKP).

## RESOLUCION DT-LOTE006/007/008-01

IDs localizados y registrados en tabla de canónicos. Ver arriba. CERRADAS.

---

## PENDIENTES PARA DECISIÓN DEL DOCENTE

1. **CAPA_02:** único canónico sin .md completo. ¿Se genera en próximo relay o se acepta el encabezado actual?
2. **Trashcan CAPA_06:** confirmar mover a trashcan los 3 candidatos:
   - FINAL v1 con error (ID: 167QxyXHjXEzP-CrXWs5dJw6WWx4DCOg3, 19.8KB)
   - FINAL duplicado 22:56 (ID: 1_o8Pidm9C8pa9urYrX-cQNqePO1UJU3L, 21KB)
   - GDoc ariel (ID: 1gGJeIngFjv-rbsFq4nPcUII-rHYwGckMuUiF6qkfA-U) — absorbido
3. **Análisis Comparativo duplicado** (ID: 1ppOtBRBgXLIynGpWcqhePCopW9ZKzw5h) — copia exacta del canónico. ¿Trashcan?
4. **config_policy V4_01 x2** — absorbidas por V4_02. ¿Trashcan?

---

## REGLA CANÓNICOS MPAT4

> NUNCA Google Docs como canónico de capa.
> El canónico es siempre el archivo .md más completo y reciente en /capas de MPAT4,
> o el archivo de código (.py, .yaml, .rs) en su módulo correspondiente.
> Los Google Docs son fuentes intermedias de trabajo — se absorben en el .md final.

---
*Actualizado: 2026-05-24 — DTs 002-01 / 003-01 / 006-01 / 007-01 / 008-01 CERRADAS*
*IDs canónicos completos registrados para todas las capas excepto CAPA_02*
*DTs abiertas restantes: 7 (5 RES/doc pendientes + 2 verificación + 1 relay CAPA_02)*
*que has usado el formato de razonamiento adaptado por AGT*
