# RES.MESH_001 — LamportClock Distribuido para MPAT4
## Autor: ai.mpat.designer@gmail.com · 2026-05-26
## Módulo: core/event_bus/ · Lenguaje: Python 3.14 · Versión: V4_15
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Estado: APROBADA Y COMPLETADA

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Problema que resuelve

### El contexto: qué es un reloj de Lamport

Un reloj de Lamport es un contador lógico que asigna un número a cada evento
en un sistema distribuido. La regla es simple: si el evento A causó el evento B,
entonces clock(A) < clock(B). Esto permite ordenar eventos sin necesidad de
sincronización de relojes físicos (que en sistemas distribuidos es imposible
de garantizar con exactitud).

En MPAT4 V4, el LamportClock original (RES.164, cognitive_event_mesh.py) vive
en la RAM de un único proceso Python. Cuando el sistema escala a múltiples procesos
o múltiples nodos físicos, cada proceso tiene su propio contador en RAM.

**El problema concreto:**

```
Proceso A (nodo 1): clock=5 → emite "session.started"
Proceso B (nodo 2): clock=5 → emite "governance.violation"

¿Cuál ocurrió primero? El sistema no puede determinarlo.
La ley de Lamport requiere: max(A, B) + 1 sobre estado compartido.
Sin estado compartido, el orden causal global es imposible.
```

---

## 2. Decisión arquitectural: Redis vs etcd

**Decisión: Redis con degradación graceful.**

### Por qué Redis gana sobre etcd

etcd garantiza consistencia fuerte (Raft consensus). Para un clock de Lamport
en un sistema de transacciones financieras irreversibles, etcd sería la elección
correcta. Pero MPAT4 usa el clock causal para **observability y semantic routing**,
no para transacciones con consecuencias irreversibles.

Redis ofrece `INCR` atómico nativo para `tick()` y scripts Lua para
`max(local, received) + 1` en `update()`. Ambas operaciones son atómicas
sin race conditions, sin reintentos, sin complejidad adicional.

| Criterio | Redis | etcd |
|---|---|---|
| Atomicidad para INCR | Nativa (O(1)) | CAS con reintentos |
| Complejidad operacional | Baja | Alta (cluster Raft) |
| Latencia típica | < 1ms | 2-10ms |
| Degradación si cae | Graceful (RAM) | Bloqueo hasta quórum |
| Caso de uso adecuado | Best-effort, observability | Transacciones críticas |

### La trampa educativa de esta decisión

La respuesta simple sería: "Redis es más rápido, usamos Redis." Eso es incorrecto.

La razón real es: **el nivel de consistencia requerido define la tecnología**.
Redis es correcto aquí porque la consecuencia de perder el orden causal exacto
entre dos eventos de observability es que el collector puede recibirlos fuera de
orden. El sistema sigue funcionando. No hay pérdida de datos, no hay corrupción
de estado, no hay consecuencias económicas.

Si el clock se usara para ordenar transacciones financieras o para garantizar
la serialización de escrituras en Memory Fabric, etcd sería la única respuesta
correcta, independientemente de la latencia.

---

## 3. Protocolo de degradación graceful

La característica más importante de esta resolución no es el uso de Redis —
es el protocolo de degradación graceful cuando Redis no está disponible.

```
1. Al instanciar LamportDistributedClock:
   - Conectar a Redis (timeout: 200ms).
   - Si falla → DEGRADED_MODE = True, log WARNING.
   - Si ok → DEGRADED_MODE = False.

2. En cada operación tick() / update() / value:
   - DEGRADED_MODE = True → operar en RAM, no reintentar Redis.
   - DEGRADED_MODE = False → operar en Redis.
   - Si Redis falla en operación → DEGRADED_MODE = True, log WARNING.
   - Retornar valor local como fallback inmediato.

3. Recovery automático cada 30 segundos:
   - Si DEGRADED_MODE = True → intentar reconexión.
   - Si ok → SET clock Redis = max(redis_val, local_val).
   - DEGRADED_MODE = False.

4. Observable en todo momento:
   - clock.is_degraded → bool, nunca lanza excepción (INV-CLOCK.2).
   - Evento "mesh.clock_degraded" via EventBus al cambiar estado.
```

**Qué pierde el sistema en modo degradado:**
- El orden causal entre eventos de distintos procesos ya no está garantizado.
- observability_collector puede recibir eventos fuera de orden causal.
- El semantic router sigue funcionando (no depende del clock para routing).
- No hay pérdida de mensajes ni corrupción de estado.

---

## 4. Lua script para update() atómico

```lua
-- ARGV[1] = received (int)
-- KEYS[1] = mpat4:clock:<tenant_id>
local current = tonumber(redis.call('GET', KEYS[1])) or 0
local received = tonumber(ARGV[1])
local new_val = math.max(current, received) + 1
redis.call('SET', KEYS[1], new_val)
return new_val
```

Redis ejecuta scripts Lua en un único thread. No hay race condition posible
entre el GET y el SET. Esta atomicidad es equivalente a la que ofrece el GIL
de Python para el modo RAM degradado (INV-CLOCK.1).

---

## 5. Invariantes

```
INV-MESH.2 (heredado): el clock nunca retrocede.
  En modo Redis ni en modo RAM el valor decrece.
  tick() siempre incrementa. update() aplica max().

INV-MESH.5 (heredado): el clasificador de complejidad sigue siendo determinista.
  El clock no afecta al clasificador de CognitiveEventMesh.

INV-BUS.1 (heredado): el clock es POR TENANT — nunca global.
  mpat4:clock:tenant_A y mpat4:clock:tenant_B son independientes.

INV-CLOCK.1 (NUEVO): tick() y update() son atómicos.
  En Redis: garantizado por INCR y Lua.
  En RAM degradado: garantizado por GIL de Python.

INV-CLOCK.2 (NUEVO): is_degraded es observable en todo momento.
  No puede lanzar excepción en ninguna condición.

INV-CLOCK.3 (NUEVO): la interfaz pública de LamportClock no cambia.
  CognitiveEventMesh no necesita modificaciones para usar LamportDistributedClock.
  El cambio es transparente para los consumidores.
```

---

## 6. Artefactos completados

| Archivo | Tamaño | ID Drive | Autor | Fecha |
|---|---|---|---|---|
| LAMPORT_DISTRIBUTED_CONTRACT_V1.md | 6.2 KB | 1jleQLwQHQgy2pCKZHKLZFGT8eI7WkoF5 | cursos.ai.agt@gmail.com | 2026-05-26 |
| lamport_schema.py | 4.3 KB | 1KEK9j6iSQbLWM25QFlxEvU05Go-pd4En | cursos.ai.agt@gmail.com | 2026-05-26 |
| lamport_distributed.py | 18.9 KB | 1FQK0sk4O_mrLVXcaTE1xJhb4-xebMrMC | cursos.ai.agt@gmail.com | 2026-05-26 |

Carpeta: core/event_bus/ (ID: 1lsaMPtDRFcXPGdBrZ8fAilsCNhpXZZiG)

**Nota sobre versiones:** existe una versión menor del mismo archivo (8.7 KB,
autor agt1973) en la misma carpeta. La versión canónica es la de 18.9 KB
(cursos.ai.agt) que implementa el protocolo de degradación graceful completo.

---

## 7. Deuda técnica post-RES.MESH_001

| ID | Descripción | Prioridad |
|---|---|---|
| DT-MESH-001 | Tests con 2+ coroutines simultáneas — demostrar atomicidad | ALTA |
| DT-MESH-002 | Test de degradación graceful — simular Redis caído | ALTA |
| DT-MESH-003 | Actualizar CognitiveEventMesh para importar LamportDistributedClock | MEDIA |
| DT-MESH-004 | Métricas OTel: is_degraded, recovery_count, clock_value_at_degradation | MEDIA |

---

## 8. Integración con otras resoluciones

| Resolución | Integración |
|---|---|
| RES.164 (CognitiveEventMesh) | LamportDistributedClock reemplaza LamportClock en RAM |
| T-007 (EventBus) | Evento "mesh.clock_degraded" publicado via EventBus |
| T-009 (Observability) | clock.is_degraded expuesto como métrica OTel |

---

*RES.MESH_001_LAMPORT_DISTRIBUIDO_V4.md · V4_15 · ai.mpat.designer@gmail.com · 2026-05-26*
*Resolución: APROBADA Y COMPLETADA*
*que has usado el formato de razonamiento adaptado por AGT*
