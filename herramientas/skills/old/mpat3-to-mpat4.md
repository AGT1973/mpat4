name: mpat3-to-mpat4
description: \"Skill de migracion relay por lotes desde MPAT3 hacia MPAT4. Activar cuando el alumno diga 'migrar', 'continuar migracion', 'tomar lote de migracion', 'retomar migracion mpat3', 'hay lotes huerfanos'. Lee el MIGRATION_LOG.md en Drive, toma el proximo lote libre o huerfano, evalua cada archivo del lote para determinar si migra, se adapta o se descarta, y genera los archivos en MPAT4 con encabezado de procedencia. NUNCA sobreescribir en MPAT4. NUNCA migrar sin evaluar vigencia del concepto. NUNCA cerrar sin actualizar el MIGRATION_LOG.\"
---

# mpat3-to-mpat4 — Migracion Relay por Lotes · V1_00
## ⛔ NUNCA sobreescribir archivos existentes en MPAT4
## ⛔ NUNCA migrar un archivo sin evaluar si su concepto sigue vigente en V4
## ⛔ NUNCA cerrar lote sin actualizar MIGRATION_LOG.md
## ⛔ NUNCA asumir que un nombre igual significa que el concepto es igual
## ⛔ NUNCA migrar codigo sin revisar si la tecnologia fue reemplazada (Docker → unikernel, etc.)

---

## Proposito

MPAT3 tiene cientos de archivos. No se pueden migrar todos en una sesion.
Esta skill divide la migracion en LOTES predefinidos, permite que distintos
alumnos tomen distintos lotes, y garantiza que cada archivo migrado quede
correctamente ubicado en MPAT4 con registro de procedencia.

La migracion no es copia. Es evaluacion + traduccion + ubicacion correcta.

**Un archivo de MPAT3 puede terminar en tres destinos:**
1. Migrado y adaptado → carpeta correspondiente en MPAT4
2. Parcialmente valido → migrado con nota de deuda tecnica
3. Obsoleto → descarte/ con nota de por que no aplica a V4

---

## Estructura en Drive

```
MPAT3/ (fuente — SOLO LECTURA durante migracion)
  ID: 1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM

MPAT4/ (destino)
  ID: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
├── MIGRATION_LOG.md           ← registro central — leer primero siempre
├── LOTE_LIST.md               ← lista de lotes definida por el docente
├── relay/temporal/            ← trabajo en curso (ID: 1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu)
├── deprecated/                ← archivos MPAT3 obsoletos con nota (ID: 14b47yd91-ebxV_rp_HVkndp0JKKthF2m)
└── [carpetas normales MPAT4]
```

---

## LOTE_LIST.md — formato del listado de lotes

El docente define este archivo antes de iniciar la migracion.

```
# LOTE_LIST — Migracion MPAT3 → MPAT4
# Version: 1_00 · Docente: [ID] · Fecha: [fecha]

| LOTE_ID  | DESCRIPCION              | CARPETA_FUENTE_MPAT3    | CARPETA_DESTINO_MPAT4  | COMPLEJIDAD | ARCHIVOS_EST |
|----------|--------------------------|-------------------------|------------------------|-------------|--------------|
| LOTE_001 | Arquitectura base        | arquitectura/           | arquitectura/          | ALTA        | ~15          |
| LOTE_002 | Capas 01-05              | capas/CAPA_01-CAPA_05   | cognition/ + capas/    | ALTA        | ~25          |
| LOTE_003 | Capas 06-10              | capas/CAPA_06-CAPA_10   | cognition/ + capas/    | ALTA        | ~25          |
| LOTE_004 | Capas 11-14              | capas/CAPA_11-CAPA_14   | cognition/ + capas/    | MEDIA       | ~20          |
| LOTE_005 | Resoluciones             | resoluciones/           | resoluciones/          | MEDIA       | ~30          |
| LOTE_006 | Investigaciones          | investigaciones/        | investigaciones/       | BAJA        | ~20          |
| LOTE_007 | Estado y plantillas      | estado/ + plantillas/   | estado/ + docs/        | BAJA        | ~15          |
| LOTE_008 | Relay historico          | zzz_proximo_relay/      | relay/ (solo lectura)  | BAJA        | ~10          |
```

**Complejidad define cuantos tokens necesita el lote:**
- ALTA  → solo tomar si tokens > 70%
- MEDIA → tomar si tokens > 50%
- BAJA  → tomar si tokens > 35%

---

## MIGRATION_LOG.md — formato obligatorio

```
# MIGRATION_LOG — MPAT3 → MPAT4
# Actualizado: [FECHA HORA] por [ALUMNO_ID]

| LOTE_ID  | ESTADO      | ALUMNO_ID    | INICIO              | ARCHIVOS_OK | ARCHIVOS_DESCARTE | NOTAS               |
|----------|-------------|--------------|---------------------|-------------|-------------------|---------------------|
| LOTE_001 | COMPLETADO  | ana@mail.com | 2026-05-20 10:00   | 13          | 2                 | CAPA_00 descartada  |
| LOTE_002 | EN_CURSO    | bob@mail.com | 2026-05-20 11:30   | 8           | 1                 | Continuar CAPA_04   |
| LOTE_003 | LIBRE       | —            | —                   | —           | —                 | —                   |
```

**Estados:** LIBRE / EN_CURSO / HUERFANO / COMPLETADO

---

## Flujo de migracion — paso a paso

### INICIO DE SESION

```
PASO 0 — IDENTIFICACION
  Preguntar: \"Nombre o email para el registro de migracion?\"
  Guardar como ALUMNO_ID

PASO 1 — LEER ESTADO
  Leer MIGRATION_LOG.md → que lotes hay disponibles
  Leer LOTE_LIST.md → descripcion y complejidad de cada lote
  Evaluar tokens actuales:
    Tokens > 70% → puede tomar lote ALTA, MEDIA o BAJA
    Tokens 50-70% → puede tomar lote MEDIA o BAJA
    Tokens 35-50% → puede tomar lote BAJA solamente
    Tokens < 35%  → NO tomar lote nuevo. Solo documentar y cerrar.

PASO 2 — SELECCIONAR LOTE
  Prioridad 1: Lotes HUERFANOS (tienen trabajo parcial — rescatar)
  Prioridad 2: Lotes LIBRES de menor LOTE_ID (orden secuencial)
  Verificar que la complejidad del lote es compatible con los tokens disponibles
  Si no: tomar el siguiente de menor complejidad
```

### TOMAR UN LOTE

```
PASO 3 — MARCAR EN CURSO
  Actualizar MIGRATION_LOG.md:
    ESTADO    → EN_CURSO
    ALUMNO_ID → [ALUMNO_ID]
    INICIO    → [FECHA HORA]
  ⛔ Guardar MIGRATION_LOG antes de empezar a migrar

PASO 4 — LISTAR ARCHIVOS DEL LOTE
  Leer la carpeta fuente en MPAT3 indicada en LOTE_LIST
  Generar lista de archivos a procesar
  Si hay trabajo parcial (lote rescatado): leer ESTADO_LOTE_PARCIAL.md
  en la temp/ anterior para saber donde se interrumpio
```

### EVALUAR Y MIGRAR CADA ARCHIVO

```
PASO 5 — EVALUACION DE VIGENCIA (por cada archivo)

  PREGUNTA A — Concepto vigente en V4?
    Ejemplo: CAPA_00 → descarte. ARQUITECTURA_UNIKERNEL → vigente pero adaptar Docker.

  PREGUNTA B — Terminologia correcta?
    Ver tabla de traduccion V3→V4 al final de esta skill.

  PREGUNTA C — Tecnologia reemplazada?
    Ver tabla de cambios tecnologicos al final de esta skill.

  DECISION:
    Todo OK          → migrar con encabezado de procedencia
    Necesita cambios → migrar con cambios + nota ADAPTADO
    Concepto muerto  → deprecated/ con nota de razon

PASO 6 — GENERAR ARCHIVO MIGRADO
  Si migra (OK o ADAPTADO):
    Nombre: [nombre_original]_V4_migrado.md
    Encabezado al inicio:
      ---
      migrado_desde: MPAT3/[ruta_relativa]
      autor_migracion: [ALUMNO_ID]
      fecha_migracion: [FECHA]
      estado: MIGRADO | MIGRADO_ADAPTADO
      cambios: [descripcion o \"ninguno\"]
      ---
    Guardar en carpeta destino indicada en LOTE_LIST usando el ID de Drive.

  Si obsoleto:
    Nombre: OBSOLETO_[nombre_original].md
    Encabezado:
      ---
      descartado_desde: MPAT3/[ruta_relativa]
      autor_evaluacion: [ALUMNO_ID]
      fecha: [FECHA]
      razon: [explicacion concreta]
      ---
    Guardar en deprecated/ (ID: 14b47yd91-ebxV_rp_HVkndp0JKKthF2m)

PASO 7 — ACTUALIZAR MIGRATION_LOG despues de CADA archivo
  Incrementar ARCHIVOS_OK o ARCHIVOS_DESCARTE
  ⛔ No esperar al final del lote — si se corta la sesion, el log refleja el estado real
```

### CIERRE

```
PASO 8 — LOTE COMPLETADO
  Todos los archivos procesados →
    MIGRATION_LOG → COMPLETADO
    Verificar encabezados y ubicacion de todos los archivos del lote

PASO 9 — CIERRE POR TOKENS (lote incompleto)
  Crear en relay/temporal/[ALUMNO]_[FECHA]/ESTADO_LOTE_PARCIAL.md:
    ## Lote: [LOTE_ID]
    ## Ultimo archivo procesado: [nombre]
    ## Archivos pendientes: [lista]
    ## Notas para quien retome: [texto libre]
  MIGRATION_LOG → dejar EN_CURSO

PASO 10 — MENSAJE AL GRUPO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    MPAT3→MPAT4 · CIERRE DE SESION
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Alumno:           [ALUMNO_ID]
    Lote trabajado:   [LOTE_ID] — [descripcion]
    Resultado:        [N] migrados + [M] adaptados + [K] descartados
    Estado del lote:  COMPLETADO | EN_CURSO — continuar desde [archivo]
    Siguiente libre:  [LOTE_ID] — Complejidad: [nivel]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Tabla de traduccion V3 → V4

| Termino V3 | Termino V4 | Notas |
|---|---|---|
| CAPA_00 | no existe | Eliminar referencias |
| Docker / contenedor | unikernel (NanoVMs / Unikraft / Firecracker) | Cambio critico |
| RELAY_NNN_MPAT_V3 | RELAY_NNN_MPAT4 | Renombrar |
| tokens/64k | contexto variable segun modelo | Actualizar numeros |
| SubQ (borrador) | SubQ V4 (implementado) | Actualizar estado |
| A2A (propuesto) | A2A v1.0 (activo) | Actualizar estado |
| ShadowRadix (investigacion) | ShadowRadix (Capa 5 incorporado) | Actualizar |
| CAPA_XX_MASTER.md V2/V3 | modulo en cognition/ | Reubicar |
| zzz_proximo_relay/ | relay/ | Renombrar referencia |
| MPAT_V3_0 | MPAT4 | En encabezados |

---

## Tabla de cambios tecnologicos V3 → V4

| Tecnologia V3 | Estado en V4 | Accion |
|---|---|---|
| Docker | PROHIBIDO | Reemplazar por unikernel |
| Python 3.11/3.12 | → Python 3.14 No-GIL | Actualizar docs |
| Pydantic V1/V2 | → Pydantic V3 | Actualizar schemas |
| FastAPI < 0.115 | → FastAPI 0.115+ | Deuda tecnica |
| REST como unico protocolo | REST + gRPC/ConnectRPC + MCP | Ampliar |
| Rust | NUEVO — no existia en V3 | Es adicion, no migracion |

---

## Reglas de calidad

| Regla | Consecuencia si se viola |
|---|---|
| Evaluar vigencia antes de copiar | Basura migrada contamina MPAT4 |
| Encabezado de procedencia en cada archivo | No se puede rastrear origen |
| MIGRATION_LOG actualizado por archivo | Si se corta, no se sabe donde quedo |
| Nunca sobreescribir en MPAT4 | Perdida de trabajo de otros alumnos |
| Lote tomado segun tokens disponibles | Lote huerfano bloquea a otros |
| Obsoletos en deprecated/ con razon explicita | Confusion sobre ausencia del archivo |

---

*mpat3-to-mpat4.skill · V1_00 · AGT 2026-05-20*
