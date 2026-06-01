# RESEARCH_INDEX — Investigaciones Pendientes MPAT4
## Creado: 2026-05-25 | Carpeta: research/ (ID: 1J-kQK4hh-Nj7ufr0P-4AYQVvTx-in_8S)
## Propósito: mapa de investigaciones tech radar para la etapa de evolución

---

## INSTRUCCIÓN DE USO

Cada EV-RELAY de tipo RESEARCH produce un archivo TECH_RADAR_[TEMA]_[FECHA].md
y lo guarda en esta carpeta.
Si la investigación concluye en adopción, también produce RESOLUCION_TECH_[NOMBRE].md.

Al cerrar una investigación, actualizar la tabla de abajo con el ID del archivo producido.

---

## INVESTIGACIONES PENDIENTES

| ID_INV | Pregunta clave | EV-RELAY | Prioridad | Estado | Alumno | Artefacto |
|---|---|---|---|---|---|---|
| INV-EV-001 | gRPC vs ConnectRPC: cuál adoptar como protocolo interno MPAT4 para reemplazar REST puro | EV_006 | ALTA | LIBRE | — | — |
| INV-EV-002 | Python 3.14 No-GIL: ¿qué impacto tiene en cognition_engine.py y event_bus.py? ¿Vale el upgrade ya? | EV_007 | MEDIA | LIBRE | — | — |
| INV-EV-003 | Pydantic V3: ¿qué rompe en los 9 schemas actuales? ¿Cuánto esfuerzo de migración? | EV_008 | MEDIA | LIBRE | — | — |
| INV-EV-004 | NanoVMs vs Firecracker: comparación real para runtimes/ de MPAT4 (DT-UK-001) | EV_009 | ALTA | LIBRE | — | — |
| INV-EV-005 | A2A v1.0 (agent-to-agent protocol): ¿cómo se integra con event_bus/ y agent_registry/? | EV_010 | MEDIA | LIBRE | — | — |
| INV-EV-006 | ShadowRadix (incorporado Capa 5): ¿documentación suficiente? ¿Precisa formalización en MPAT4? | pendiente | BAJA | LIBRE | — | — |
| INV-EV-007 | MCP (Model Context Protocol) v2: ¿cambios que afectan CAPA_07 MCPAppsRenderer? | pendiente | MEDIA | LIBRE | — | — |

---

## INVESTIGACIONES COMPLETADAS

| ID_INV | Tema | Alumno | Fecha | Decisión | Artefacto ID |
|---|---|---|---|---|---|
| (vacío al inicio) | | | | | |

---

## CRITERIOS DE EVALUACIÓN (5 obligatorios)

Todo TECH_RADAR debe evaluar la tecnología contra estos 5 criterios:
1. Compatibilidad con arquitectura unikernel (sin Docker)
2. Compatibilidad con Python 3.x (o Rust donde aplique)
3. Impacto en módulos P1-P10 existentes
4. Complejidad de adopción (esfuerzo estimado en relays)
5. Riesgo de adopción (regresiones, breaking changes)

Decisión final: ADOPT / TRIAL / ASSESS / HOLD

---

*RESEARCH_INDEX.md · MPAT4 · research/ · 2026-05-25*
*que has usado el formato de razonamiento adaptado por AGT*
