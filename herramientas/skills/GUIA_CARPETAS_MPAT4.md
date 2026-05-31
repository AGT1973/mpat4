# GUIA_CARPETAS_MPAT4.md
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Versión: V4_12 · Fecha: 2026-05-23
## Propósito: Referencia en español para alumnos — qué va en cada carpeta y dónde mover un archivo

---

## PARA QUÉ EXISTE ESTE ARCHIVO

Las carpetas de MPAT4 tienen nombres en inglés. Este documento existe para que cualquier alumno, independientemente de su nivel de inglés, pueda:

- Entender qué tipo de contenido vive en cada carpeta.
- Saber a dónde mover un archivo si no reconoce el nombre de la carpeta destino.
- Entender la lógica detrás de los directorios de descarte y por qué no deben eliminarse.

Si encontrás una carpeta cuyo nombre no reconocés, buscala en este documento antes de mover o crear cualquier archivo.

---

## MAPA DE CARPETAS — QUÉ SIGNIFICA CADA UNA

### `contracts/`
**Qué es:** contratos. Acuerdos escritos que definen qué debe hacer un módulo antes de que alguien escriba una línea de código.
**Qué va acá:** archivos `CONTRACT_[MODULO]_V1.md` y `CONTRACT_RUST_[MODULO]_V1.md`
**Regla clave:** ningún código puede existir sin un contrato aprobado en esta carpeta.

---

### `schemas/`
**Qué es:** esquemas. Definiciones formales de la estructura de los datos que el sistema usa.
**Qué va acá:** archivos `schema_[modulo].py` escritos en Python con Pydantic.
**Regla clave:** un schema depende de un contrato. Si no hay contrato, no hay schema.

---

### `resoluciones/`
**Qué es:** resoluciones. Decisiones técnicas o pedagógicas que el grupo tomó y que quedaron registradas formalmente.
**Qué va acá:** archivos `RES_NNN_[descripcion].md`
**Cuándo crear uno:** cuando el grupo discute algo y llega a un acuerdo que afecta el diseño del sistema o el funcionamiento del programa.

---

### `deprecated/`
**Qué es:** deprecado. Archivos que ya no están en uso activo pero que se conservan para referencia histórica.
**Qué va acá:** versiones antiguas de contratos, schemas o módulos que fueron reemplazados.
**Diferencia con trashcan:** deprecated tiene algo que fue válido en su momento y se reemplazó con un proceso ordenado. El trashcan tiene cosas que se descartaron durante la construcción.

---

### `relay/`
**Qué es:** el sistema de trabajo colaborativo entre alumnos.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `relay/active/` | el relay que está siendo trabajado ahora |
| `relay/temporal/` | borradores, trabajo en progreso sin cerrar (WIP) |
| `relay/pointer/` | el archivo RELAY_POINTER que indica dónde está el trabajo actualmente |
| `relay/docs/` | prompts listos para copiar al grupo para el próximo alumno |

**Regla clave:** un relay no se borra. Se cierra y se archiva. El pointer siempre se actualiza al terminar.

---

### `core/`
**Qué es:** el núcleo del sistema. Todo lo que hace que MPAT4 funcione.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `core/cognition/agents/` | lógica de agentes autónomos |
| `core/cognition/context/` | manejo de contexto en las conversaciones y sesiones |
| `core/cognition/kernel/` | núcleo cognitivo central |
| `core/cognition/orchestration/` | coordinación entre agentes y módulos |
| `core/cognition/planning/` | planificación de tareas y secuencias |
| `core/cognition/reasoning/` | módulos de razonamiento |
| `core/event_bus/` | el bus de eventos que conecta todos los módulos |
| `core/federation/` | comunicación entre sistemas distribuidos |
| `core/execution_graph/` | el grafo que define cómo se ejecutan las tareas |
| `core/governance/` | reglas y políticas del sistema |
| `core/memory/` | sistema de memoria externa del agente |
| `core/observability/` | monitoreo, logs, trazabilidad del sistema |
| `core/runtime/` | entorno de ejecución (Firecracker / NanoVMs / Unikraft) |
| `core/sandboxing/` | aislamiento seguro de módulos |
| `core/rust/parsers/` | parsers críticos escritos en Rust |
| `core/rust/codecs/` | codecs (codificación/decodificación) en Rust |
| `core/rust/hot_paths/` | rutas de código que se ejecutan con alta frecuencia, en Rust |
| `core/rust/ffi_bridges/` | puentes entre Python y Rust (FFI con PyO3) |
| `core/rust/types/` | definiciones de tipos de datos en Rust |
| `core/node_research/` | investigación de integración con Node.js (no producción) |

**Regla clave:** si el módulo toca memoria, parsing o rendimiento crítico → va en Rust. Si es lógica de agentes, orquestación o API → va en Python.

---

### `providers/`
**Qué es:** proveedores. Integraciones con servicios externos (APIs de IA, bases de datos, servicios en la nube).
**Qué va acá:** módulos que conectan MPAT4 con el mundo exterior.

---

### `ecosystem/`
**Qué es:** ecosistema. Herramientas, scripts y módulos que rodean al sistema principal pero no son parte del core.
**Qué va acá:** utilidades, adaptadores, conectores.

---

### `education/`
**Qué es:** carpeta educativa del programa.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `education/student_relays/` | copias de relays para uso educativo y seguimiento del grupo |

---

### `tests/`
**Qué es:** tests. Archivos que verifican que el código funciona correctamente.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `tests/unit/` | tests unitarios en Python (`test_[modulo].py`) |
| carpetas rust | tests de Rust van junto al código fuente en `core/rust/` |

---

### `research/`
**Qué es:** investigación. Material que explora ideas, tecnologías o decisiones que aún no están confirmadas para producción.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `research/benchmarks/` | comparaciones de rendimiento entre opciones |
| `research/experiments/` | experimentos técnicos en curso |
| `research/futures/` | ideas y propuestas para versiones futuras (`FUT_NNN_*.md`) |
| `research/papers/` | artículos académicos o técnicos de referencia |
| `research/tech_radar/` | evaluaciones de tecnologías nuevas (`TECH_RADAR_[FECHA].md`) |

---

### `deployment/`
**Qué es:** despliegue. Configuraciones y scripts para poner el sistema en producción.
**Qué va acá:** manifiestos de unikernel, configuraciones de red, scripts de arranque.

---

### `scripts/`
**Qué es:** scripts. Programas cortos de utilidad para tareas de mantenimiento o automatización.
**Qué va acá:** scripts de migración, limpieza, generación de datos de prueba.

---

### `docs/`
**Qué es:** documentación.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `docs/public/` | documentación legible para cualquier alumno o colaborador externo |

---

### `herramientas/`
**Qué es:** herramientas del programa. Skills y MCPs que Claude usa para trabajar en MPAT4.
**Subcarpetas:**

| Subcarpeta | Qué va acá |
|---|---|
| `herramientas/skills/` | archivos `.skill` y `.md` de skills del ecosistema |
| `herramientas/mcps/` | archivos `.py` de servidores MCP |

---

### `system_state/`
**Qué es:** estado del sistema. Snapshots del estado global del proyecto en un momento determinado.
**Qué va acá:** archivos de estado que permiten reconstruir el punto exacto en que estaba el proyecto.

---

## TRASHCAN, BORRA, _BORRAR — LO QUE PARECE BASURA NO LO ES

### Nombres que puede tener esta carpeta
En distintas versiones del programa esta carpeta puede llamarse:
- `trashcan/`
- `borra/`
- `_BORRAR/`

Todas cumplen la misma función y aplican las mismas reglas.

---

### Qué función cumple

Esta carpeta tiene **dos funciones simultáneas** que no se deben confundir:

**Función 1 — Descarte lógico**
Cuando un archivo es reemplazado por una versión mejor (un MASTER, un _UNIFICADO, un V3_01), el archivo anterior no se borra del sistema. Se mueve al trashcan con el protocolo de eliminación lógica. Esto garantiza que la historia del archivo queda registrada.

**Función 2 — Reserva de trazabilidad**
Si durante el trabajo aparece una brecha de documentación —una decisión que nadie recuerda cómo se tomó, un contrato con origen incierto, una regla que no tiene justificación visible— el trashcan es el primer lugar donde buscar. Los archivos descartados conservan el razonamiento que los hizo insuficientes, y ese razonamiento es información valiosa.

**En resumen:** el trashcan no es basura. Es el registro del proceso de decisión.

---

### Qué se puede y qué no se puede hacer con el trashcan

| Acción | ¿Permitida? | Motivo |
|---|---|---|
| Consultar un archivo para entender una decisión | Sí | Es la función de reserva de trazabilidad |
| Rescatar un concepto descartado para informar trabajo nuevo | Sí, con precaución | El concepto puede servir como referencia |
| Copiar un archivo del trashcan directamente a producción | No | El archivo fue descartado por una razón |
| Rescatar y reactivar un archivo sin revisión | No | Anularía el propósito del descarte lógico |
| Si un concepto del trashcan resulta necesario | Se reconstruye desde cero | Nueva autoría, nuevo número de versión, informado por el trashcan |
| Eliminar el trashcan para "limpiar" el Drive | No | Se perdería la trazabilidad de decisiones |

---

### Diferencia entre trashcan y deprecated

| | `trashcan/` | `deprecated/` |
|---|---|---|
| Qué contiene | archivos descartados durante la construcción | archivos reemplazados en proceso ordenado |
| Por qué se guardó | protocolo de eliminación lógica | migración planificada a versión nueva |
| Puede consultarse | sí, para rastrear decisiones | sí, para entender evolución del sistema |
| Puede reactivarse directamente | no | no sin revisión |

---

## REGLA GENERAL — QUÉ HACER SI NO SABÉS DÓNDE VA UN ARCHIVO

1. Buscá el tipo de artefacto en la ROUTING_MATRIX del skill `mpat4-relay`.
2. Si el nombre de la carpeta destino no lo entendés, buscalo en este documento.
3. Si el tipo de artefacto no está en la ROUTING_MATRIX ni en este documento, **no muevas el archivo solo**. Dejalo en `relay/temporal/` con una nota y avisá al grupo o al docente.
4. Nunca creés una carpeta nueva sin registrar el ID en el relay y avisar al docente para actualizar el MCP.

---

*GUIA_CARPETAS_MPAT4.md · AGT 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*