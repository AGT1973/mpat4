# RESOLUCION_DOCENTE_001.md
## Autor: clases.andrea.biologia@gmail.com · 2026-05-26
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Tipo: Resolucion de acciones pendientes — destinatario exclusivo: docente
## Para: ai.mpat.designer@gmail.com
## que has usado el formato de razonamiento adaptado por AGT

---

## RESUMEN EJECUTIVO

Hay dos acciones que solo el docente puede ejecutar y que bloquean o degradan
el trabajo de todos los alumnos en cada sesion. Ambas son de baja complejidad
tecnica pero requieren acceso administrativo al Drive del proyecto y al
sistema de configuracion de Claude.ai de los alumnos.

---

## ACCION-DOC-001 — Permisos de escritura en carpetas MPAT4

Estado: URGENTE — activo desde RELAY_012 aproximadamente
ID deuda: DT-PERM-001

Carpetas con canAddChildren=false para los alumnos:

| Carpeta | ID | Impacto |
|---|---|---|
| relay/ | 1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte | relays guardados en raiz MPAT4 |
| relay/temporal/ | 1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu | artefactos temporales en raiz |
| cognition/ | 1K1dR78NjVNT70g6VTTWv4LZxFsnbnrJU | engines y schemas cognitivos en raiz |
| agent_registry/ (vieja) | 11u7yEBhHjjOnEIP5-C5zvHDZsq3_3mNO | registry en raiz |

Desde RELAY_012 hasta RELAY_017 (6 relays), todos los artefactos que debian ir
a esas carpetas fueron guardados en la raiz MPAT4 con prefijo TEMPORAL_.

Accion requerida:
1. En Google Drive: abrir cada carpeta listada arriba.
2. Click derecho → Compartir → verificar que los alumnos tienen rol "Editor".
3. Si el rol es "Viewer": cambiar a "Editor" para las cuentas del grupo MPAT4.
4. Notificar al grupo que los permisos fueron actualizados.

Accion posterior (alumno, una vez resuelto):
Mover los archivos TEMPORAL_ a sus carpetas correctas y renombrarlos sin el prefijo.
Puede delegarse al proximo alumno disponible como tarea de RELAY_018 opcion 7.

---

## ACCION-DOC-002 — Actualizar bootstrap mpat4-alumno.skill

Estado: ALTA — activo desde RELAY_017
ID deuda: RIESGO-SKILL-001 / DEC-054

Problema:
El archivo mpat4-alumno.skill instalado en las preferencias de los alumnos contiene:

  ID: 1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD   ← SKILL_V4_12 (vieja, backup)

Debe decir:
  ID: 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6   ← SKILL_V4_14 (activa)

Las 4 nuevas rutas de carpetas registradas en V4_14 no son conocidas por los alumnos
hasta que se resuelva esto.

Accion requerida:
En el archivo mpat4-alumno.skill (instalado en Settings → Profile → Personal preferences
de cada alumno), buscar la linea que contiene el ID de SKILL PRINCIPAL y reemplazarla.
Notificar al grupo para que actualicen sus preferencias.

---

## ACCION-DOC-003 — Definir politica de tracks paralelos (MEDIA)

Estado: RIESGO-STR-002 — registrado por ariel, pendiente decision coordinador

El RELAY_POINTER_V4_018_UNIFICADO.md incluye una politica sugerida:
- Un solo RELAY activo a la vez en MPAT4 V4
- Docente puede crear pointers con sufijo _DOCENTE
- Track V3_01 usa numeracion RELAY_V3_xxx

El docente debe confirmar, modificar o reemplazar esta politica.
Si no hay respuesta en el proximo relay, la politica sugerida queda vigente por defecto.

---

## VERIFICACION ESPERADA

Cuando ACCION-DOC-001 y ACCION-DOC-002 esten resueltas, notificar al grupo:

  MPAT4 — Permisos y skill actualizados.
  - Carpetas relay/, cognition/, agent_registry/ ahora tienen permisos de escritura.
  - mpat4-alumno.skill actualizado: ID = 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6
  - Los archivos TEMPORAL_ en raiz MPAT4 pueden ser movidos por cualquier alumno.
  - RELAY_018 disponible — pointer: RELAY_POINTER_V4_018_UNIFICADO.md
    ID: 1ZGUBDS39u4DlCBUpD6pFPBR5_djv65dH

---

*RESOLUCION_DOCENTE_001.md · clases.andrea.biologia@gmail.com · 2026-05-26*
*que has usado el formato de razonamiento adaptado por AGT*
