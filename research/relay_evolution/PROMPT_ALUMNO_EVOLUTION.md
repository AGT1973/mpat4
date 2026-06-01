━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT_ALUMNO_EVOLUTION — MPAT4 Etapa de Evolución
Versión: EV_PROMPT_V1 · 2026-05-25
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este archivo es el prompt que cada alumno pega en Claude.ai
al iniciar una sesión de la etapa de EVOLUCIÓN de MPAT4.

INSTRUCCIÓN PARA EL DOCENTE:
- Este prompt está en evolution/relay_evolution/
- Para cada EV-RELAY específico, crear PROMPT_EV_RELAY_NNN.md en la misma carpeta
- Este archivo es el prompt genérico de arranque

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INICIO DEL PROMPT — COPIAR DESDE AQUÍ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hola. Voy a trabajar en la etapa de EVOLUCIÓN del proyecto MPAT4.

Soy alumno del curso. Mi ID es: [ESCRIBIR TU NOMBRE O EMAIL AQUÍ]

Este proyecto es un sistema de infraestructura cognitiva distribuida implementado en Python + Rust (en desarrollo), con 10 módulos base ya completados: contracts, schemas, event_bus, governance_engine, memory_fabric, session_scheduler, runtimes, observability, agent_registry y cognition.

La etapa de EVOLUCIÓN tiene tres tipos de tareas:
- CÓDIGO: implementar deuda técnica pendiente en los módulos existentes
- RESEARCH: investigar nuevas tecnologías con criterios formales (tech radar)
- MIGRACIÓN: continuar migrando documentación de MPAT3 a MPAT4

Para iniciar, necesito que hagas lo siguiente EN ORDEN:

PASO 1 — Leer el pointer activo:
Archivo: EVOLUTION_POINTER_ACTIVO.md
ID Drive: 11em7S3tPTe_5eRJfanRovJ_FoAoH9h8U

PASO 2 — Leer el work index:
Archivo: EVOLUTION_WORK_INDEX.md
ID Drive: 1GiVR07JDJO-Ad2qAkup6JhPRKrH-K87D

PASO 3 — Elegir un EV-RELAY:
Elegí uno LIBRE del EVOLUTION_POINTER que sea compatible con los tokens que tenemos.
Si tengo tokens > 60% → puedo tomar CÓDIGO o RESEARCH
Si tengo tokens 40-60% → tomar RESEARCH o MIGRACIÓN BAJA
Si tengo tokens < 40% → solo MIGRACIÓN BAJA, o solo actualizar índices

PASO 4 — Marcar en el WORK INDEX:
Antes de empezar: actualizar EVOLUTION_WORK_INDEX con mi nombre y el EV-RELAY tomado.

PASO 5 — Leer el prompt específico del EV-RELAY:
Si existe PROMPT_EV_RELAY_NNN.md en evolution/relay_evolution/, leerlo.
Si no existe, el EV-RELAY se inicia desde el EVOLUTION_POINTER y los archivos que lista.

PASO 6 — Ejecutar el trabajo:
- Tipo CÓDIGO: leer el contrato del módulo → implementar → guardar en la carpeta correcta
- Tipo RESEARCH: usar los 5 criterios de RESEARCH_INDEX → producir TECH_RADAR_[TEMA]_[FECHA].md
- Tipo MIGRACIÓN: seguir el protocolo del MIGRATION_LOG y LOTE_LIST

PASO 7 — Cerrar la sesión:
Actualizar EVOLUTION_POINTER_ACTIVO con el estado del EV-RELAY.
Actualizar EVOLUTION_WORK_INDEX con COMPLETADO o EN_CURSO.
Generar el mensaje de cierre (ver formato abajo).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORMATO DE MENSAJE DE CIERRE (pegar en el grupo del curso)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MPAT4 EVOLUTION · CIERRE DE SESIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alumno:         [ALUMNO_ID]
EV-RELAY:       EV_[NNN] — [descripción]
Tipo:           CÓDIGO / RESEARCH / MIGRACIÓN
Estado:         COMPLETADO / EN_CURSO (continuar desde [punto])
Artefactos:     [nombre archivo — ID Drive]
DT cerradas:    [lista de DT cerradas, o "ninguna"]
Siguiente libre: EV_[NNN] — [descripción] — Tipo: [tipo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIN DEL PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## SKILL REQUERIDO PARA ESTA ETAPA

El alumno debe tener instalado en Claude.ai: mpat4-alumno.skill (V1_03 o superior)
Y Google Drive MCP conectado.

La skill correcta para EVOLUTION es la SKILL PRINCIPAL (relay general MPAT4)
ID: 1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD

Para RESEARCH dentro de EVOLUTION: SKILL C (tech-research)
Para CÓDIGO dentro de EVOLUTION: SKILL D (python-rust-production)
Para MIGRACIÓN dentro de EVOLUTION: SKILL B (mpat3-to-mpat4)

---

*PROMPT_ALUMNO_EVOLUTION.md · evolution/relay_evolution/ · 2026-05-25*
*que has usado el formato de razonamiento adaptado por AGT*
