# MPAT4_DEST
# destino: contracts
# nombre: CONTRACT_SUBQ_RETRY_V4_01.md
# alumno: cursos.ai.agt@gmail.com

# CONTRACT_SUBQ_RETRY_V4_01.md
## MPAT4 — Contrato Formal: Retry Automatico SubQ (DT-SQ-001)
## Version V4_01 · 2026-05-31
## Autor: cursos.ai.agt@gmail.com · RELAY_038
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## DT resuelta: DT-SQ-001 — Retry automatico para tareas "failed" en SubQ
*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. PROPOSITO

Este contrato define la interfaz, invariantes y limites del modulo
`event_bus/subq_retry.py`, que implementa el reintento automatico
de tareas con `status="failed"` en la Sub-Queue de MPAT4.

**Problema que resuelve (DT-SQ-001):**
Actualmente, cuando un worker falla al procesar una `SubQTask`, el
resultado queda con `status="failed"` en Redis pero NO existe mecanismo
automatico de reintento. La tarea muere silenciosamente sin notificacion
ni segunda oportunidad. Esto viola P5 (toda decision es auditable) y
produce perdida de trabajo cognitivo sin registro observable.

**Lo que SubQRetry NO hace (limites del contrato):**
- NO valida ni modifica presupuesto de tokens (eso es CAPA_3 / Budget Manager)
- NO reencola tareas con status="timeout" (esas tienen su propio path)
- NO decide si una tarea merece reintento segun el contenido del payload
- NO accede directamente al Orchestrator (CAPA_3)
- NO es un scheduler global -- solo actua sobre tareas "failed" en SubQ

---

## 2. POSICION EN LA ARQUITECTURA

```
SubQueue (Redis ZSET)
     |
     | [task status="failed"]
     v
SubQRetryManager  <-- este modulo
     |
     |-- reencola en ZSET con retry_count + 1 y backoff score
     |-- emite evento al EventBusV4 (task.retry_enqueued / task.dead_lettered)
     |-- si retry_count >= max_attempts: mueve a DLQ (Dead Letter Queue)
     |
     v
EventBusV4 (notificacion) + Redis DLQ (si dead_lettered)
```

**Relacion con otros modulos:**
- `event_bus_v4.py` (ID: 1u_fmWkm8Y7Lx2SdP3UGNHBU7g5mvqddp) — canal de notificacion
- `event_schema_V4_14_DT-BUS-003.py` (ID: 1DIk-HoLITNv2nqhqS1BjJNgwVhgqtG_t) — schemas EventBus
- `schema_subq_v4.py` (ID: 1CYA-nKITUpi-s02oFgZX0Htocg9MdYTr) — tipos SubQTask / SubQResult
- `ARQUITECTURA_SUBQ_V4_01.md` (ID: 191WfHA8Zt2DVM9WA8qYruHGlvrdGGccM) — arquitectura de referencia

---

## 3. INVARIANTES DEL CONTRATO

```
INV-RETRY.1: SubQRetryManager SOLO procesa tareas con status="failed".
             Tareas con status="completed" o "timeout" son ignoradas.

INV-RETRY.2: El campo retry_count de SubQTask se incrementa en 1 por cada
             reintento. NUNCA se decremente ni se resetee.

INV-RETRY.3: Si retry_count >= max_attempts (configurable, default=3),
             la tarea se mueve a la Dead Letter Queue (DLQ) y se emite
             task.dead_lettered al EventBusV4. NUNCA se reencola.

INV-RETRY.4: El backoff es EXPONENCIAL con jitter. Formula canonica:
             delay = min(backoff_base * (2 ** retry_count) + jitter, backoff_max)
             donde jitter = random.uniform(0, backoff_base).
             El score Redis refleja: score = priority + (now_ms + delay_ms) / 1e13

INV-RETRY.5: Cada reintento emite un evento task.retry_enqueued al EventBusV4
             con tenant_id, task_id, retry_count, next_attempt_ts. Sin excepcion.

INV-RETRY.6: SubQRetryManager NO deduce ni devuelve tokens de budget.
             El Budget Manager de CAPA_12 es responsable de eso por separado.

INV-RETRY.7: El namespace Redis del retry es el mismo que el de SubQ:
             mpat:{tenant_id}:{queue_name}
             El DLQ usa: mpat:{tenant_id}:{queue_name}:dlq
             Nunca cross-tenant (P3 Zero-Trust).

INV-RETRY.8: SubQRetryManager es STATELESS entre llamadas. Todo estado
             persiste en Redis. No hay estado en memoria entre reinicios.
```

---

## 4. TIPOS FORMALES

### SubQRetryConfig (parametros de politica)

```python
# Fuente canonica: SubQRetryConfig en schema_subq_v4.py
# SubQRetryManager lee estos parametros de config_policy en runtime.

max_attempts: int        # default=3, ge=1, le=10
backoff_base_seconds: float  # default=2.0, gt=0.0
backoff_max_seconds: float   # default=60.0, gt=0.0
dead_letter_ttl: int         # default=86400 (24h), TTL en DLQ
```

### RetryDecision (tipo interno)

```python
@dataclass(frozen=True)
class RetryDecision:
    should_retry: bool        # True si retry_count < max_attempts
    next_retry_count: int     # retry_count + 1
    delay_seconds: float      # backoff calculado con jitter
    reason: str               # "retry_eligible" | "max_attempts_reached"
```

### Eventos emitidos al EventBusV4

```python
# task.retry_enqueued — emitido cuando se reencola una tarea
@dataclass(frozen=True)
class TaskRetryEnqueuedPayload:
    tenant_id: str
    task_id: str
    queue_name: str
    retry_count: int          # el NUEVO retry_count (ya incrementado)
    next_attempt_ts: str      # ISO8601 UTC del proximo intento estimado
    original_error: str       # error que causo el fallo previo
    occurred_at: str

# task.dead_lettered — emitido cuando se mueve a DLQ
@dataclass(frozen=True)
class TaskDeadLetteredPayload:
    tenant_id: str
    task_id: str
    queue_name: str
    final_retry_count: int    # retry_count al momento de mover a DLQ
    original_error: str
    dlq_key: str              # clave Redis donde fue movida
    occurred_at: str
```

---

## 5. INTERFAZ PUBLICA DEL MODULO

```python
# event_bus/subq_retry.py

class SubQRetryManager:
    """
    Gestor de reintentos para tareas SubQ con status='failed'.

    INV-RETRY.1..8 aplican a todos los metodos publicos.

    Uso canonico:
        manager = SubQRetryManager(redis_client, event_bus, config)
        await manager.process_failed_task(task, result)
    """

    def __init__(
        self,
        redis_client,           # Redis client async (aioredis o redis.asyncio)
        event_bus: EventBusV4,  # singleton del proceso
        config: SubQRetryConfig,
    ) -> None: ...

    async def process_failed_task(
        self,
        task: SubQTask,         # tarea que fallo
        result: SubQResult,     # resultado con status="failed" y error
    ) -> RetryDecision:
        """
        Evalua si la tarea merece reintento y actua.

        Si should_retry=True:
            - incrementa retry_count
            - calcula delay con backoff exponencial + jitter (INV-RETRY.4)
            - reencola en Redis ZSET con score ajustado
            - emite task.retry_enqueued al EventBusV4 (INV-RETRY.5)

        Si should_retry=False (max_attempts alcanzado):
            - mueve tarea a DLQ con TTL dead_letter_ttl (INV-RETRY.3)
            - emite task.dead_lettered al EventBusV4 (INV-RETRY.5)

        Retorna RetryDecision con la decision tomada.
        Nunca silencia errores internos -- propaga excepciones al caller.
        """
        ...

    async def get_dlq_tasks(
        self,
        tenant_id: str,
        queue_name: str,
        limit: int = 100,
    ) -> list[dict]:
        """
        Retorna tareas en la DLQ del tenant/queue.
        Solo lectura -- no modifica estado.
        """
        ...

    def evaluate_retry(
        self,
        task: SubQTask,
        config: SubQRetryConfig,
    ) -> RetryDecision:
        """
        Logica pura de decision (sin I/O).
        Testeable sin Redis ni EventBus.
        Calcula delay con formula INV-RETRY.4.
        """
        ...
```

---

## 6. CLAVES REDIS

```
Queue principal (reencola aqui):
  mpat:{tenant_id}:{queue_name}                    → ZSET (mismo que SubQ)

Dead Letter Queue:
  mpat:{tenant_id}:{queue_name}:dlq               → Hash (task_id → JSON)
  TTL aplicado por tarea con EXPIRE dead_letter_ttl

Metadatos de retry (opcional, para observabilidad):
  mpat:{tenant_id}:{queue_name}:retry_stats        → Hash (total_retried, total_dead_lettered)
```

---

## 7. INTEGRACION CON WORKER

El worker existente (`MPATWorker.run_once`) ya emite `task_failed` al EventBusV4
cuando una tarea falla (INV-WORKER.2 en ARQUITECTURA_SUBQ_V4_01.md).

SubQRetryManager se conecta como handler de ese evento:

```python
# En el bootstrap del worker pool (capa_11/worker_bootstrap.py):
bus.register(
    tenant_id=tenant_id,
    event_type="task.failed",      # nuevo event_type a agregar a EventBusV4
    handler=retry_manager.handle_task_failed_event,
)
```

NOTA: "task.failed" como event_type del EventBusV4 es NUEVO -- requiere
aprobacion de docente o RES antes de agregar al bus canonico.
Alternativa sin cambiar el bus: el worker llama directamente a
`retry_manager.process_failed_task(task, result)` tras capturar la excepcion.
La alternativa directa es preferible para V4_01 (menor superficie de cambio).

---

## 8. DEUDA TECNICA GENERADA POR ESTE CONTRATO

| ID | Descripcion | Prioridad |
|---|---|---|
| DT-SQ-001 | Implementar subq_retry.py segun este contrato | ALTA |
| DT-SQ-002 | Agregar event_type "task.retry_enqueued" y "task.dead_lettered" al EventBusV4 canonico (requiere RES) | MEDIA |
| DT-SQ-003 | Test de integracion: SubQRetryManager + Redis real (test_subq_retry_integration.py) | ALTA |

---

## 9. CRITERIOS DE ACEPTACION (DT-SQ-001 CERRADO cuando)

- [ ] subq_retry.py existe en event_bus/ con clase SubQRetryManager
- [ ] Todos los INV-RETRY.1..8 tienen implementacion verificable
- [ ] evaluate_retry() es logica pura testeable sin I/O
- [ ] process_failed_task() reencola con score correcto segun INV-RETRY.4
- [ ] process_failed_task() mueve a DLQ cuando retry_count >= max_attempts
- [ ] test_subq_retry_integration.py pasa con Redis real o mock
- [ ] No se toca CAPA_3, Budget Manager, ni event_schema_V4_14 en esta DT

---

## 10. HISTORIAL

| Version | Cambio | Autor | Fecha | Relay |
|---|---|---|---|---|
| V4_01 | Creacion inicial — DT-SQ-001 | cursos.ai.agt@gmail.com | 2026-05-31 | RELAY_038 |

---

*CONTRACT_SUBQ_RETRY_V4_01.md · cursos.ai.agt@gmail.com · 2026-05-31 · MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*
