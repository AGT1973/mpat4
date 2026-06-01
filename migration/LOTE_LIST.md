# LOTE_LIST — Migración MPAT3 → MPAT4
## Versión: 1_00 · Docente: agt1973@gmail.com · Fecha: 2026-05-23
## Basado en: AUDITORIA_TOTAL_MPAT3_PARA_V4_2026-05-22.md (ID: 1BdPgi3q8BUzUBRp4VMMDJeEUT2NMayFT)

---

## ANTES DE TOMAR UN LOTE — LEER ESTO

La migración no es copia. Cada archivo se evalúa con tres preguntas:
1. ¿El concepto sigue vigente en V4?
2. ¿La terminología es correcta (sin Docker, sin V3, sin referencias obsoletas)?
3. ¿La tecnología fue reemplazada?

Ver tabla completa de traducción V3→V4 en el skill `mpat3-to-mpat4`.

**Regla de tokens:**
- ALTA → solo tomar si tokens > 70%
- MEDIA → tomar si tokens > 50%
- BAJA → tomar si tokens > 35%
- Menos de 35% → NO tomar lote nuevo. Solo documentar y cerrar.

---

## TABLA DE LOTES

| LOTE_ID | DESCRIPCIÓN | CARPETA FUENTE (MPAT3) | CARPETA DESTINO (MPAT4) | COMPLEJIDAD | ARCHIVOS EST. | PRIORIDAD |
|---|---|---|---|---|---|---|
| LOTE_001 | Arquitectura base | `arquitectura/` | `contracts/` + `docs/public/` | ALTA | ~8 | 1 |
| LOTE_002 | Capas 01–05 | `capas/` (CAPA_01 a CAPA_05) | `core/cognition/` según capa | ALTA | ~5 + variantes | 2 |
| LOTE_003 | Capas 06–10 + CAPA_08 referencia | `capas/` (CAPA_06 a CAPA_10) | `core/cognition/` según capa | ALTA | ~5 + variantes | 3 |
| LOTE_004 | Capas 11–14 + DT-016-001 | `capas/` (CAPA_11 a CAPA_14) | `core/cognition/` según capa | MEDIA | ~4 + variantes | 4 |
| LOTE_005 | Resoluciones V3_02 | `resoluciones/` | `resoluciones/` | MEDIA | ~5 canónicos | 5 |
| LOTE_006 | Investigaciones P01–P75 | `investigaciones/PENDIENTES_MPAT_2026/` | `research/` según tema | BAJA | ~75 | 6 |
| LOTE_007 | Estado y documentos de cierre | `estado/` + raíz MPAT3 | `system_state/` + `docs/public/` | BAJA | ~6 | 7 |
| LOTE_008 | Relay histórico R001–R035 | `zzz_relay/` + `zzz_proximo_relay/` | `relay/` (solo lectura archivado) | BAJA | ~10 canónicos | 8 |

---

## DETALLE POR LOTE

### LOTE_001 — Arquitectura base
**Canónico principal:** `ARQUITECTURA_base_V3_02_INC03.md` (ID: 1peMlToJcdcrU3qFga3sSaCqQjQHMvnis)
**Archivos a evaluar:**
- `ARQUITECTURA_base_V3_02_INC03.md` → MIGRAR ADAPTADO (actualizar a terminología V4)
- `ARQUITECTURA_base_V3_03.md` → MIGRAR ADAPTADO (base para V4)
- `ARQUITECTURA_pendientes_V3_03.md` → MIGRAR (pendientes heredados)
- `ARQUITECTURA_system_V3_03.md` → MIGRAR ADAPTADO (actualizar topología a V4)
- `contrato_formal_ejecucion.md` → MIGRAR ADAPTADO (actualizar contratos)
- Duplicados → DESCARTAR (ver audit para lista de duplicados)

**Adaptaciones obligatorias:**
- Docker → NanoVMs/Firecracker/Unikraft
- Python 3.11/3.12 → Python 3.14 No-GIL
- Agregar Rust como lenguaje de producción para hot paths
- Pydantic V2 → Pydantic V3

---

### LOTE_002 — Capas 01–05
**Canónicos:** archivos `CAPA_0X_MASTER_V3_01.md` en `capas/`
**Destino en MPAT4 por capa:**

| Capa | Descripción | Destino MPAT4 |
|---|---|---|
| CAPA_01 | API Gateway / QUICGateway + eBPF | `core/runtime/` |
| CAPA_02 | Preprocessing / FastAPI / SSE / WebSocket | `core/cognition/context/` |
| CAPA_03 | Orchestrator / Scheduler No-GIL / MAS | `core/cognition/orchestration/` |
| CAPA_04 | Motor de Agentes / A2A / Audio Kernel | `core/cognition/agents/` |
| CAPA_05 | Motor de Inferencia / ModelRouter | `core/cognition/reasoning/` |

**Nota CAPA_02:** FastAPI 0.115+ requerido — mencionar en deuda técnica.

---

### LOTE_003 — Capas 06–10
**Canónicos:** archivos `CAPA_0X_MASTER_V3_01.md` o `_UNIFICADO` en `capas/`

| Capa | Descripción | Destino MPAT4 |
|---|---|---|
| CAPA_06 | Estado Cognitivo / RLHF / Multi-Expert | `core/cognition/kernel/` |
| CAPA_07 | MCP 2.0 / ToolRegistry / Skill Validation | `core/cognition/agents/` |
| CAPA_08 | Dream Cycle / Hebbiano / RMH — **REFERENCIA 10/10** | `core/memory/` — MIGRAR INTACTO |
| CAPA_09 | NHP Protocol / ZeroTrustSession / ASL-3 | `core/sandboxing/` |
| CAPA_10 | Monitoring / OTel / LongContext / NVFP4 | `core/observability/` |

**CAPA_08 es el template de calidad 10/10. No modificar. Cada capa migrada se contrasta contra este estándar.**

---

### LOTE_004 — Capas 11–14
**Incluye DT-016-001** (cubierta por RES.160 — implementar en relay posterior a RELAY_005)

| Capa | Descripción | Destino MPAT4 |
|---|---|---|
| CAPA_11 | Unikernel-per-Tenant / SubQ | `core/runtime/` + `core/sandboxing/` |
| CAPA_12 | Multi-tenant / A2A v1.0 / VMAO | `core/federation/` |
| CAPA_13 | Delivery Layer A2A / SubQ / UnikerGuard | `core/execution_graph/` |
| CAPA_14 | policy.yaml / PolicyLoader / PolicyContract | `core/governance/` |

**Nota CAPA_14:** PolicyContract → V4 con TenantContext obligatorio.

---

### LOTE_005 — Resoluciones
**Canónico:** `INDICE_SEMANTICO_RES113_RES160_V3_02.md` (ID: 1xmGZWdzuznz4l5TByFUVMNy5SjwvPKHX)
**Destino:** `resoluciones/` en MPAT4
**Las RES migran como referencia inmutable.** No se editan. Se agregan en V4 desde RES.161 en adelante.
**RES.139 NUNCA se reasigna.**

---

### LOTE_006 — Investigaciones (BLOQUEADO hasta subida P11–P75)
**Prerequisito:** subir archivos P11–P75 a `investigaciones/PENDIENTES_MPAT_2026/` en MPAT3 antes de iniciar este lote.
P01–P10 ya están en Drive. P11–P75 (65 archivos) pendientes de subida.
**Destino:** `research/` en MPAT4 según tema de cada investigación.

---

### LOTE_007 — Estado y documentos de cierre
**Archivos clave:**
- `ESTADO_CIERRE_V3_DEFINITIVO_R033.md` (ID: 1SY4kFPudgcBzpNEvskaahe3TQpL6m9S9q) → `system_state/`
- `RELAY_035_MPAT_V3_02_ZETA_CERRADO.md` → `relay/` archivado
- `LEEME_ADMIN_V3_CIERRE.md` → `docs/public/`

---

### LOTE_008 — Relay histórico
**Fuente:** `zzz_relay/` y `zzz_proximo_relay/`
**Solo los canónicos (R001–R035).** No los borradores intermedios.
**Destino:** carpeta archivada dentro de `relay/` — marcada como HISTORICO_V3, solo lectura.

---

## IDs CLAVE DE REFERENCIA

| Recurso | ID Drive |
|---|---|
| MPAT3 raíz (SOLO LECTURA) | `1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM` |
| MPAT4 raíz (destino) | `1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI` |
| MIGRATION_LOG.md | `1uCYySAsSGodD5k-axGst8XkVj4dtVu6H` |
| CAPA_08 referencia 10/10 | `1IsmJH4-35F35lDSnZ9_5m3KRJm-_uBQZ` |
| ARQUITECTURA canónico V3_02 | `1peMlToJcdcrU3qFga3sSaCqQjQHMvnis` |
| INDICE_SEMANTICO RES (fuente primaria) | `1xmGZWdzuznz4l5TByFUVMNy5SjwvPKHX` |
| ESTADO_CIERRE_V3_R033 (canónico) | `1SY4kFPudgcBzpNEvskaahe3TQpL6m9S9q` |
| AUDITORIA_TOTAL_MPAT3_PARA_V4 | `1BdPgi3q8BUzUBRp4VMMDJeEUT2NMayFT` |

---

*LOTE_LIST.md · V1_00 · AGT 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*
