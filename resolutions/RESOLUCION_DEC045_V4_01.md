# RESOLUCION_DEC045_V4_01.md
## Decisión Arquitectural DEC-045 — Resolución formal
## Autor: cursos.agt@gmail.com (docente_AGT_2026) · 2026-05-19
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Estado: APROBADO Y VIGENTE

*que has usado el formato de razonamiento adaptado por AGT*

---

## ENCABEZADO DE DECISIÓN

| Campo | Valor |
|-------|-------|
| ID | DEC-045 |
| Título | Convención de nombres para cadenas paralelas en relay/ |
| Tipo | Convención de nomenclatura — meta-infraestructura |
| Prioridad | ALTA — impacta navegabilidad de todos los relays V4 |
| Estado | APROBADO ✓ |
| Fecha | 2026-05-19 |
| Autor | cursos.agt@gmail.com (docente_AGT_2026) |
| Módulos afectados | relay/ · docs/ · governance_engine/ · cognition/ |

---

## CONTEXTO

Al cerrarse V3 (RELAY_028 · 2026-05-19) y retomarse trabajo V4,
el primer relay de la nueva fase colisionó en nombre con un relay
existente de Cadena B (V3_01 investigaciones):

- `RELAY_015.md` → Cadena B · PaymentDispatcher · CAPA_07 (preexistente)
- `RELAY_015_V4.md` → Cadena A · config_policy V4_02 · DT-COG-001 (nuevo)

La ambigüedad era navegacional: sin leer el contenido completo, un
alumno nuevo no podía determinar cuál era el relay activo de V4.

---

## OPCIONES EVALUADAS

### Opción A — Mover Cadena B a subcarpeta relay/v3/
Descartada. Requiere mover archivos existentes, lo que viola
INV-GLOBAL-001 (NUNCA sobreescribir / mover sin coordinador).

### Opción B — Renombrar archivos Cadena B con prefijo V3_
Descartada. Igual violación de INV-GLOBAL-001. Los archivos
RELAY_015.md, RELAY_016.md, etc. son inmutables.

### Opción C — Sufijo _V4 en todos los relays nuevos de Cadena A
ADOPTADA. No toca archivos existentes. Aplica hacia adelante.
Costo: cero. Beneficio: discriminación inmediata por nombre.

### Opción D — Crear carpeta relay_v4/ separada
Descartada. Rompe la continuidad de la cadena A (RELAY_001 a RELAY_014
ya existen sin esa carpeta y son inmutables).

---

## DECISIÓN ADOPTADA — OPCIÓN C

**A partir del 2026-05-19, todos los relays de Cadena A (V4 infraestructura)
llevan el sufijo `_V4` en el nombre del archivo.**

```
Formato obligatorio: RELAY_NNN_V4.md
Ejemplo: RELAY_016_V4.md, RELAY_017_V4.md
```

**El RELAY_POINTER de Cadena A sigue el mismo patrón:**
```
RELAY_POINTER_V4_ACTUALIZADO_[FECHA].md
```

**Los archivos de Cadena B (V3) no se tocan.** Son reconocibles
por su contenido (CAPA_XX, FUT-NNN, RES.NNN) y están CERRADOS.

---

## ARTEFACTOS QUE IMPLEMENTAN ESTA DECISIÓN

| Artefacto | Ubicación | ID Drive |
|-----------|-----------|----------|
| CONVERGENCIA_V4_V3_02.md | docs/ | 1FdAproPkzUlUk3iO-m8-oiiyFDZkBvFO |
| RELAY_015_V4.md (primer aplicación) | relay/ | 1tfPf9g5Yg5Os1G-MzbGCSXwiSZIHP-Vs |
| RELAY_POINTER_V4_..._R2.md | relay/ | 1q51uHt8XarZJTYpMqeU1Q9MGFuRihfUX |
| INFORME_DEC045_V4_01.md | informes/ | 1HWygHfeg1QLI_CjpxRwZz2jHwscXncRh |
| RESOLUCION_DEC045_V4_01.md | docs/ | (este archivo) |

---

## INVARIANTES DERIVADOS

**INV-RELAY-001 (nuevo):**
Todo relay de Cadena A creado desde 2026-05-19 en adelante
DEBE incluir el sufijo `_V4` en su nombre.

**INV-RELAY-002 (nuevo):**
El archivo RELAY_POINTER activo de Cadena A SIEMPRE tiene
el patrón `RELAY_POINTER_V4_ACTUALIZADO_*.md`.

---

## CIERRE

DEC-045 APROBADO Y VIGENTE desde 2026-05-19.
RIESGO-011 MITIGADO.

---

*RESOLUCION_DEC045_V4_01.md · MPAT4 · 2026-05-19*
*cursos.agt@gmail.com (docente_AGT_2026)*
*que has usado el formato de razonamiento adaptado por AGT*
