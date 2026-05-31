# INVENTARIO_ARCHIVOS_PROBLEMATICOS_2026-05-27.md
## Para acción manual del docente — ai.mpat.designer@gmail.com
## Generado: 2026-05-27
## Ruta local: I:\Mi unidad\MPAT\MPAT4\

---

## LISTA A — GOOGLE DOCS (convertir a .md manualmente)

Estos archivos están guardados como Google Doc en Drive.
Acción: abrir cada uno → copiar contenido → guardar como .md con el mismo nombre.
Luego eliminar el Google Doc original.

| # | Nombre archivo | Carpeta Drive | Ruta local aproximada | Owner | URL directa |
|---|---|---|---|---|---|
| A-01 | schema_res171.py | schemas/ | I:\...\MPAT4\schemas\ | backup45122021 | https://docs.google.com/document/d/13hWbGwWbDOMPqvNfl5pm1NXGgCo388ROlmFPXhe0o3s/edit |
| A-02 | schema_res172.py | schemas/ | I:\...\MPAT4\schemas\ | backup45122021 | https://docs.google.com/document/d/1DyAXJMgxzlF8RS23z4gsePikasoGt-kA44IeMCIQUdc/edit |
| A-03 | schema_res173.py | schemas/ | I:\...\MPAT4\schemas\ | backup45122021 | https://docs.google.com/document/d/1ghVUAppulMnTqQCPBGFl46cQp4KP3jygYAcFzye2LKQ/edit |
| A-04 | schema_res174.py | schemas/ | I:\...\MPAT4\schemas\ | backup45122021 | https://docs.google.com/document/d/1wuVgKGKPhd7TfkxNqdWPtfo0LchzJM6zdH5aKAx4ZAc/edit |
| A-05 | RELAY_020_MPAT_V4.md | relay/ raíz | I:\...\MPAT4\relay\ | backup45122021 | https://docs.google.com/document/d/1_vI3pJcM73P_Tr8N0YVcOkyy6qqTbWlZIu49igZZdGU/edit |
| A-06 | RELAY_POINTER_V4_020.md | relay/ raíz | I:\...\MPAT4\relay\ | backup45122021 | https://docs.google.com/document/d/1qsoTjMPj518yFQ4CF7s6WUzYbWfXA-uVm5upwJgpzLs/edit |

### Nota A-01 a A-04
Los schema_resNNN.py son código Python guardados como Google Doc — extensión engañosa.
Al convertir: guardar como `schema_resNNN.py` (no .md) en schemas/ con contentMimeType text/x-python.

### Nota A-05 y A-06
Ya existe versión text/plain de ambos en relay/ raíz. El Google Doc es el duplicado. Solo eliminar.

---

## LISTA B — ARCHIVOS .py MAL UBICADOS O DUPLICADOS

Clasificación por problema:

### B-1 — TEMPORALES (borrar a _DEPRECATED)

Prefijo TEMPORAL indica borrador no aprobado para producción.

| # | Nombre | Carpeta actual | ID Drive | Owner | Acción |
|---|---|---|---|---|---|
| B-01 | TEMPORAL_test_cognition_engine_v2.py | relay/ raíz | `1bwPLvQMUvu6xom0gXLvwM4QmRj_aZq14` | claudeacc1011 | _DEPRECATED |
| B-02 | TEMPORAL_cognition_engine_v3.py | relay/ raíz | `1rfKlv7lla9-6neUdpgqFRorph1_Dy2WC` | claudeacc1011 | _DEPRECATED |
| B-03 | TEMPORAL_cognitive_event_mesh_V4_14.py | raíz MPAT4 | `16n4_ixeoo6SbvmM2_tWUgL5CsL-pC9qb` | ariel.garcia.traba | _DEPRECATED |
| B-04 | TEMPORAL_aesp_freeze_session_bridge.py | raíz MPAT4 | `1QzlGUpupSvLnPKVS5mzWwWYJW_OzXNLE` | ariel.garcia.traba | _DEPRECATED |
| B-05 | TEMPORAL_test_aesp_integration.py | raíz MPAT4 | `12Fvd6DrtKg_V8Q2cBuOgXj85H3hNFida` | ariel.garcia.traba | _DEPRECATED |
| B-06 | TEMPORAL_test_sync_memory_to_redis.py | raíz MPAT4 | `1qBJdtfUzERN-lh_FdvMU2rNqCYqe-Bhz` | claudeacc1011 | _DEPRECATED |
| B-07 | TEMPORAL_cognition_engine_v2.py | raíz MPAT4 | `1620qWm75aCJJ570n6CxOJvjzlc3ST4_O` | claudeacc1011 | _DEPRECATED |

### B-2 — EN RELAY/ RAÍZ (mover a core/)

Archivos de producción guardados en lugar equivocado.

| # | Nombre | Carpeta actual | ID Drive | Owner | Carpeta destino |
|---|---|---|---|---|---|
| B-08 | refactoring_agent.py | relay/ raíz | `1Kdy3PUi76TQQUDXcdKuhkZsZVzWHzu8v` | andrea.proyecto.ia | core/ |
| B-09 | social_agent.py | relay/ raíz | `1JrmPZQSepBEU7uAIwwUYTK0hXeQoHw9o` | andrea.proyecto.ia | core/ |

### B-3 — DUPLICADOS (verificar cual es el canónico)

Mismo nombre, dos versiones distintas. Requiere conciliación antes de eliminar.

| # | Nombre | Carpeta | ID | Owner | Tamaño | Fecha |
|---|---|---|---|---|---|---|
| B-10a | runtime_manager_V4_14.py | core/runtime/ | `1q987Sh8H0JPe8E2Wpf8vPpxErCStxNRj` | agt1973 | 5.1 KB | 2026-05-26 |
| B-10b | runtime_manager_V4_14.py | core/runtime/ | `1TphEzgxMvCpv2q9qWYh6Z-huyVGmzF6y` | ariel.garcia.traba | 6.9 KB | 2026-05-27 |
| B-11a | test_cognition_integration.py | raíz MPAT4 | `1fWIDR6IPoIjWnSxEZbZ9LulwryFfkQ-_` | claudeacc1011 | 18 KB | 2026-05-25 |
| B-11b | test_cognition_integration.py | tests/ | `14S0woX46JkUHuVeQhQeyDDSu1liQJGO9` | claudeacc1011 | 18 KB | 2026-05-25 |
| B-11c | test_cognition_integration_raiz_DT-COG-004.py | raíz MPAT4 | `1XJB0NU13-AcUcJ9RKuz5uQ0gxTPyXFgC` | claudeacc1011 | 18 KB | 2026-05-26 |
| B-12a | Copia de event_bus.py | carpeta ariel | `1pjVl3a3uUO8E2aEUvZPnVUy6TM_yZdbn` | ariel.garcia.traba | 20 KB | 2026-05-24 |
| B-12b | event_bus.py | core/event_bus/ | `1fFaLWnpG0hGtCpZcXPuBed9aHsKuz4C-` | ariel.garcia.traba | 20 KB | 2026-05-13 |
| B-13a | lamport_distributed.py | core/cognition/ | `1UoxQe-c0klsk1iQl6R6FWS745me4mGSz` | agt1973 | 8.7 KB | 2026-05-26 |
| B-13b | lamport_distributed.py | carpeta cursos | `1FQK0sk4O_mrLVXcaTE1xJhb4-xebMrMC` | cursos.ai.agt | 18.9 KB | 2026-05-26 |
| B-14a | lamport_schema.py | schemas/ | `1pYj4NsPm4HsptiqtbcEC98LcX1RGoknq` | agt1973 | 2.9 KB | 2026-05-26 |
| B-14b | lamport_schema.py | carpeta cursos | `1KEK9j6iSQbLWM25QFlxEvU05Go-pd4En` | cursos.ai.agt | 4.3 KB | 2026-05-26 |
| B-15a | cognition_engine_V4_03.py | raíz MPAT4 | `1rr1an_br0tYOSC2PfWKFNnKwW2f33H93` | ariel.garcia.traba | 24.2 KB | 2026-05-26 |
| B-15b | cognition_engine_V4_02.py | carpeta ariel | `1tiZh4nw8QGLZeQeULbjZMHeiBlhRdaRD` | ai.mpat.designer | 19.3 KB | 2026-05-25 |

### B-4 — .old (archivar en _DEPRECATED)

| # | Nombre | Carpeta | ID Drive | Owner | Acción |
|---|---|---|---|---|---|
| B-16 | observability_collector.old.py | core/observability/ | `1c9X4E4z_RwtGem5RXGfZOqW6lFgLi7-i` | cursos.ai.agt | _DEPRECATED |
| B-17 | mcp_mpat4_v4_15.old.py | zzz_relay/ | `1NWSXNfFf1byZjM1Irh8EfY6xfcQyWB_w` | cursos.agt | _DEPRECATED |

### B-5 — EN RAÍZ MPAT4 SIN UBICAR (requieren carpeta correcta)

| # | Nombre | ID Drive | Owner | Carpeta destino probable |
|---|---|---|---|---|
| B-18 | aesp_engine.py | `12WUkUwqF2eECTx0OG-3zfPjy2ubF6si0` | ariel.garcia.traba | core/aesp/ |
| B-19 | a2a_contract_store_redis.py | `1SvGFi5R_omxL2BbTJAgea3mafn1AwVN3` | clases.andrea.biologia | core/a2a/ |
| B-20 | test_a2a_economy.py | `1nAKlazuf715Pf4eCb8YDNZBP3tfwBW-0` | clases.andrea.biologia | tests/ |
| B-21 | event_schema.py | `1bPepiz2YK5tPd1dOXjdYW5i8cy1aHpGE` | ariel.garcia.traba | schemas/ (ver B-22) |
| B-22 | event_schema.py | `1kY4b8Z893G_hPUjYo7zjFKmoMBm2cElG` | ai.mpat.designer | schemas/ — CONCILIAR con B-21 |
| B-23 | docx_2_md.py | `1zzU-lKs2NIB1nD_L688fG3VB0o23Nl4y` | ai.mpat.designer | herramientas/ |

---

## RESUMEN DE ACCIONES

| Tipo | Cantidad | Acción |
|---|---|---|
| Google Docs → convertir a .md/.py | 6 | Lista A — editar a mano |
| TEMPORAL → _DEPRECATED | 7 | Lista B-1 — script limpieza |
| Mal ubicados en relay/ → core/ | 2 | Lista B-2 — script limpieza |
| Duplicados → conciliar | 6 grupos | Lista B-3 — decisión docente |
| .old → _DEPRECATED | 2 | Lista B-4 — script limpieza |
| Sin ubicar → carpeta correcta | 6 | Lista B-5 — mover manualmente |

---

## ORDEN DE EJECUCIÓN RECOMENDADO

1. Lista A — convertir Google Docs primero (bloquean la lectura del sistema)
2. Lista B-1 + B-4 — ejecutar con `limpieza_mpat4_docente.py`
3. Lista B-3 — conciliar duplicados (requiere leer contenido de cada par)
4. Lista B-2 + B-5 — reubicar con script o manualmente
5. Verificar que relay/ raíz quede limpio de .py y Google Docs

*INVENTARIO_ARCHIVOS_PROBLEMATICOS_2026-05-27.md · AGT 2026-05-27*
*que has usado el formato de razonamiento adaptado por AGT*
