# INFORME_CONVERGENCIA_RELAY_017.md
## Autor: clases.andrea.biologia@gmail.com · 2026-05-26
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Tipo: Informe de evaluacion y convergencia — version RELAY_017
## Destinatarios: ai.mpat.designer@gmail.com (docente) + grupo MPAT4
## que has usado el formato de razonamiento adaptado por AGT

---

## 1. SITUACION DETECTADA

Al evaluar el RELAY_POINTER_V4_017 se encontraron TRES pointers con el mismo
numero de version, escritos el mismo dia por tres autores distintos, con contenido
divergente. Esto impide que cualquier alumno nuevo sepa con certeza que RELAY_018
debe ejecutar.

Adicionalmente, existe un cuarto track (ariel / V3_01 DT-004) completamente separado
del repo MPAT4 principal que tambien usa numeracion RELAY_017.

---

## 2. MAPA REAL DE TRACKS ACTIVOS

| Track | Autor | Ambito | Ultimo relay | Estado |
|---|---|---|---|---|
| A — cognition/ | claudeacc1011@gmail.com | CoT/ToT schema_v2 sync_memory | RELAY_017 cerrado | schema V2 generado, engine pendiente de ajuste |
| B — AESP + registry | ariel.garcia.traba@gmail.com | RES.171 AESP, agent_registry V4_03, cognition_engine_V4_03 | RELAY_017 cerrado | 5 artefactos producidos |
| C — infra skills | cursos.ai.agt@gmail.com (docente) | SKILL_V4_14, mantenimiento carpetas | RELAY_017 cerrado | skill publicada, bootstrap pendiente |
| D — V3_01 DT-004 | ariel.garcia.traba@gmail.com | informes de capas V3_01 | RELAY_017_DT cerrado | track completamente independiente, no interfiere con MPAT4 V4 |

---

## 3. ANALISIS DE SOLAPAMIENTO ENTRE TRACKS

### 3.1 Solapamiento A-B (cognition/) — REAL Y REQUIERE RESOLUCION

Track A (claudeacc1011) produjo:
- TEMPORAL_cognition_schema_v2.py (ID: 1WW4lDj8QgKMKJ1EZpSMFOO3qPwG0Hy1E)
  Agrega: ReasoningStrategy enum en schema, CognitionConfig tipado,
  ThoughtEntry.reasoning_strategy, ThoughtTrace.strategies_used()

Track B (ariel) produjo:
- cognition_engine_V4_03.py (ID: 1rr1an_br0tYOSC2PfWKFNnKwW2f33H93)
  Implementa CoT + ToT beam search, importa ReasoningStrategy desde el engine (local)

PROBLEMA CONCRETO: el engine V4_03 define ReasoningStrategy localmente.
El schema v2 tambien lo define. Hay dos definiciones del mismo tipo en el proyecto.
DEC-053 (track A) establece que ReasoningStrategy debe vivir en el schema, no en el engine.
El engine V4_03 (track B) no fue ajustado a DEC-053 — esto es exactamente DT-COG-007b.

RESOLUCION: DT-COG-007b es la tarea de ajuste que une los dos tracks.
Es una tarea pequeña (eliminar la definicion local del engine, agregar el import).
No hay contradiccion conceptual — ambos tracks llegaron al mismo diseno por caminos distintos.

### 3.2 Solapamiento B-C (infraestructura) — APARENTE, NO REAL

Track B usa la skill para trabajar. Track C actualiza la skill.
El unico riesgo es que alumnos del track B carguen SKILL_V4_12 (vieja) mientras
el docente no actualice el bootstrap. Esto es RIESGO-SKILL-001, ya documentado.
No hay contradiccion de contenido entre los tracks.

### 3.3 Track D — INDEPENDIENTE

El track DT-004 de ariel opera sobre un repo V3_01 completamente distinto.
Sus artefactos (INFORME_CAPA_12, CAPA_13, etc.) no interfieren con MPAT4 V4.
El uso de "RELAY_017" en ese track es una coincidencia de numeracion — no hay
relacion con los relays del proyecto principal. No requiere accion de convergencia.

---

## 4. PROBLEMAS ESTRUCTURALES (independientes de los tracks)

### PROBLEMA-PERM-001 — Permisos de escritura (URGENTE)

Carpetas sin permisos de escritura desde hace varios relays:
- relay/ (ID: 1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte)
- cognition/ (ID: 1K1dR78NjVNT70g6VTTWv4LZxFsnbnrJU)
- agent_registry/ (ID: 11u7yEBhHjjOnEIP5-C5zvHDZsq3_3mNO)
- relay/temporal/ (ID: 1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu)

Impacto acumulado: todos los artefactos de R012 a R017 estan en raiz MPAT4
con prefijo TEMPORAL_. La estructura del proyecto se degrada cada relay.
Requiere: ai.mpat.designer@gmail.com verifica y cambia permisos en Drive.

### PROBLEMA-SKILL-001 — Bootstrap desactualizado (ALTA)

mpat4-alumno.skill apunta a SKILL_V4_12 (ID: 1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD).
La skill activa es SKILL_V4_14 (ID: 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6).
Los alumnos cargan la version vieja en cada sesion hasta que el docente actualice.
Requiere: actualizar la linea del ID en mpat4-alumno.skill instalado en los alumnos.

### PROBLEMA-POINTER-001 — Tres pointers activos simultaneos (CRITICO)

El sistema de relay asume un unico pointer como fuente de verdad.
Hay tres pointers con numeracion V4_017, en carpetas distintas, con contenido divergente.
Un alumno nuevo que llega a RELAY_018 no tiene forma deterministica de saber cual seguir.
Resolucion: RELAY_POINTER_V4_018_UNIFICADO.md generado en esta sesion.

---

## 5. DECISION DE UNIFICACION

Los tres tracks A, B, C operan sobre el mismo sistema MPAT4 V4. Sus tablas de estado,
IDs clave, deuda tecnica y proximas tareas viven en el RELAY_POINTER_V4_018_UNIFICADO.md.

Lo que se reporta por separado (temas distintos):
- Track D (ariel / V3_01 DT-004): INFORME_TRACK_D_DT004.md
- Acciones docente: RESOLUCION_DOCENTE_001.md

---

## 6. ARTEFACTOS GENERADOS EN ESTA SESION

| Archivo | Tipo | ID Drive |
|---|---|---|
| INFORME_CONVERGENCIA_RELAY_017.md | Este informe | (guardar en raiz MPAT4) |
| RELAY_POINTER_V4_018_UNIFICADO.md | Nuevo pointer unico | (guardar en raiz MPAT4) |
| RESOLUCION_DOCENTE_001.md | Acciones exclusivas docente | (guardar en raiz MPAT4) |
| INFORME_TRACK_D_DT004.md | Estado track V3_01 | (guardar en raiz MPAT4) |
| CIERRE_POINTERS_OBSOLETOS_017.md | Cierre formal pointers viejos | (guardar en raiz MPAT4) |

*INFORME_CONVERGENCIA_RELAY_017.md · clases.andrea.biologia@gmail.com · 2026-05-26*
*que has usado el formato de razonamiento adaptado por AGT*
