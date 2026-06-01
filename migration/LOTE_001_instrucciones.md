# LOTE_001 — Arquitectura base
## Instrucciones de trabajo para el alumno que tome este lote
## Complejidad: ALTA · Tomar solo si tokens > 70%

---

## ARCHIVOS A PROCESAR (carpeta fuente: MPAT3/arquitectura/)
## ID carpeta fuente: 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF

| Archivo | ID Drive | Decision | Accion |
|---|---|---|---|
| ARQUITECTURA_base_V3_02_INC03.md | 1peMlToJcdcrU3qFga3sSaCqQjQHMvnis | CANONICO ACTIVO | MIGRAR ADAPTADO |
| ARQUITECTURA_base_V3_03.md | (buscar en arquitectura/) | GENERADO R033 | MIGRAR ADAPTADO |
| ARQUITECTURA_pendientes_V3_03.md | (buscar en arquitectura/) | REFERENCIA | MIGRAR |
| ARQUITECTURA_systema_V3_03.md | (buscar en arquitectura/) | DIAGRAMA ASCII | MIGRAR ADAPTADO |
| contrato_formal_ejecucion.md | (buscar en arquitectura/) | HISTORICO V2/V3 | MIGRAR ADAPTADO |
| ARQUITECTURA_base_V3_02_INC03 (2).md | (buscar en arquitectura/) | DUPLICADO | DESCARTAR |
| ARQUITECTURA_base_V3_02_PATCH_INC03.md | (buscar en arquitectura/) | PATCH APLICADO | DESCARTAR |
| ARQUITECTURA_base_V3_01.md | (buscar en arquitectura/) | HISTORICO | DESCARTAR |

## DESTINO EN MPAT4
Carpeta: contracts/ + docs/public/
ID MPAT4 raiz: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI

## ADAPTACIONES OBLIGATORIAS

| Termino V3 | Reemplazar por |
|---|---|
| Docker / contenedor | unikernel (NanoVMs / Firecracker / Unikraft) |
| Python 3.11 / 3.12 | Python 3.14 No-GIL |
| Pydantic V2 | Pydantic V3 |
| RELAY_NNN_MPAT_V3 | RELAY_NNN_MPAT4 |
| (agregar donde no exista) | Rust como lenguaje para hot paths |

## ENCABEZADO OBLIGATORIO

```
---
migrado_desde: MPAT3/arquitectura/[nombre_original]
id_fuente: [ID Drive]
autor_migracion: [tu email]
fecha_migracion: [fecha]
lote: LOTE_001
estado: MIGRADO | MIGRADO_ADAPTADO
cambios: [descripcion o "ninguno"]
destino_mpat4: contracts/ | docs/public/
---
```

## MIGRATION_LOG CANONICO
ID: 1fHZsPrgTMlYBXrDVp0aPVoTE2oY7REqJ
Actualizar despues de cada archivo — no al final del lote.

---

*LOTE_001_instrucciones.md · docente · 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*
