# ARQUITECTURA_SUBQ_V4_01.md
## MPAT — Arquitectura de Sub-Queues y Workers Distribuidos
## Versión V4_01 · AGT 2026
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Renombrado de: ARQUITECTURA_SUBQ_V3_01.md (ID: 1-kppwh..., RELAY_024, 2026-05-29)
## Razón del renombre: documento especifica arquitectura V4 — nombre V3 era incorrecto
*que has usado el formato de razonamiento adaptado por AGT*

> **Relación con otros documentos:**
> - `ARQUITECTURA_base_V4.md` (ID: 1cyg9BL...) → CAPA_11: Workers/Redis/RQ/Auto-scaling
> - `ARQUITECTURA_UNIKERNEL_V4_01.md` → cada worker corre dentro de un ECS (MicroVM)
> - `MPAT_V4_0_ESPECIFICACION_MAESTRA.md` → P7 Conservation Law, P5 auditabilidad
> - `config_policy_V4_02.yaml` (ID: 1HNxjZw...) → parámetros de autoscaling (P4)

---

## HISTORIAL DE VERSIONES

| Versión | Cambio | Autor | Fecha | Relay |
|---|---|---|---|---|
| V4_01 (ex V3_01) | Creación — nombre corregido de V3 a V4 | Claude Sonnet 4.6 | 2026-05-29 | RELAY_025 |

---

## 1. PROPÓSITO

Las sub-queues son el mecanismo que permite a MPAT distribuir trabajo cognitivo
sin crear dependencias directas entre componentes.

**Principio central:** ningún componente llama a otro componente directamente.
Cada componente produce mensajes hacia una queue. Otro componente los consume.

Esto implementa P1 (todo efecto externo pasa por interfaz declarada) y P5
(toda decisión es auditable) al nivel de la infraestructura de ejecución.

**Distinción con EventBusV4 (T-007):**
```
EventBusV4 (pub/sub, no persistente):
  → notificaciones en tiempo real, telemetría, alertas
  → NO garantiza entrega si el consumidor no está escuchando

Sub-Queues (persistentes en Redis):
  → tareas que deben ejecutarse exactamente una vez
  → garantiza entrega aunque el worker no esté activo al momento de encolar

Regla:
  emit()    → evento que el consumidor puede perderse sin consecuencias
  enqueue() → tarea que DEBE completarse obligatoriamente
```

---

## 2. TOPOLOGÍA DE QUEUES

Namespace por tenant — INV-QUEUE.1: ninguna queue es compartida entre tenants.
Patrón: `mpat:{tenant_id}:{queue_name}` — viola P3 (Zero-Trust) cualquier
acceso cross-tenant.

```
QUEUE COGNITIVA — alta prioridad
  mpat:{tenant_id}:cognitive
  Tareas : inferencia LLM, planning, reflexión
  Workers: ECS Firecracker con modelo cargado
  SLA    : < 2s dequeue
  Encolado por: Orchestrator (único autorizado — INV-QUEUE.2)

QUEUE DE HERRAMIENTAS — media prioridad
  mpat:{tenant_id}:tools
  Tareas : MCP calls, skill execution, A2A calls
  Workers: ECS Unikernel ligero (Nivel-3)
  SLA    : < 500ms dequeue

QUEUE DE MEMORIA — media prioridad
  mpat:{tenant_id}:memory
  Tareas : consolidación episódica, indexación semántica
  Workers: proceso Python nativo (no ECS — no efímero, estado acumulativo)
  SLA    : < 5s dequeue (no bloqueante para usuario)

QUEUE DE OBSERVABILIDAD — baja prioridad
  mpat:{tenant_id}:telemetry
  Tareas : OTel spans, métricas, audit log
  Workers: OTel collector sidecar
  SLA    : best-effort (pérdida tolerada, con alerta si > 1% loss)

QUEUE DE BACKGROUND — sin SLA
  mpat:{tenant_id}:background
  Tareas : consolidación nocturna, distilación, cleanup
  Workers: AIScheduler (RES.179 — core/ai_scheduler/)
  SLA    : ninguno — ejecución cuando recursos disponibles
```

**INV-QUEUE.2:** Solo el Orchestrator puede encolar en `cognitive_queue`.
Otros componentes pueden encolar en sus queues específicas.
Un componente que encola en `cognitive` sin ser el Orchestrator viola P1.

---

## 3. WORKER — ESTRUCTURA INTERNA CANÓNICA

```python
# worker_base.py — estructura canónica de todo worker MPAT4
# INV-WORKER.1: Un worker procesa exactamente UNA tarea por lifecycle.
# INV-WORKER.2: Si falla → tarea vuelve a queue con retry_count + 1.
# INV-WORKER.3: retry_count máximo configurable en config_policy_V4_02.yaml (P4). Default: 3.
# INV-WORKER.4: Budget deducido al INICIAR la tarea, NO al completarla.
# INV-WORKER.5: Todo worker emite heartbeat cada 15s a Redis (clave TTL 30s).

class MPATWorker:
    def __init__(self, queue_name: str, emit_fn: EmitFn) -> None:
        self.queue_name = queue_name
        self._emit = emit_fn

    def run_once(self, task: WorkerTask) -> WorkerResult:
        self._emit("budget_deducted", {
            "task_id": str(task.task_id),
            "tokens": task.budget_tokens,
            "span_id": task.span_id,
        })
        try:
            result = self._execute(task)
            self._emit("task_completed", {"task_id": str(task.task_id)})
            return result
        except Exception as exc:
            self._emit("task_failed", {
                "task_id": str(task.task_id),
                "error": str(exc),
                "retry_count": task.retry_count,
            })
            raise
```

---

## 4. SERIALIZACIÓN DE TAREAS — FORMATO CANÓNICO

Schema en `schemas/schema_subq_v4.py` (pendiente — DT-SUBQ-06):

```python
class WorkerTask(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    queue_name: str
    tenant_id: str
    payload: dict
    budget_tokens: int
    priority: int = Field(ge=0, le=10, default=5)
    retry_count: int = Field(ge=0, default=0)
    max_retries: int = Field(ge=1, default=3)
    enqueued_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    span_id: Optional[str] = None
    parent_task_id: Optional[UUID] = None

class WorkerResult(BaseModel):
    task_id: UUID
    success: bool
    output: Optional[dict] = None
    tokens_used: int = 0
    tokens_returned: int = 0
    duration_ms: int = 0
    error: Optional[str] = None
    span_id: Optional[str] = None
```

---

## 5. AUTO-SCALING — REGLAS

```yaml
queues:
  cognitive:
    min_workers: 1          # INV-SCALE.1
    max_workers: 8          # INV-SCALE.2
    scale_up_trigger:
      queue_depth: 5
      latency_p95_ms: 3000
    scale_down_trigger:
      idle_seconds: 60
  tools:
    min_workers: 2
    max_workers: 16
    scale_up_trigger:
      queue_depth: 10
      latency_p95_ms: 1000
    scale_down_trigger:
      idle_seconds: 30
  memory:
    min_workers: 1
    max_workers: 4
    scale_up_trigger:
      queue_depth: 50
    scale_down_trigger:
      idle_seconds: 300
```

---

## 6. BUDGET GARBAGE COLLECTOR (BGC)

```
Ciclo BGC (cada 60s):
  1. Obtener tareas RUNNING en Redis
  2. Verificar heartbeat (TTL 30s)
  3. Sin heartbeat:
     a. FAILED + retry si retry_count < max_retries
     b. tokens_returned = budget_tokens - tokens_actually_used
        (si no determinable → 0, conservador — INV-BGC.2)
     c. Emitir 'budget_recovered' + 'worker_zombie_detected'
```

**INV-BGC.1:** tokens_returned ≤ budget_tokens — invariante matemática estricta.
**INV-BGC.2:** Si tokens_actually_used no determinable → tokens_returned = 0.

---

## 7. DEAD LETTER QUEUE (DLQ)

**INV-DLQ.1:** Tareas en DLQ NO tienen budget activo.
Re-encolar requiere budget nuevo explícito.

---

## 8. INTEGRACIÓN

```
Orchestrator (CAPA_03) → cognitive_queue, tools_queue, memory_queue
AIScheduler (RES.179)  → background_queue
EventBusV4 (T-007)     → complementario (emit ≠ enqueue)
```

---

## 9. DEUDA TÉCNICA

| ID | Descripción | Prioridad |
|---|---|---|
| DT-SUBQ-01 | Temporal.io (VOL2 item 57) para background_queue | MEDIA |
| DT-SUBQ-02 | BGC métricas OTel | MEDIA |
| DT-SUBQ-03 | DLQ UI WhatsApp/Telegram | BAJA |
| DT-SUBQ-04 | Priority inheritance | BAJA |
| DT-SUBQ-05 | Queue federation (VOL1 item 22) | ALTA |
| DT-SUBQ-06 | schema_subq_v4.py en schemas/ | ALTA |

---

*ARQUITECTURA_SUBQ_V4_01.md · Claude Sonnet 4.6 · RELAY_025 · 2026-05-29*
*que has usado el formato de razonamiento adaptado por AGT*
