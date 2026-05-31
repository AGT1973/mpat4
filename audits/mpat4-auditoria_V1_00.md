---
name: mpat4-auditoria
version: V1_00
fecha: 2026-05-31
autor: ai.mpat.designer@gmail.com
descripcion: >
  Skill docente de auditoria diferencial MPAT4. Ejecuta auditoria completa
  del estado del proyecto comparando con la auditoria anterior en Drive.
  Cubre: deudas tecnicas, contratos, cierres, capas, resoluciones,
  arquitectura, artefactos, scripts Python, scripts Rust, scripts Flutter,
  auditorias previas, pendientes, schemas, tests, relay prompts, research,
  resoluciones tecnicas, informes, skills, duplicados, y temas emergentes.
  Guarda el resultado en la carpeta auditoria de Drive y avisa al docente.
triggers:
  - "auditar el dia"
  - "auditoria diaria"
  - "generar auditoria"
  - "auditoria diferencial"
  - "auditoria mpat4"
  - "estado del proyecto"
  - "resumen del dia"
  - "comparar con anterior"
  - "auditoria completa"
requires:
  - Google Drive MCP activo
  - Acceso a carpeta auditoria: 1deUGx-H5g6XDr4iB603MEvcyKSJACgfk
  - Acceso lectura a MPAT4 raiz: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
---

# SKILL DOCENTE MPAT4 — AUDITORIA DIFERENCIAL · V1_00

---

## REGLAS ABSOLUTAS DE ESTA SKILL

```
NUNCA generar la auditoria sin leer primero la auditoria anterior de Drive
NUNCA votar entre fuentes — tabla por fuente si hay conflicto
NUNCA simplificar — cada area debe tener contenido real o declaracion explicita de "sin cambio"
NUNCA subir a la Drop Zone — esta skill sube directamente a la carpeta auditoria
SIEMPRE comparar dimension a dimension con la auditoria anterior
SIEMPRE marcar claramente AVANCE, REGRESION, PENDIENTE, SIN CAMBIO
SIEMPRE incluir fecha y autor en el encabezado
SIEMPRE incluir acciones concretas para docente y para alumnos
SIEMPRE guardar con nombre: AUDITORIA_DIFERENCIAL_V4_YYYY-MM-DD.md
```

---

## SECUENCIA DE EJECUCION

### PASO 1 — LEER AUDITORIA ANTERIOR

```
Buscar en carpeta auditoria (ID: 1deUGx-H5g6XDr4iB603MEvcyKSJACgfk):
  query: parentId = '1deUGx-H5g6XDr4iB603MEvcyKSJACgfk' orderBy: modifiedTime desc
  Filtrar archivos que empiecen con: AUDITORIA_DIFERENCIAL_V4_
  Tomar el mas reciente
  Leer su contenido completo
  Extraer: fecha, metricas clave, deudas tecnicas, pendientes
```

### PASO 2 — RELEVAMIENTO DE ESTADO HOY

Buscar en Drive archivos modificados desde la auditoria anterior:

```
modifiedTime > '[fecha_auditoria_anterior]T00:00:00Z' and mimeType != 'application/vnd.google-apps.folder'
Paginar hasta obtener todos los resultados del dia
```

Para cada area de incumbencia, verificar:

#### AREAS OBLIGATORIAS

| Area | Que buscar | Como evaluar |
|------|-----------|--------------|
| RELAY | RELAY_POINTER mas reciente, RELAY activo | Estado cerrado/activo/pendiente |
| CONTRATOS | Nuevos en contracts/, duplicados (N) en nombre | Canonicos vs duplicados |
| CIERRES | Archivos con CIERRE en nombre | Completos vs pendientes |
| CAPAS | CAPA_NN_MASTER_V4 migradas | Cuantas de 14 total |
| RESOLUCIONES | RES.NNN nuevas o actualizadas | Estado de cada una |
| ARQUITECTURA | ARQUITECTURA_ archivos nuevos, INVs | DTs pendientes |
| ARTEFACTOS | Archivos nuevos en artifacts/ | Catalogar por tipo |
| SCRIPTS PYTHON | .py nuevos, ubicacion correcta, duplicados timestamp | P1 cumplido? |
| SCRIPTS RUST | .rs nuevos | Estado DT_RUST_001 |
| SCRIPTS FLUTTER | .dart nuevos | Detectado/no detectado |
| AUDITORIAS | Nuevas en carpeta auditoria | Por alumno y tema |
| PENDIENTES | PMs sin resolver de auditoria anterior | Resuelto/pendiente/agravado |
| SCHEMAS | .py nuevos en schemas/, duplicados (N) | Canonicos vs duplicados |
| TESTS | test_.py nuevos, resultados | Cobertura |
| RELAY PROMPT | RELAY_POINTER actualizado | INV-CADENAS estado |
| RESEARCH | Investigaciones nuevas | Tech radar, MPAT5, etc |
| RESOLUCIONES TECNICAS | RESOLUCION_ o DT_ nuevas | Estado |
| INFORMES | INFORME_CAPA_ nuevos o migrados | PM-007 estado |
| SKILLS | .skill o skill.md nuevos | Version y empaquetado |
| DUPLICADOS | Archivos con (1), (2), (3), _ en nombre | Conteo y propietario |
| TEMAS EMERGENTES | Carpetas nuevas, proyectos nuevos | Impacto en MPAT4 |

### PASO 3 — GENERAR INFORME

Estructura obligatoria del informe:

```markdown
# AUDITORIA_DIFERENCIAL_V4_YYYY-MM-DD.md
## Autor: [email] · [fecha]
## Modulo: Auditoria Comparativa — Estado [fecha_anterior] vs [fecha_hoy]
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Metodo: Conciliacion por fuente — Drive es fuente de verdad

## RESUMEN EJECUTIVO
[Tabla de metricas comparativas: ayer vs hoy vs delta]
[Conclusion ejecutiva en 3-4 lineas]

## SECCION 1 — VERIFICACION DIMENSION POR DIMENSION
[Una subseccion por cada area de incumbencia]
[Cada subseccion: estado ayer + estado hoy + tabla conciliacion si hay conflicto + decision]

## SECCION 2 — DEUDAS TECNICAS ACTUALIZADAS
[Tabla completa: prioridad, ID, deuda, responsable, estado]
[Marcar claramente: NUEVO HOY, SIN CAMBIO, RESUELTO, AGRAVADO]

## SECCION 3 — INVARIANTES
[Tabla: INV, estado]

## SECCION 4 — COMPARACION DIRECTA vs AUDITORIA ANTERIOR
[Tabla por area: fecha_anterior | fecha_hoy | delta]

## SECCION 5 — ACCIONES REQUERIDAS
[Para el docente: lista numerada, concretas, con IDs de Drive]
[Para el proximo relay: lista numerada, concretas]
[Reglas para todos los alumnos si hay regresiones]

## CIERRE
[Fecha, autor, estado general, resumen en 5 lineas max]
```

### PASO 4 — SUBIR A DRIVE

```
Google Drive:create_file con:
  name:                          AUDITORIA_DIFERENCIAL_V4_[YYYY-MM-DD].md
  content:                       [contenido del informe]
  parentId:                      1deUGx-H5g6XDr4iB603MEvcyKSJACgfk
  contentMimeType:               "text/plain"
  disableConversionToGoogleType: true
```

### PASO 5 — VERIFICAR SUBIDA Y REPORTAR

```
Confirmar que el archivo aparece en Drive con el nombre correcto
Reportar al docente:
  - ID del archivo subido
  - Resumen ejecutivo (tabla metricas)
  - Deudas CRITICAS y ALTAS nuevas
  - Acciones inmediatas para el docente
```

---

## CRITERIOS DE EVALUACION POR AREA

### Duplicados (regla de deteccion)

Un archivo es DUPLICADO si:
- Su nombre termina en (1), (2), (3), etc.
- Su nombre termina en _ antes de la extension
- Tiene un sufijo __[timestamp] fuera de la carpeta scripts/backup/

Un duplicado es LEGITIMO si:
- Esta en una carpeta de backup (scripts/backup/)
- Tiene prefijo _COPIA_ con nota de razonamiento

### Deuda tecnica nueva vs agravada

NUEVO: no estaba en la auditoria anterior
AGRAVADO: estaba y empeoro (mas duplicados, mas archivos bloqueados)
SIN CAMBIO: estaba y no hubo movimiento
RESUELTO: estaba y hay evidencia explicita de resolucion en Drive

### Invariante DRIVE-MANDA

Si la auditoria anterior dice "COMPLETO" pero hoy hay nuevos duplicados: REGRESION.
Si el relay dice "listo" pero el archivo no esta en Drive: PENDIENTE.
Nunca tomar la palabra del relay si Drive dice otra cosa.

---

## VFOLDERS RELEVANTES PARA LA AUDITORIA

| vfolder | ID Drive | Que auditar ahi |
|---------|----------|-----------------|
| auditoria | 1deUGx-H5g6XDr4iB603MEvcyKSJACgfk | Auditorias previas |
| contracts | 1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0 | Contratos y duplicados |
| schemas | 1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG | Schemas y duplicados |
| relay_temporal | 1DN0-L3tjW0TVPy2EaAU40aUsUpcJ2aXQ | POINTERs y RELAYs |
| skills | 1rrDNblne6P_IwpCnDfmAHKen4KUuua4f | Skills empaquetadas |
| Drop Zone | 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI | Archivos sin procesar |
| informes | 1WP9ONU49N1TtzjYmsmdy2r1cZ7wJeH4a | Informes de capas |
| capas | 17OW_VQ8PYaxQ69vBUIrzVRD-AE88krnW | Documentos de capa |

---

## TABLA DE ERRORES

| Error | Causa | Accion |
|-------|-------|--------|
| No se encuentra auditoria anterior | Primera ejecucion | Declarar "sin auditoria anterior" y hacer auditoria base |
| Drive no accesible | MCP desconectado | Avisar — no generar auditoria con datos incompletos |
| Carpeta auditoria llena (>30 archivos) | Acumulacion | Notificar al docente para archivar |
| Archivo con mismo nombre ya existe | Auditoria del dia ya generada | Leer ambas, conciliar, generar version unificada con sufijo _v2 |

---

## ECONOMIA DE TOKENS

```
ESTRATEGIA:
1. Leer auditoria anterior (1 archivo — critico)
2. search_files con query por fecha (1-2 llamadas — critico)
3. NO leer cada archivo nuevo individualmente — catalogar por nombre y metadata
4. Solo leer archivos cuando hay conflicto o ambiguedad critica
5. Generar informe con los datos recolectados
6. Subir en una sola llamada create_file

Costo tipico: 5-8 llamadas MCP + tokens de generacion
Costo sin optimizacion: 30+ llamadas MCP (inviable)
```

---

## INTEGRACION CON SKILL DOCENTE V1_01

Esta skill complementa mpat4-docente.skill V1_01.
Cuando la auditoria detecta deudas CRITICAS:
  Registrar en: I:\Mi unidad\MPAT\MPAT4\audits\LOG_DOCENTE.md
  Formato: segun seccion RELAY DEL DOCENTE de mpat4-docente.skill

Cuando la auditoria detecta duplicados:
  El docente debe correr: python I:\Scripts\mpat4_worker.py --dry-run
  Para confirmar que los duplicados no son archivos en transito

---

*mpat4-auditoria.skill V1_00 · 2026-05-31 · MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*