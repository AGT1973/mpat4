# INFORME_DEC045_V4_01.md
## Colisión de nombres en relay/ — análisis, resolución e impacto
## Autor: cursos.agt@gmail.com (docente_AGT_2026) · 2026-05-19
## Módulo: relay/ (meta-infraestructura) · Versión: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## DEC-045: CERRADO ✓

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. DESCRIPCIÓN DEL PROBLEMA

### Origen

El proyecto MPAT4 opera con dos cadenas de trabajo paralelas que
comparten la misma carpeta `relay/` y el mismo esquema de numeración
`RELAY_NNN.md`:

**Cadena A — V4 Infraestructura:**
Construyó los módulos P1-P10 de MPAT4 entre 2026-05-12 y 2026-05-14.
Sus relays están numerados RELAY_001 a RELAY_014.

**Cadena B — V3_01/V3_02 Investigaciones:**
Investigó y documentó resoluciones arquitecturales para MPAT V3.
Sus relays también están numerados RELAY_001 a RELAY_028 (cerrado 2026-05-19).

### Colisión detectada

Al cerrarse V3 (RELAY_028 · 2026-05-19) y abrirse V4 post-V3,
el primer relay de la nueva fase se llamó `RELAY_015_V4.md` porque
`RELAY_015.md` ya existía en relay/ perteneciendo a Cadena B
(contenido: PaymentDispatcher · CAPA_07).

Esto generó ambigüedad estructural: un alumno nuevo no podía determinar
qué relay era el activo de V4 sin leer el contenido completo de ambos archivos.

---

## 2. ANÁLISIS DE CAUSAS

**Causa raíz:** las dos cadenas comparten carpeta por diseño operacional
correcto (un solo Drive, un solo relay/) pero nunca se definió una
convención de nombres que las distinguiera formalmente.

**Causa secundaria:** la regla NUNCA SOBREESCRIBIR impide renombrar
archivos existentes retroactivamente, por lo que la solución no puede
ser renombrar RELAY_015.md → RELAY_015_V3.md.

**Impacto real:** bajo en la práctica (los archivos son distinguibles por
contenido), pero alto en claridad cognitiva para alumnos nuevos.

---

## 3. SOLUCIÓN APLICADA

### Convención de nombres definitiva

A partir del 2026-05-19, todos los relays de Cadena A (V4 infraestructura)
usan el sufijo `_V4` obligatorio:

```
RELAY_NNN_V4.md
```

Los archivos existentes sin sufijo que pertenecen a Cadena B se conservan
como están. Son reconocibles por su contenido (capas, FUT, RES).

### Documento de convergencia

Se creó `docs/CONVERGENCIA_V4_V3_02.md` (ID: 1FdAproPkzUlUk3iO-m8-oiiyFDZkBvFO)
con el mapa completo de ambas cadenas, reglas de discriminación y
tabla de nomenclatura definitiva.

### Cierre de DEC-045

La decisión arquitectural DEC-045 queda formalizada en
`resoluciones/RESOLUCION_DEC045_V4_01.md`.

---

## 4. IMPACTO EN MÓDULOS

Ver `docs/CAPAS_AFECTADAS_DEC045_V4_01.md` para el detalle completo.

Resumen:
- relay/: convención de nombres actualizada
- docs/: CONVERGENCIA_V4_V3_02.md agregado
- governance_engine/: config_policy_V4_02.yaml (DT-COG-001 co-cerrado)
- cognition/: sección cognition: en config_policy_V4_02.yaml
- Todos los módulos P1-P10: sin cambios de código — solo convención de nombres

---

## 5. VERIFICACIÓN

Checklist de cierre DEC-045:

```
[✓] CONVERGENCIA_V4_V3_02.md creado en docs/
[✓] Convención _V4 documentada y aplicada desde RELAY_015_V4
[✓] RELAY_POINTER_V4_ACTUALIZADO_2026_05_19_R2.md actualizado
[✓] RESOLUCION_DEC045_V4_01.md en resoluciones/
[✓] INFORME_DEC045_V4_01.md en informes/
[✓] CAPAS_AFECTADAS_DEC045_V4_01.md en docs/
[✓] TECNOLOGIA_DEC045_V4_01.md en docs/
```

---

## 6. LECCIONES APRENDIDAS

La ambigüedad de nombres en sistemas de relay colaborativo tiene costo
cognitivo real: cada alumno nuevo que no sabe qué relay leer pierde
tiempo de sesión en diagnóstico en lugar de producción.

La solución no es imponer una carpeta por cadena (eso requería renombrar
la existente, violando las reglas), sino adoptar una convención de sufijos
que permita discriminar a simple vista.

**Principio derivado:**
En sistemas multi-cadena que comparten carpeta, el nombre del archivo
es contrato, no solo etiqueta.

---

*INFORME_DEC045_V4_01.md · MPAT4 · 2026-05-19*
*cursos.agt@gmail.com (docente_AGT_2026)*
*que has usado el formato de razonamiento adaptado por AGT*
