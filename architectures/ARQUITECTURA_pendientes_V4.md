---
migrado_desde: MPAT3/arquitectura/ (ARQUITECTURA_pendientes_V2_102 + ARQUITECTURA_pendientes_V2_102 (2) + estado de cierre V3_02)
id_fuente: 1j2ajXzlJ9vQh3vYX6V2PdRan90RFr5an + 1mzUh8iS9ptLH-GhWyNghKzp85D1pYZ_2
autor_migracion: agt1973@gmail.com
fecha_migracion: 2026-05-23
lote: LOTE_001
estado: MIGRADO_ADAPTADO
cambios: |
  - Pendientes V2/V3 evaluados para vigencia en V4
  - DTs heredadas de V3_02 incorporadas
  - FUTs abiertos re-evaluados
destino_mpat4: contracts/
---

# ARQUITECTURA_pendientes_V4.md
## Pendientes abiertos y deudas técnicas heredadas hacia MPAT V4

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. DTs HEREDADAS DE V3_02 (activas en V4)

| DT | Descripción | Prioridad | RES relacionada | Estado |
|----|-------------|-----------|-----------------|--------|
| DT-016-001 | tool_call delegation real vía SubQ | ALTA | RES.160 | Parcialmente cubierta — implementación física pendiente |
| DT-06-01 | namespace mpat:cx:{session_id}:experts sin tenant_id | MEDIA | RES.158 (deuda) | Patch documental emitido, físico pendiente |
| DT-015-001 | CAPA_12 pendientes VMAO DAGPlanner | MEDIA | — | Spec en INFORME_CAPA_12, RES formal pendiente |
| DT-015-004 | CAPA_12 pendientes VMAO DAGVerifier | MEDIA | — | Spec en INFORME_CAPA_12, RES formal pendiente |
| DT-012-003 | CAPA_08 pendiente (Memory Budget) | MEDIA | — | Sin spec formal |
| FUT-12-F | A2A + ECS + SubQ Circuit Breaker | MEDIA | RES.158 (numeración) | Decisión docente: deuda V4 |

---

## 2. FUTs NUEVOS IDENTIFICADOS PARA V4

| FUT | Descripción | Fuente | Prioridad |
|-----|-------------|--------|-----------|
| FUT-V4-01 | A2A Protocol 2026 como nuevo platform_id en CAPA_01 | frontera_capa1.md | ALTA |
| FUT-V4-02 | CAPA_06 Memoria Persistente SOTA 2026 (LOCOMO, LangGraph, MCP SEP-1865) | MPAT_V10_Especificacion_Tecnica_Evolucion_Capa6.md | ALTA |
| FUT-V4-03 | Micropagos x402 / Stripe for Agents (CAPA_07) | investigación 2026 | MEDIA |
| FUT-V4-04 | SEP-1865 MCP Apps UIs ricas en iframe (CAPA_07) | investigación 2026 | MEDIA |
| FUT-V4-05 | Python 3.14 No-GIL validación en producción | stack V4 | ALTA |
| FUT-V4-06 | Rust hot paths vía PyO3 — SubQ broker, schema parser | stack V4 | MEDIA |

---

## 3. PATCHES SIN RES FORMAL (heredados de V3_02)

Estos patches están en resoluciones/ de MPAT3 y requieren RES.162+ en V4:

| Archivo | Capa | RES a asignar | Descripción |
|---------|------|---------------|-------------|
| PATCH_CAPA_14_POLICY_LOADER_V3_02.md | CAPA_14 | RES.162 | Policy Loader refactoring |
| PATCH_CAPA_07_TOOL_REGISTRY_V3_02.md | CAPA_07 | RES.163 | Tool Registry búsqueda semántica |
| CAPA_09_PATCH_FIREWALL_HTML_V3_01.md | CAPA_09 | RES.164 | SemanticFirewall inspect_html() |
| CAPA_13_PATCH_MCP_APP_V3_01.md | CAPA_13 | RES.165 | MCP Apps Delivery |

---

## 4. TAREAS ADMINISTRATIVAS PENDIENTES (no bloqueantes)

| Tarea | Responsable | Estado |
|-------|-------------|--------|
| Borrar 13 archivos duplicados en resoluciones/ MPAT3 | Admin Drive | Pendiente |
| Borrar 25 archivos duplicados en informes/ MPAT3 | Admin Drive | Pendiente |
| Mover informes/V3_02/ subcarpeta (vaciar) | Admin Drive | Pendiente |
| Mover RES.158_V4 y RES.159 a V4/resoluciones/ | Alumno V4 | Pendiente |
| Actualizar INDICE_SEMANTICO con RES.161 | Primer relay V4 | Pendiente |
| Completar LOTE_002 a LOTE_008 | Grupo | En curso |

---

## 5. BLOQUEANTES

| Bloqueante | Descripción | Libera |
|-----------|-------------|--------|
| P11-P75 sin subir | Principios pedagógicos V4 no subidos aún | LOTE_006 |

---

*ARQUITECTURA_pendientes_V4.md · MPAT4 · contracts/ · 2026-05-23*
*agt1973@gmail.com · LOTE_001 · Skill B mpat3-to-mpat4*
*que has usado el formato de razonamiento adaptado por AGT*
