---
name: mpat4-relay
description: >
  Skill de trabajo colaborativo relay para MPAT4 — Infraestructura Cognitiva
  Distribuida. Activar SIEMPRE cuando el alumno diga ".", "continuar",
  "continuar con mpat4", "seguimos", "siguiente pendiente", "retomar mpat4",
  o al inicio de sesión si hay contexto MPAT4 presente. También activar si el
  alumno menciona relay, RELAY_POINTER, módulo pendiente, o pide trabajar en
  contracts, schemas, event_bus, governance, memory, observability,
  agent_registry o cognition. NO esperar que el alumno nombre el skill
  explícitamente — si el contexto es MPAT4, activar.
compatibility: Google Drive MCP requerido
---

# MPAT4 — Skill Relay Colaborativo

## Qué hace este skill

Un alumno dice "continuar". El skill hace todo lo demás:

1. Identifica al alumno (ALUMNO_ID)
2. Lee el estado real desde Drive (nunca confía en memoria)
3. Verifica firma del relay anterior
4. Toma control del trabajo en relay/temporal/
5. Verifica el estado real del módulo activo en Drive
6. Genera el artefacto correspondiente
7. Lo guarda firmado en Drive
8. Cierra con los 3 artefactos obligatorios

**El estado vive en Drive, no en la memoria de Claude.**

---

## Reglas absolutas — leer antes de cualquier acción

- **NUNCA** Google Doc — siempre `text/plain` + `disableConversionToGoogleType: true`
- **NUNCA** sobreescribir — crear versión nueva, renombrar original a `nombre.old.ext`
- **NUNCA** código sin contrato aprobado
- **NUNCA** schema sin contrato
- **NUNCA** Docker — solo Firecracker / NanoVMs / Unikraft
- **NUNCA** cerrar sin los 3 artefactos de cierre
- **NUNCA** relay sin las 10 secciones
- **SIEMPRE** encabezado firmado en cada archivo generado
- **SIEMPRE** Drive gana sobre lo que dice el relay

**Error "No approval received" en .py largo:** dividir en partes.
Si persiste: guardar como .md provisional + nota en relay.

---

## Configuración de rutas

Este skill NO maneja IDs de Drive directamente.
Usa el **MCP MPAT4** para resolver rutas semánticas a IDs reales.

Rutas semánticas principales:
```
mpat/                     ← raíz del proyecto
mpat/mpat4/               ← raíz MPAT4
mpat/mpat4/relay/         ← zona operativa de relays
mpat/mpat4/relay/temporal/← mesa de trabajo limpia
mpat/mpat4/contracts/     ← contratos de módulos
mpat/mpat4/schemas/       ← schemas Pydantic
mpat/mpat4/resoluciones/  ← resoluciones arquitecturales
mpat/mpat4/docs/          ← documentación
mpat/mpat4/research/      ← investigaciones y papers
mpat/mpat4/research/papers/
mpat/mpat4/research/benchmarks/
mpat/mpat4/research/experiments/
mpat/mpat4/research/fut/
mpat/mpat4/core/cognition/
mpat/mpat4/core/event_bus/
mpat/mpat4/core/governance/
mpat/mpat4/core/memory/
mpat/mpat4/core/observability/
mpat/mpat4/core/federation/
mpat/mpat4/core/execution_graph/
mpat/mpat4/core/runtime_core/
mpat/mpat4/core/sandboxing/
```

Para resolver cualquier ruta a su ID real, llamar al MCP MPAT4:
`mcp_mpat4.resolve_path("mpat/mpat4/contracts/")`

Si el MCP MPAT4 no está disponible, leer el archivo
`mpat/herramientas/mcps/folder_ids.json` desde Drive como fallback.

---

## Flujo de sesión — 6 pasos

### PASO 0 — Identificación del alumno

Preguntar: **"¿Nombre o email para registrar tu autoría en MPAT4?"**

Guardar como `ALUMNO_ID`. Usar en el encabezado de TODOS los archivos.
Aceptar cualquier identificador: email, nombre, apodo.
Registrar en `RELAY_NNN+1.md` y en `RELAY_POINTER`.

---

### PASO 1 — Leer estado y tomar control

1. Buscar `RELAY_POINTER_V4*.md` más reciente en `mpat/mpat4/relay/`
2. Actualizar RELAY_POINTER: poner ALUMNO_ID como "trabajando", estado `EN_PROGRESO`
3. Copiar trabajo a `mpat/mpat4/relay/temporal/` — mesa de trabajo limpia
4. **Verificar firma del relay anterior:**
   - Firmado → continuar normalmente
   - Sin firma → alumno anterior sin tokens. Informar: `"⚠️ RELAY_[NNN] sin firma — completando trabajo previo desde temporal/"`. Cerrar ese relay antes de abrir uno nuevo.
5. Leer `RELAY_NNN.md` activo
6. Informar: `"Relay activo: RELAY_[NNN] — [descripción breve]"`

---

### PASO 2 — Verificar estado real en Drive

- Listar archivos en la carpeta del módulo activo
- **NO confiar en el relay** — Drive siempre gana
- Si Drive difiere del relay → creer a Drive, documentar discrepancia en sección 10 del cierre
- Registrar: qué contratos, schemas, implementaciones y tests existen realmente

---

### PASO 3 — Cargar solo lo necesario

Leer en este orden y nada más:

1. RELAY_POINTER — qué módulo trabajar
2. RELAY_NNN.md activo — tarea exacta
3. Contrato del módulo activo (si existe)
4. Schemas relacionados (si existen)

No cargar módulos no relacionados — economía de tokens.

---

### PASO 4 — Generar artefacto según estado

| Estado del módulo | Artefacto |
|---|---|
| Sin contrato | `CONTRACT_V1.md` — 10 secciones |
| Sin schema | `schema.py` — Pydantic V3 |
| Sin implementación | módulo Python con invariantes |
| Sin tests | suite de tests unitarios |
| Todo completo | investigación en `research/` o resolución de deuda técnica |

#### Encabezado obligatorio en cada archivo:
```
# [NOMBRE_ARCHIVO]
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [módulo] · Versión: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
```

#### Leyes arquitecturales — aplican a todo código:
- Runtime: Firecracker / NanoVMs / Unikraft — NUNCA Docker
- Comunicación: subsistema → Event Bus → subsistema — NUNCA directa
- Memoria: siempre externa en Memory Fabric — NUNCA en runtime
- Todo skill: sandboxeable
- Todo relay: serializable

#### Tecnologías V3 migradas a V4 — dónde viven:

| Tecnología V3 | Módulo V4 | Carpeta |
|---|---|---|
| A2A v1.0 | federation | `core/federation/` |
| SubQ (Sub-Queue) | event_bus | `core/event_bus/streams/` |
| ShadowRadix / CSA | execution_graph | `core/execution_graph/planner/` |
| NHP Protocol | sandboxing | `core/sandboxing/seccomp/` |
| Dream Cycle RMH | memory | `core/memory/consolidation/` |
| Unikernel por usuario | runtime_core | `core/runtime_core/unikernel/` |
| policy.yaml governance | governance | `core/governance/policies/` |
| eBPF / QUIC | federation | `core/federation/relay_exchange/` |
| MCPAppsRenderer | ecosystem | `ecosystem/skills/` |

Si un módulo de esta tabla no tiene contrato aún → es trabajo pendiente para el alumno.

---

### PASO 5 — Guardar en Drive

- Guardar solo en carpeta del módulo activo + `relay/`
- Siempre `disableConversionToGoogleType: true`
- Si el archivo ya existe: crear versión nueva → renombrar original a `.old.ext`
- Registrar ID de Drive de cada archivo (va en sección 2 del relay de cierre)

---

### PASO 6 — Cierre

#### Token check — ejecutar antes de decidir:
- **> 60% restantes** → continuar con sub-tarea del mismo relay
- **< 60% restantes** → preparar cierre
- **< 40% restantes** → CERRAR AHORA, nada más

#### 3 artefactos obligatorios de cierre:

**6a.** `relay/RELAY_NNN+1.md` — 10 secciones completas
**6b.** `RELAY_POINTER_V4_ACTUALIZADO_[FECHA].md` — en `mpat/mpat4/relay/`
**6c.** `docs/PROMPT_ALUMNO_RELAY_NNN+1.md` — prompt listo para copiar al grupo

---

## Estructura del relay — 10 secciones obligatorias

```markdown
# RELAY_NNN.md
## Autor: [ALUMNO_ID] · [FECHA]
## Módulo: [módulo] · Sistema: MPAT4
## Relay anterior: RELAY_NNN-1.md — [firmado por: ALUMNO_ID_ANTERIOR]

[APERTURA] módulo activo, prioridad, situación al iniciar

[INFO_ALUMNO] qué leer primero · qué NO tocar · IDs clave

1. OBJETIVO DE ESTA SESIÓN
   Qué se hizo efectivamente (no qué se intentó).

2. ARTEFACTOS CREADOS
   | archivo | carpeta semántica | ID Drive | estado |

3. SCHEMAS DEFINIDOS
   | archivo | clases | ID Drive | invariantes clave |

4. EVENTOS DEFINIDOS
   | tipo_evento | clase | cuándo se emite |

5. DECISIONES ARQUITECTURALES
   DEC-NNN: decisión → razón → consecuencia

6. RIESGOS DETECTADOS
   RIESGO-NNN: descripción → impacto → mitigación
   Estado: Activo | Heredado | Resuelto

7. PRÓXIMA PRIORIDAD
   Módulo + tarea exacta + precondiciones + IDs necesarios

8. ARCHIVOS CRÍTICOS A LEER PRIMERO
   | archivo | ID Drive | por qué es crítico |

9. INVARIANTES — NO ROMPER
   Lista completa y explícita. No "ver contrato".

10. DEUDA TÉCNICA
    | ítem | motivo | prioridad | quién resuelve |

[TRASPASO → RELAY_NNN+1]
Mensaje listo para copiar al grupo de alumnos.
Firmado: [ALUMNO_ID] · [FECHA]
```

---

## Estructura del contrato — 10 secciones obligatorias

```markdown
1. OBJETIVO
2. MOTIVACIÓN ARQUITECTURAL
3. CAMPOS / INTERFACE — tabla con tipos Pydantic
4. EVENTOS QUE EMITE — tipo | payload mínimo
5. EVENTOS QUE CONSUME
6. FLUJO OPERACIONAL — pasos numerados + ramas de error
7. INVARIANTES — INV-XXX-NNN
8. RIESGOS — tabla con impacto y mitigación
9. OBSERVABILIDAD — Redis + OTel + métricas mínimas
10. SIGUIENTE ALUMNO — tarea exacta + archivos + qué no tocar
```

---

## Research — cuándo y cómo abrir una investigación

Una investigación se abre en `mpat/mpat4/research/` cuando:

**A. El docente la asigna** — aparece en el relay como tarea explícita
**B. El sistema la detecta** — al revisar un módulo falta tecnología o hay decisión pendiente
**C. El alumno la encuentra** — al codificar topa con un problema real (incompatibilidad, tecnología no resuelta, decisión arquitectural sin precedente)

### Tipos y carpetas:

| Tipo | Carpeta | Cuándo |
|---|---|---|
| Paper nuevo relevante para V4/V5 | `research/papers/` | Siempre no bloqueante |
| Propuesta de feature para V5 | `research/fut/` | Siempre no bloqueante |
| Comparación técnica (A vs B) | `research/benchmarks/` | Siempre no bloqueante |
| Problema bloqueante de implementación | `research/experiments/` | Puede bloquear relay |

### Si la investigación es bloqueante:
1. Pausar el relay activo
2. Crear `RESEARCH_NNN_[TEMA].md` en `research/experiments/`
3. Documentar en sección 10 del relay: deuda técnica abierta, bloqueante
4. El relay no avanza hasta que otro alumno resuelva la investigación y publique en `resoluciones/`

### Si no es bloqueante:
1. Crear `RESEARCH_NNN_[TEMA].md` en la subcarpeta correspondiente
2. Documentar en sección 10 del relay: investigación abierta, no bloqueante
3. Continuar el relay normalmente

### Encabezado de toda investigación:
```
# RESEARCH_NNN_[TEMA].md
## Autor: [ALUMNO_ID] · [FECHA]
## Origen: docente | sistema | código
## Tipo: paper | fut | benchmark | experiment
## Estado: abierta | en_progreso | resuelta
## Bloqueante: sí [módulo bloqueado] | no
## Módulo relacionado: [módulo]
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
```

---

## Protocolo de traspaso

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MPAT4 · TRASPASO AL SIGUIENTE ALUMNO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Cerrado por:    [ALUMNO_ID]
  Fecha:          [FECHA]
  RELAY:          RELAY_[NNN]
  Completado:     [descripción concreta]
  Próximo:        RELAY_[NNN+1] — [descripción]
  Archivos clave: [lista con IDs Drive]
  Deuda abierta:  [si hay, describirla]

  COPIAR AL GRUPO:
  "Terminé RELAY_[NNN] en MPAT4.
   Hice: [tarea].
   Próximo: RELAY_[NNN+1].
   Firmado: [ALUMNO_ID] · [FECHA]"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Qué va en cada carpeta de MPAT4

| Carpeta | Qué contiene | Quién escribe | Formato |
|---|---|---|---|
| `relay/` | RELAY_NNN.md activos + RELAY_POINTER | alumno al cerrar | .md |
| `relay/temporal/` | trabajo en progreso de la sesión activa | alumno durante sesión | cualquiera |
| `contracts/` | contratos de módulos (10 secciones) | alumno al iniciar módulo | .md |
| `schemas/` | schemas Pydantic V3 | alumno después de contrato | .py |
| `resoluciones/` | resoluciones de decisiones arquitecturales | alumno al resolver deuda | .md |
| `docs/public/` | documentación pública del proyecto | alumno o docente | .md |
| `docs/internal/` | notas internas, topología, índices | docente o coordinador | .md .json |
| `docs/architecture/` | diagramas y decisiones de arquitectura | alumno con DEC-NNN | .md |
| `research/papers/` | análisis de papers con recomendación | alumno o docente | .md |
| `research/fut/` | propuestas de features para V5 | cualquiera | .md |
| `research/benchmarks/` | comparaciones técnicas (A vs B) | alumno | .md |
| `research/experiments/` | prototipos y problemas bloqueantes | alumno | .md .py |
| `core/*/` | implementación real de módulos | alumno después de contrato+schema | .py |
| `tests/unit/` | tests unitarios por módulo | alumno al completar impl. | .py |
| `tests/integration/` | tests de integración entre módulos | alumno avanzado | .py |
| `deprecated/` | archivos obsoletos renombrados | sistema (automático) | cualquiera |
| `scripts/bootstrap/` | scripts de setup del proyecto | docente | .py |
| `system_state/` | snapshots del estado del sistema | skill al cerrar relay | .json .md |

---

## Notas de migración V3 → V4

- V3: trabajo por capas (CAPA_01 a CAPA_14) en `mpat/mpat3/`
- V4: trabajo por módulos de infraestructura cognitiva en `mpat/mpat4/`
- Las tecnologías resueltas en V3 se migran a V4 cuando tienen contrato aprobado
- La migración es un relay propio: `RELAY_NNN_MIGRACION_[TECNOLOGIA].md`
- Orden inmutable por módulo: Contrato → Schema → Implementación → Tests → Memory Fabric
- Sin contrato aprobado el módulo no avanza
- El runtime es efímero: nace → hidrata memoria → ejecuta → exporta relay → muere
