# SESSION_SCHEDULER_CONTRACT_V4_01.md
## Autor: cursos.agt.ia@gmail.com · 2026-05-13
## Módulo: session_scheduler/ · Versión: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Basado en: RELAY_007.md (ariel.garcia.traba@gmail.com)

---

## 1. OBJETIVO

El `session_scheduler` controla el ciclo de vida completo de las sesiones cognitivas en MPAT4.
No es un despachador de tareas ni un scheduler de trabajos. Es el módulo que decide:

- **CUÁNDO** nace una sesión (spawn): validando presupuesto, identidad, runtime disponible.
- **CON QUÉ recursos**: presupuesto de tokens, tipo de runtime (nanovm/unikraft/firecracker), TTL.
- **CUÁNTO vive**: TTL configurable, con warning al 80% y teardown automático al expirar.
- **CÓMO se suspende y reactiva**: hydrate/checkpoint preservan el estado cognitivo en Redis.
- **CUÁNDO muere**: teardown por budget, TTL, cierre explícito, violación de policy o error.

Sin session_scheduler, los agentes vivirían indefinidamente, consumirían recursos sin límite
y nunca liberarían memoria. Esto viola P7 (budget inviolable), P3 (zero trust / aislamiento)
y P12 (cognición efímera-persistente).

**Límite de responsabilidad:**
- session_scheduler NO ejecuta lógica de agente.
- session_scheduler NO decide qué hace el agente dentro de la sesión.
- session_scheduler NO gestiona memoria semántica (eso es memory_fabric/).
- session_scheduler SÍ persiste y transiciona SessionState en Redis.
- session_scheduler SÍ emite eventos al event_bus en cada transición.

---

## 2. INVARIANTES

| ID         | Invariante                                                                                  | Consecuencia si se rompe            |
|------------|--------------------------------------------------------------------------------------------|--------------------------------------|
| INV-SCH-001 | `tenant_id` vacío en spawn() → rechazar + emitir `session.rejected`                      | Sesiones sin tenant son anónimas e inauditables |
| INV-SCH-002 | `budget=0` en spawn() → rechazar + emitir `session.budget_insufficient`                  | Agente sin presupuesto no puede operar |
| INV-SCH-003 | `runtime_type` no en `allowed_runtimes` de config_policy.yaml → rechazar               | Protege contra Docker y runtimes no auditados |
| INV-SCH-004 | Si ya existe sesión ACTIVE con mismo `ecs_id` → rechazar spawn() nuevo                  | Evita duplicación de contexto cognitivo |
| INV-SCH-005 | `teardown()` persiste checkpoint ANTES de destruir el runtime                            | Sin checkpoint previo, el conocimiento se pierde |
| INV-SCH-006 | `SessionState` se persiste en Redis al INICIO de cada transición de phase               | Si cae el sistema mid-transición, el estado es recuperable |

**Restricciones adicionales (no negociables):**
- NUNCA Docker. Runtimes válidos: `nanovm`, `unikraft`, `firecracker`.
- NUNCA importar directamente desde otros módulos (governance_engine, memory_fabric).
  Toda comunicación vía event_bus (P9).
- NUNCA instanciar SessionScheduler directamente. Usar `get_session_scheduler()` (singleton).
- NUNCA código de este módulo en schemas/ — y NUNCA schema en session_scheduler/.

---

## 3. MÉTODOS PÚBLICOS

### `spawn(request: SpawnRequest) -> SessionState`

Crea una nueva sesión cognitiva.

```
PRECONDICIONES:
  - request.tenant_id no vacío (INV-SCH-001)
  - budget disponible > 0 (INV-SCH-002) — verificar con governance_engine via event_bus
  - request.runtime_type in allowed_runtimes (INV-SCH-003)
  - sin sesión ACTIVE con mismo ecs_id (INV-SCH-004)

POSTCONDICIONES:
  - SessionState en Redis con phase=ACTIVE
  - Evento session.spawned emitido
  - Si warm_start=True: memory_fabric.warm_start ejecutado via event_bus
```

### `hydrate(session_id: UUID) -> SessionState`

Reactiva una sesión SUSPENDED. Carga checkpoint_data de Redis y transiciona a ACTIVE.

### `suspend(session_id: UUID) -> SessionState`

Suspende una sesión ACTIVE. Persiste checkpoint_data. Transiciona a SUSPENDED.

### `teardown(session_id: UUID, reason: TeardownReason) -> None`

Destruye una sesión. INV-SCH-005: checkpoint ANTES de destruir. Transiciona TEARDOWN → TERMINATED.
Libera claves Redis. Emite session.terminated.

### `checkpoint(session_id: UUID) -> None`

Serializa el estado cognitivo actual. Persiste en Redis bajo `session:{tenant_id}:{session_id}:checkpoint`.
Emite session.checkpointed.

---

## 4. ESTRUCTURA SessionState

| Campo                | Tipo              | Requerido | Descripción                                           |
|----------------------|-------------------|-----------|-------------------------------------------------------|
| `session_id`         | UUID4             | SÍ        | Identificador único de sesión                         |
| `tenant_id`          | str (min_len=1)   | SÍ        | Tenant dueño de la sesión                             |
| `ecs_id`             | UUID4             | SÍ        | ECS vinculado a esta sesión                           |
| `phase`              | SessionPhase      | SÍ        | Estado actual: COLD→SPAWNING→ACTIVE→SUSPENDED→TEARDOWN→TERMINATED |
| `runtime_type`       | str               | SÍ        | `nanovm` (default), `unikraft`, `firecracker`         |
| `spawned_at`         | datetime \| None  | NO        | Timestamp de SPAWNING                                 |
| `suspended_at`       | datetime \| None  | NO        | Timestamp de última suspensión                        |
| `terminated_at`      | datetime \| None  | NO        | Timestamp de TERMINATED                               |
| `ttl_seconds`        | int (gt=0)        | SÍ        | Duración máxima en segundos (default: 3600)           |
| `checkpoint_data`    | dict              | NO        | Estado cognitivo serializado                          |
| `budget_at_spawn`    | int (ge=0)        | SÍ        | Presupuesto al momento de spawn (auditoría)           |

---

## 5. CAMPOS DE CONFIGURACIÓN

Leídos desde `config_policy.yaml` → sección `session_scheduler`:

| Campo                              | Tipo | Default | Descripción                                          |
|------------------------------------|------|---------|------------------------------------------------------|
| `max_session_duration_seconds`     | int  | 3600    | TTL máximo absoluto por sesión                       |
| `warm_pool_size`                   | int  | 3       | Sesiones pre-calentadas disponibles                  |
| `cold_boot_timeout_seconds`        | int  | 10      | Timeout para arrancar un runtime cold                |
| `checkpoint_interval_seconds`      | int  | 300     | Frecuencia de checkpoint automático                  |
| `max_concurrent_sessions_per_tenant`| int | 5      | Límite de sesiones simultáneas por tenant            |
| `allowed_runtimes`                 | list | [nanovm, unikraft, firecracker] | Runtimes permitidos (sin Docker) |
| `ttl_warning_threshold`            | float| 0.8     | % de TTL para emitir session.ttl_warning             |

---

## 6. FLUJO spawn()

```
SpawnRequest recibido
        │
        ▼
[INV-SCH-001] tenant_id vacío?
        │ SÍ → emitir session.rejected → retornar error
        │ NO ↓
[INV-SCH-002] budget disponible?  (event → governance_engine)
        │ NO → emitir session.budget_insufficient → retornar error
        │ SÍ ↓
[INV-SCH-003] runtime_type válido?
        │ NO → emitir session.rejected (runtime inválido) → retornar error
        │ SÍ ↓
[INV-SCH-004] sesión ACTIVE con mismo ecs_id?
        │ SÍ → emitir session.rejected (duplicada) → retornar error
        │ NO ↓
[INV-SCH-006] Crear SessionState (phase=SPAWNING) → persistir en Redis
        │
        ▼
warm_start=True? → memory_fabric.warm_start via event_bus
        │
        ▼
Actualizar phase=ACTIVE → persistir en Redis (INV-SCH-006)
        │
        ▼
Emitir session.spawned → retornar SessionState
```

---

## 7. FLUJO teardown()

```
teardown(session_id, reason) recibido
        │
        ▼
Cargar SessionState desde Redis
        │
        ▼
[INV-SCH-006] Actualizar phase=TEARDOWN → persistir en Redis
        │
        ▼
[INV-SCH-005] checkpoint() → serializar estado → guardar en Redis
        │
        ▼
Liberar recursos del runtime (stop nanovm / unikraft / firecracker)
        │
        ▼
[INV-SCH-006] Actualizar phase=TERMINATED, terminated_at=now() → persistir
        │
        ▼
Remover session_id del Set active_sessions en Redis
        │
        ▼
Emitir session.terminated (session_id, reason, ts)
```

---

## 8. EVENTOS QUE EMITE

| Evento                      | Cuándo se emite                          | Payload mínimo                               |
|-----------------------------|------------------------------------------|----------------------------------------------|
| `session.spawned`           | spawn() exitoso, phase=ACTIVE            | session_id, tenant_id, ecs_id, ts            |
| `session.rejected`          | spawn() rechazado (cualquier validación) | tenant_id, ecs_id, reason, ts                |
| `session.suspended`         | suspend() completado                     | session_id, tenant_id, ts                    |
| `session.hydrated`          | hydrate() completado                     | session_id, tenant_id, ts                    |
| `session.checkpointed`      | checkpoint() completado                  | session_id, tenant_id, ts                    |
| `session.terminated`        | teardown() completado                    | session_id, reason, ts                       |
| `session.budget_insufficient`| spawn() con budget=0                    | tenant_id, ecs_id, ts                        |
| `session.ttl_warning`       | 80% del TTL consumido                    | session_id, remaining_sec, ts                |

---

## 9. ESQUEMA REDIS

| Clave                                          | Tipo   | TTL      | Contenido                            |
|------------------------------------------------|--------|----------|--------------------------------------|
| `session:{tenant_id}:{session_id}:state`       | String | ttl_seconds | SessionState serializado (JSON)   |
| `session:{tenant_id}:{session_id}:checkpoint`  | String | Sin TTL  | dict con estado cognitivo            |
| `session:{tenant_id}:active_sessions`          | Set    | Sin TTL  | Set de session_ids activos           |
| `session:{tenant_id}:stats`                    | Hash   | Sin TTL  | spawned, terminated, suspended, etc. |

**Reglas Redis:**
- El state key tiene TTL igual a ttl_seconds de la sesión.
- El checkpoint key NO tiene TTL (sobrevive al runtime — P12).
- El Set active_sessions se limpia en teardown().

---

## 10. DEUDA TÉCNICA Y RIESGOS

| ID        | Descripción                                                           | Impacto | Quién resuelve |
|-----------|-----------------------------------------------------------------------|---------|----------------|
| DT-SCH-001 | Sin tests de integración para session_scheduler.py                  | Medio   | RELAY_008+     |
| DT-SCH-002 | warm_pool_size no implementado (sesiones pre-calentadas)             | Bajo    | RELAY_008+     |
| DT-SCH-003 | TTL monitoring no tiene worker background — solo lazy check           | Medio   | RELAY_008+     |
| DT-SCH-004 | checkpoint_interval_seconds definido pero sin loop automático        | Medio   | RELAY_008+     |
| RIESGO-SCH-001 | Redis sin AOF/RDB — state y checkpoint se pierden en restart     | Alto    | Coordinador infra |
| RIESGO-SCH-002 | governance_engine comunicado via event_bus: latencia no medida   | Bajo    | observability/ |

---

*SESSION_SCHEDULER_CONTRACT_V4_01.md · cursos.agt.ia@gmail.com · 2026-05-13*
*Módulo: session_scheduler/ · Sistema: MPAT4 — Infraestructura Cognitiva Distribuida*
*que has usado el formato de razonamiento adaptado por AGT*
