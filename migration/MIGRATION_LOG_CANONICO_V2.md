# MIGRATION_LOG_CANONICO — MPAT3 → MPAT4
## Version: V2
## Creado V1: 2026-05-26 · cursos.agt@gmail.com
## Actualizado V2: 2026-05-26 · cursos.agt@gmail.com
## Motivo V2: LOTE_006 replanificado — bloqueo removido por decision docente
## Ver: RESOLUCION_LOTE_006_REPLANIFICACION.md (ID: 1YtsCGAA7epZzZvVy4Vd830YdViUpCJWR)
## Reemplaza V1: ID 1lxtKa3quhNyiq6V0YLhe_k0jJJKU4rV0 (archivado en trashcan)
## LEER LOTE_LIST_b antes de tomar cualquier lote

---

## REGLA DE EXISTENCIA UNICA

ESTE es el unico MIGRATION_LOG valido (V2 — buscar siempre el de mayor version).
Antes de crear cualquier archivo de control, buscar con search_files si ya existe.
NUNCA crear un segundo MIGRATION_LOG.
NUNCA formato gdoc. Siempre text/plain con disableConversionToGoogleType=true.
Parent obligatorio: MPAT4 raiz (ID: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI).

---

## ESTADO GLOBAL

| Parametro | Valor |
|---|---|
| Ciclo fuente | MPAT3 V3_02 — CERRADO DEFINITIVAMENTE |
| Capas migrables | 15/15 (11 directas + 4 adaptadas) |
| RES migrables | 46 activas |
| DTs heredadas | 1 ALTA (cubierta por RES.160) + 6 MEDIA/BAJA |
| Primera RES disponible V4 | RES.161 |
| Lotes totales | 9 |
| Lotes CERRADOS | 3 (LOTE_001, LOTE_002, LOTE_003) |
| Lotes PENDIENTES | 6 (LOTE_004 a LOTE_009) |
| Lotes BLOQUEADOS | 0 — LOTE_006 desbloqueado 2026-05-26 |

---

## REGISTRO DE LOTES

| LOTE_ID | ESTADO | ALUMNO_ID | INICIO | FIN | ARCHIVOS_OK | ARCHIVOS_ADAPTADOS | ARCHIVOS_DESCARTE | NOTAS |
|---|---|---|---|---|---|---|---|---|
| LOTE_001 | HUERFANO | ai.mpat.designer@gmail.com | 2026-05-23 | — | 0 | 1 | 0 | Parcial: ARQUITECTURA_base_V4_00.md generado (ID: 1WavWJdiZZ_I2E0lKUlVCJ-17Nh9ZtuNL). Pendiente: pendientes_V4 + system_V4 + contrato_formal_V4. Retomado por EV_RELAY_013. Ver ESTADO_LOTE_001_PARCIAL.md |
| LOTE_002 | COMPLETADO | andrea.proy | 2026-05-23 | 2026-05-24 | — | — | — | CAPA_09. Canonico: CAPA_09_MASTER_V3_02_FINAL.md (ID: 1kzOamGrWO1jWDGW99eCYA94bgt68JAA-). Trashcan pendiente EV_011. |
| LOTE_003 | COMPLETADO | cursos.agt@gmail.com | — | 2026-05-24 | — | — | — | CAPA_06 + CAPA_07. Canonicos finales en capas/. Trashcan pendiente EV_011. |
| LOTE_004 | LIBRE | — | — | — | — | — | — | CAPAS 00 y 04. Prioridad MEDIA. Disponible. |
| LOTE_005 | LIBRE | — | — | — | — | — | — | CAPAS 01, 02, 03. Prioridad NORMAL. Disponible. |
| LOTE_006 | LIBRE | — | — | — | — | — | — | CAPAS 05 y 08. Desbloqueado 2026-05-26 por decision docente. Ver RESOLUCION_LOTE_006_REPLANIFICACION.md (ID: 1YtsCGAA7epZzZvVy4Vd830YdViUpCJWR). Recursos CAPA_08 pre-identificados: IDs 1fM8vC2fOz7gzR05THTwgfeW3fT2W6ukzgapdjPH19hE y 1ErBZklf5jSOzG5iZmAbEffXQ_UPQQkayxK0ZGXDaAPM |
| LOTE_007 | LIBRE | — | — | — | — | — | — | CAPAS 10, 11, 12. Prioridad NORMAL. Disponible. |
| LOTE_008 | LIBRE | — | — | — | — | — | — | CAPAS 13, 14. Prioridad NORMAL. Disponible. |
| LOTE_009 | LIBRE | — | — | — | — | — | — | Raiz MPAT3. Prioridad MEDIA. Disponible. |

**Estados validos:** LIBRE / EN_CURSO / HUERFANO / COMPLETADO

---

## ARCHIVOS PRODUCIDOS — LOTE_001 (parcial)

| Archivo | ID Drive | Estado |
|---|---|---|
| ARQUITECTURA_base_V4_00.md | 1WavWJdiZZ_I2E0lKUlVCJ-17Nh9ZtuNL | GENERADO |
| ARQUITECTURA_pendientes_V4_00.md | — | PENDIENTE (EV_RELAY_013) |
| ARQUITECTURA_system_V4_00.md | — | PENDIENTE (EV_RELAY_013) |
| contrato_formal_ejecucion_V4_00.md | — | PENDIENTE (EV_RELAY_013) |

---

## ARCHIVOS A MOVER A TRASHCAN — pendiente EV_011

Ver LOTE_LIST_b para lista completa.
Responsable: alumno que tome EV_RELAY_011.

---

## ARCHIVOS DE CONTROL ARCHIVADOS

| Archivo | ID | Fecha | Motivo |
|---|---|---|---|
| MIGRATION_LOG.md (gdoc) | 1Zd4Ey7ND5cEzmnZWiU4rskmgcSn8eWKhcctBPw13OkM | 2026-05-26 | Formato gdoc, estado falso — en trashcan |
| MIGRATION_LOG.md (txt/plain) | 1H58Hb6hs_9FlgO7cYccNx1gov7WODn7N | 2026-05-26 | Parent incorrecto — en trashcan |
| MIGRATION_LOG_CANONICO.md V1 | 1lxtKa3quhNyiq6V0YLhe_k0jJJKU4rV0 | 2026-05-26 | Reemplazado por V2 (LOTE_006 actualizado) — en trashcan |

---

## REGLA DE CIERRE DE MPAT3

Cuando los 9 lotes esten en estado COMPLETADO ejecutar PROTOCOLO_CIERRE_MPAT3.md.
MPAT3 no se elimina. Se renombra a archivo historico de solo lectura.

---

## HISTORIAL DE ACTUALIZACIONES

| Fecha | Alumno | Accion |
|---|---|---|
| 2026-05-23 | agt1973@gmail.com | Log original creado como gdoc (violacion) |
| 2026-05-23 | ai.mpat.designer@gmail.com | LOTE_001 tomado — EN_CURSO |
| 2026-05-23 | ai.mpat.designer@gmail.com | ARQUITECTURA_base_V4_00.md generado — 1 de 4 archivos |
| 2026-05-23 | andrea.proy | LOTE_002 tomado — segundo log creado (ERROR-M1) |
| 2026-05-24 | cursos.agt@gmail.com | LOTE_002 y LOTE_003 cerrados en LOTE_LIST_b (sin actualizar log — ERROR-M2) |
| 2026-05-26 | cursos.agt@gmail.com | MIGRATION_LOG_CANONICO V1 creado — errores M1/M2/M4/M5/M6 reparados |
| 2026-05-26 | cursos.agt@gmail.com | LOTE_006 desbloqueado — LIBRE. V2 creado. |

---

*MIGRATION_LOG_CANONICO.md · V2 · AGT 2026-05-26 · cursos.agt@gmail.com*
*que has usado el formato de razonamiento adaptado por AGT*
