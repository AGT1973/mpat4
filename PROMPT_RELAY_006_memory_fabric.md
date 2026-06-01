# PROMPT\_RELAY\_006 — memory\_fabric/

## Para: próximo alumno MPAT4

## Generado por: [clases.andrea.biologia@gmail.com](mailto:clases.andrea.biologia@gmail.com) · 2026-05-13

## Basado en: RELAY\_005.md

---

## TU IDENTIDAD Y ROL

Sos el próximo alumno del proyecto MPAT4 trabajando en modo relay. El estado del sistema vive en Google Drive. Vos no empezás desde cero: arrancás exactamente donde dejó Andrea.

**Tu primera acción obligatoria:** identificarte con tu email antes de escribir cualquier archivo. Todos los artefactos llevan firma de autor.

---

## PASO 0 — LEER ANTES DE HACER NADA

Leer en este orden exacto desde Google Drive (carpeta raíz MPAT4): `1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI`

1. `relay/RELAY_005.md` — ID: `1VWqeV34zbDlFkS6JFr8hCqsrPLcrQTTx`  
2. `governance_engine/GOVERNANCE_ENGINE_CONTRACT_V4_01.md` — ID: `15fO8p9EEAbkMtBwH-7cpvaLDzUOm4iNT`  
3. `governance_engine/governance_schema.py` — ID: `1T_FdXr99PEByFvAFKLThQmi9F4JOW7u9`  
4. `governance_engine/governance_engine.py` — ID: `1H3haE06cNMx8dM0t-4a5y31AtxZVc2ja`  
5. `schemas/ecs_schema.py` — ID: `1pWlab26bxU5PclYOCl0JxN2TuA3ZpeoQ`  
6. `event_bus/event_bus.py` — ID: `1fFaLWnpG0hGtCpZcXPuBed9aHsKuz4C-`

NO escribas ningún archivo hasta haber leído todos estos.

---

## ESTADO ACTUAL DEL SISTEMA (al iniciar RELAY\_006)

| Prioridad | Módulo | Contrato | Schema | Implementación |
| :---- | :---- | :---- | :---- | :---- |
| 1 | contracts/ | ✅ ECS\_CONTRACT\_V1.md | — | — |
| 2 | schemas/ | ✅ | ✅ ecs\_schema \+ event\_schema \+ event\_bus\_schema | ✅ |
| 3 | event\_bus/ | ✅ EVENT\_BUS\_CONTRACT\_V4\_01 | ✅ | ✅ event\_bus.py (635 líneas, Redis Streams, 8 invariantes) |
| 4 | governance\_engine/ | ✅ GOVERNANCE\_ENGINE\_CONTRACT\_V4\_01 | ✅ governance\_schema.py | ✅ config\_policy.yaml \+ budget\_engine.py \+ governance\_engine.py |
| **5** | **memory\_fabric/** | ❌ | ❌ | ❌ |
| 6–10 | resto | ❌ | ❌ | ❌ |

**Tu módulo: `memory_fabric/` — Prioridad 5** ID carpeta Drive: `1ovXyzv6zkDu4OGW7JDLJXzD9M9uB2bXl`

---

## REVISIÓN DE CÓDIGO — OBLIGATORIA ANTES DE IMPLEMENTAR

Antes de escribir una sola línea de memory\_fabric, verificá estos puntos en el código existente. Si encontrás una violación, generá una resolución formal en `resoluciones/` (ID: `16VKDIKpDO8sWa6NxI3sGFbWlN3QHP8fj`) y avisá al coordinador. NO parchés silenciosamente código de otros alumnos.

### Checklist de revisión (verificar en el código ya existente)

**event\_bus.py**

- [ ] INV-BUS-001: emit() rechaza tenant\_id vacío → buscar la guarda al inicio de emit()  
- [ ] INV-BUS-002: emit() rechaza event\_type no en ALL\_EVENT\_TYPES  
- [ ] INV-BUS-003: \_stream\_key() siempre incluye tenant\_id en el namespace  
- [ ] INV-BUS-004: handlers aislados con asyncio.create\_task \+ gather(return\_exceptions=True)  
- [ ] INV-BUS-005: event\_bus.py NO importa ningún módulo de dominio (grep imports)  
- [ ] INV-BUS-006: model\_dump\_json() en serialización (no model\_dump() sin json)  
- [ ] INV-BUS-007: parámetros desde config (no hardcodeados)  
- [ ] INV-BUS-008: payload entregado exacto al handler sin transformar  
- [ ] get\_event\_bus() singleton implementado

**governance\_schema.py**

- [ ] GovernanceDecision tiene `model_config = ConfigDict(frozen=True)` — INV-GOV-006  
- [ ] BudgetState tiene `model_validator` que recomputa status automáticamente  
- [ ] PolicyConfig tiene `model_config = ConfigDict(frozen=True)`  
- [ ] AuditEntry tiene `model_config = ConfigDict(frozen=True)`  
- [ ] Todos los Enum heredan de `str, Enum`

**budget\_engine.py**

- [ ] INV-GOV-001: consume() llama a \_signal\_exceeded() cuando budget\_spent \>= budget\_total  
- [ ] INV-GOV-005: \_require\_tenant() al inicio de get\_state() y consume()  
- [ ] INV-GOV-007: modo conservador activo si Redis no disponible (budget=0, EXCEEDED)  
- [ ] Singleton get\_budget\_engine() implementado  
- [ ] \_persist() usa model\_dump\_json() \+ setex() con TTL

**governance\_engine.py**

- [ ] INV-GOV-002: \_audit() llamado ANTES de todo return en evaluate()  
- [ ] INV-GOV-003: governance\_engine.py NO importa módulos de dominio  
- [ ] INV-GOV-004: \_load\_config() lee config\_policy.yaml con fallback a \_DEFAULTS  
- [ ] DEC-015: medición de tiempo en evaluate() con warning si \> max\_policy\_eval\_ms  
- [ ] set\_event\_emitter() para inyección sin import circular (P1)  
- [ ] Singleton get\_governance\_engine() implementado

**ecs\_schema.py**

- [ ] INV-ECS-001: field\_validator rechaza tenant\_id \== 'anonymous'  
- [ ] INV-ECS-002: ecs\_id no cambia post-creación (inmutable por diseño)  
- [ ] INV-ECS-003: model\_validator rechaza budget\_spent \> budget\_total  
- [ ] INV-ECS-004: with\_phase() crea COPIA, no muta el original  
- [ ] INV-ECS-006: with\_phase() valida que la transición sea forward  
- [ ] INV-ECS-007: append\_trace() crea COPIA, nunca muta logic\_trace  
- [ ] INV-ECS-009: confidence clampead a \[0.0, 1.0\]  
- [ ] serialize\_for\_redis() usa model\_dump\_json()  
- [ ] restore\_from\_redis() usa model\_validate\_json()

---

## TU TAREA: memory\_fabric/

### Qué es memory\_fabric

El módulo de memoria persistente y episódica de MPAT4. Su trabajo es:

1. Almacenar fragmentos de memoria de largo plazo por tenant (P12: cognición persistente).  
2. Recuperar memorias relevantes dado un contexto (búsqueda semántica o por clave).  
3. Registrar episodios de sesión (qué pasó, cuándo, con qué resultado).  
4. Proveer acceso a la memoria al ECS entre sesiones (warm start).

### Archivos a generar (en orden estricto)

**1\. MEMORY\_FABRIC\_CONTRACT\_V4\_01.md** → en `memory_fabric/` Con las 10 secciones obligatorias del contrato MPAT4:

- OBJETIVO, RESTRICCIONES, SCHEMAS, EVENTOS, DECISIONES, RIESGOS, PRÓXIMA PRIORIDAD, ARCHIVOS A LEER, INVARIANTES, DEUDA TÉCNICA.

**2\. memory\_fabric\_schema.py** → en `memory_fabric/` Pydantic V3. Clases mínimas a definir:

- `MemoryFragment`: un recuerdo almacenado. Campos: fragment\_id (uuid), tenant\_id, content (str), tags (list\[str\]), importance (float 0-1), created\_at, last\_accessed, access\_count (int), source\_ecs\_id (str | None).  
- `EpisodeRecord`: un episodio de sesión. Campos: episode\_id (uuid), tenant\_id, ecs\_id, phase\_reached (ECSPhase), tokens\_consumed (int), outcome (str), started\_at, ended\_at, summary (str | None).  
- `MemoryQuery`: parámetros de búsqueda. Campos: tenant\_id, query\_text (str | None), tags (list\[str\]), limit (int default=10), min\_importance (float default=0.0).  
- `MemoryQueryResult`: resultado de búsqueda. Campos: fragments (list\[MemoryFragment\]), total\_found (int), query\_time\_ms (float).  
- `FabricConfig`: config del módulo (frozen). Campos: redis\_url, max\_fragments\_per\_tenant (int), fragment\_ttl\_seconds (int), episode\_ttl\_seconds (int).

**3\. memory\_fabric.py** → en `memory_fabric/`

- Clase `MemoryFabric` con singleton `get_memory_fabric()`.  
- Métodos: `store(fragment)`, `query(query)`, `get_by_id(fragment_id, tenant_id)`, `store_episode(episode)`, `get_episodes(tenant_id, limit)`, `delete(fragment_id, tenant_id)`.  
- Backend: Redis. Namespace `{tenant_id}:memory:fragments:{fragment_id}`.  
- Namespace episodios: `{tenant_id}:memory:episodes:{episode_id}`.  
- Índice de búsqueda simple: Redis SET `{tenant_id}:memory:index` con fragment\_ids.  
- NO importar ningún módulo de dominio (P1). Solo redis, governance\_schema, memory\_fabric\_schema.  
- Consultar governance\_engine antes de cada operación (evaluate()).  
- Si governance DENY → rechazar operación, emitir evento, no crashear (P6).

**4\. RELAY\_006.md** → en `relay/` Con las 10 secciones del relay MPAT4. Firmar con tu email y fecha.

### Reglas que NO podés romper

- NUNCA Docker. Runtime \= NanoVMs. min\_memory\_mb \= 128\.  
- Pydantic V3 obligatorio. `model_dump_json()` en toda serialización Redis.  
- Singleton `get_memory_fabric()`.  
- Namespace Redis siempre incluye tenant\_id (INV-ECS-001, P3 Zero Trust).  
- Si Redis no disponible → modo degradado graceful, no crash (P6).  
- Consultar governance\_engine antes de store/query (P8 Policy First).  
- NO llamar directamente a event\_bus desde memory\_fabric. Usar el emit inyectado via `set_event_emitter()` (mismo patrón que governance\_engine).  
- Todo fragmento tiene tenant\_id. Sin tenant\_id → rechazar (INV-GOV-005 heredada).  
- Los episodios son append-only. No se modifican post-creación.

### Eventos que memory\_fabric debe emitir

| Evento | Cuándo |
| :---- | :---- |
| memory.fragment\_stored | store() exitoso |
| memory.fragment\_retrieved | query() retorna resultados |
| memory.fragment\_not\_found | get\_by\_id() no encuentra el fragmento |
| memory.episode\_stored | store\_episode() exitoso |
| memory.governance\_denied | governance DENY en cualquier operación |
| memory.redis\_unavailable | Redis no disponible al iniciar |

### Invariantes que memory\_fabric debe cumplir

- INV-MEM-001: Ningún fragmento sin tenant\_id válido.  
- INV-MEM-002: store() llama a governance evaluate() antes de escribir en Redis.  
- INV-MEM-003: Episodios son inmutables post-creación (frozen Pydantic).  
- INV-MEM-004: Si Redis no disponible → MemoryFabric entra en modo degradado (retorna vacío, no crashea).  
- INV-MEM-005: Namespace Redis siempre con tenant\_id. Nunca clave sin prefijo de tenant.  
- INV-MEM-006: max\_fragments\_per\_tenant se controla al hacer store(). Si se supera → eliminar el más antiguo.  
- INV-MEM-007: memory\_fabric.py NO importa event\_bus directamente. Solo usa emit inyectado.

---

## ECONOMÍA DE TOKENS

- Leer SOLO los archivos listados en PASO 0\.  
- NO cargar módulos no relacionados (session\_scheduler, cognition, etc.).  
- Al llegar al 40% de tokens restantes → GENERAR RELAY\_006 INMEDIATAMENTE y detenerse.  
- Al llegar al 60% → evaluar si continuar o preparar relay.

---

## AL TERMINAR

Guardar RELAY\_006.md en `relay/` (ID carpeta: `1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte`) con el encabezado obligatorio:

\# RELAY\_006.md

\#\# Autor: \[TU\_EMAIL\] · \[FECHA\]

\#\# Módulo: memory\_fabric/ · Versión: V4\_01

Luego copiar al grupo: "Terminé RELAY\_006. Implementé memory\_fabric/ (contrato \+ schema \+ implementación). Próximo: session\_scheduler/ — leer RELAY\_006.md para arrancar."

---

*PROMPT\_RELAY\_006 · generado por [clases.andrea.biologia@gmail.com](mailto:clases.andrea.biologia@gmail.com) · 2026-05-13* *que has usado el formato de razonamiento adaptado por AGT*  
