# RELAY_017.md
## Autor: AGT (docente) · 2026-05-26
## Módulo: herramientas/skills/ · Lenguaje: — · Versión: V4_14
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## RES ejecutada: DEUDA_DOCENTE — Actualización SKILL_V4_14

*que has usado el formato de razonamiento adaptado por AGT*

[APERTURA] — Deuda docente de Alta prioridad registrada en RELAY_016 y RELAY_POINTER_V4_016.
Tarea: actualizar SKILL principal con los 4 IDs de carpetas creadas en RES.166/167/168/169.

[INFO_ALUMNO] — Leer primero: SKILL_V4_14_en_gdrive.md (ID nuevo abajo).
                NO tocar: SKILL_V4_12_en_gdrive.md (backup, no eliminar).

---

## 1. OBJETIVO DE ESTA SESIÓN

Deuda docente completada: SKILL_V4_14_en_gdrive.md creado con los 4 IDs de carpetas nuevas.
La skill anterior (V4_12) queda como backup — no fue modificada (protocolo NUNCA sobreescribir).

Qué se hizo:
- SKILL_V4_14_en_gdrive.md generado con 4 IDs nuevos en el bloque JSON de estructura.
- Version bump V4_12 → V4_14 aplicado en header YAML, títulos, encabezados de artefactos y tabla SKILLS.
- Sección CAMBIOS V4_12 → V4_14 documentada con los 4 ítems exactos y su RES de origen.
- Archivo guardado en herramientas/skills/ con contentMimeType text/plain y disableConversionToGoogleType.

---

## 2. ARTEFACTOS CREADOS

| Archivo | Tipo | Lenguaje | Carpeta | ID Drive | Estado |
|---|---|---|---|---|---|
| SKILL_V4_14_en_gdrive.md | SKILL principal | — | herramientas/skills/ | 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6 | COMPLETO |
| SKILL_V4_12_en_gdrive.md | BACKUP (sin tocar) | — | herramientas/skills/ | 1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD | BACKUP pre-V4_14 |

---

## 3. SCHEMAS / TYPES DEFINIDOS

Sin cambios en schemas. Esta sesión fue exclusivamente de mantenimiento de infraestructura de skills.

---

## 4. EVENTOS DEFINIDOS

Sin nuevos eventos. Sesión de mantenimiento.

---

## 5. DECISIONES ARQUITECTURALES

DEC-054: SKILL_V4_14 creada como archivo nuevo — NO sobreescribiendo V4_12.
         Razón: protocolo inmutable de versioning del proyecto.
         Consecuencia: el bootstrap mpat4-alumno.skill referencia aún a V4_12 → pendiente docente (ver sección 10).

DEC-055: Version bump V4_12 → V4_14 (no V4_13).
         Razón: alinear número de versión con el número de relay activo al momento de la actualización.
         Consecuencia: no hay V4_13 — documentado explícitamente en sección CAMBIOS.

---

## 6. RIESGOS DETECTADOS

RIESGO-SKILL-001: mpat4-alumno.skill (bootstrap local) referencia SKILL_V4_12 por ID.
                  Impacto: alumnos cargan V4_12 en lugar de V4_14 hasta que el docente actualice el bootstrap.
                  Mitigación: actualizar mpat4-alumno.skill con ID 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6.
                  Estado: Activo — pendiente docente.

RIESGO-OBS-001: SubsystemName.AGENT_REGISTRY no existe en schema. Heredado de RELAY_016.
                Estado: Activo.

RIESGO-OBS-002: OTelTracer en RAM — spans no persisten entre reinicios. Heredado de RELAY_016.
                Estado: Activo.

---

## 7. PRÓXIMA PRIORIDAD

Opciones sin precondiciones duras (en orden de impacto):

1. TAREA_RT_001 — event_bus.publish real (Python, impacto Alta, desbloquea comunicación inter-módulo)
   ID contrato: 1rhohqyFWKuSn-mZ54TKb97Cbmhm2s8Bf
2. RES.170 — MCP 2.0 Providers (nuevo módulo, providers/)
3. TAREA_MESH_001 — LamportClock multiprocess (Python, impacto Alta)
   ID contrato: 1efyf_bMvdZHHd_gWM8aO1Czd4jsny-6Q

Acción docente pendiente:
- Actualizar mpat4-alumno.skill con nuevo ID de SKILL_V4_14: 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6

---

## 8. ARCHIVOS CRÍTICOS A LEER PRIMERO

| Archivo | Carpeta | ID Drive |
|---|---|---|
| SKILL_V4_14_en_gdrive.md | herramientas/skills/ | 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6 |
| observability_collector.py | core/observability/ | 15UKxPph6nZ3GtFwtKX6zO196IczsVfha |
| agent_identity.py | agent_registry/identity/ | 1mIdrStX-27hLVQx3ERWiSZSe5offoqnf |

---

## 9. INVARIANTES — NO ROMPER

INV-SKILL-001: NUNCA sobreescribir una skill — siempre versión nueva con nombre nuevo.
INV-SKILL-002: NUNCA modificar el bootstrap mpat4-alumno.skill sin aviso explícito al grupo.
INV-SKILL-003: IDs en el bloque JSON de la skill deben ser verificados contra Drive antes de publicar.
INV-OBS-001: NUNCA importar directamente de otro módulo — solo via event_bus.
INV-OBS-002: health_check() NUNCA lanza excepción hacia arriba.
INV-OBS-003: timestamp SIEMPRE con tzinfo=timezone.utc.
NUNCA Docker. NUNCA subprocess para Python↔Rust.

---

## 10. DEUDA TÉCNICA

| Ítem | Lenguaje | Motivo | Prioridad | Quién resuelve |
|---|---|---|---|---|
| mpat4-alumno.skill: apuntar a V4_14 | — | Bootstrap referencia V4_12 aún | Alta | Docente |
| SubsystemName.AGENT_REGISTRY | Python | No existe en schema | Media | Próxima RES de schema |
| Test unitario RES.169 | Python | Sin test_observability_collector_res169.py | Alta | Próximo alumno tests/ |
| OTelTracer persistencia | Python | Spans en RAM | Media | Cuando memory_fabric esté disponible |

---

[TRASPASO → RELAY_017]
DEUDA_DOCENTE completada. SKILL_V4_14 publicada con 4 IDs nuevos.
Próximo: TAREA_RT_001 event_bus.publish real O RES.170 MCP 2.0 Providers.
Acción docente pendiente: actualizar mpat4-alumno.skill → ID 1F9QYxvTvDLNrM7hXsNLpu42mtb3jcaH6
Firmado: AGT (docente) · 2026-05-26

*que has usado el formato de razonamiento adaptado por AGT*
