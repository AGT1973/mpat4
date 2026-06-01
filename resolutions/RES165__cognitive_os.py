"""
RES165__cognitive_os.py
DESTINO FINAL: core/cognitive_os.py
RES.165 — MPAT4 | Relay: RELAY_011 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


P31 — AI Native OS: redefine las abstracciones del sistema operativo
cuando la cognición es el ciudadano de primera clase.


En un SO clásico: Process, Thread, IPC, Scheduler.
En el AI Native OS:
  CognitiveProcess  = sesión de agente con budget, SOUL y unikernel propio.
  CognitiveThread   = tarea paralela dentro del mismo proceso cognitivo.
  CognitiveIPC      = paso de mensajes via CognitiveEventMesh (RES.164).
  CognitiveScheduler= asigna tokens de inferencia según prioridad y P7.


INVARIANTES:
  INV-OS.1: un CognitiveProcess tiene EXACTAMENTE un unikernel (Firecracker).
            No compartido entre procesos. (Hereda INV-FIRE.1)
  INV-OS.2: un CognitiveThread no puede exceder el budget de su CognitiveProcess.
            Los threads comparten el pool de tokens del proceso padre.
  INV-OS.3: toda IPC entre procesos pasa por CognitiveEventMesh (RES.164).
            Los procesos NUNCA se llaman directamente entre sí.
  INV-OS.4: el CognitiveScheduler aplica P7 (Conservation Law) antes de
            asignar tokens a cualquier proceso.
  INV-OS.5: CognitiveSignal.FREEZE detiene INMEDIATAMENTE el proceso
            (equivalente cognitivo de SIGKILL). No hay gracia period.


TRAMPA EDUCATIVA:
  "CognitiveThread es lo mismo que un subagente."
  FALSO: un CognitiveThread comparte el unikernel y el budget del proceso padre.
  Un subagente (RES.239) tiene su PROPIO unikernel, su propio budget y
  su propia sesión en el SessionSchedulerV4. Son abstracciones de diferente nivel:
  Thread = dentro del proceso. Subagente = proceso hijo independiente.


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Optional
from uuid import uuid4


from cognitive_kernel.kernel_bridge import CognitiveKernelInterface, KernelBudgetState
from event_bus_v4 import EventBusV4
from core.cognitive_event_mesh import CognitiveEventMesh


logger = logging.getLogger("mpat.cognitive_os")




# ---------------------------------------------------------------------------
# Enums de estado
# ---------------------------------------------------------------------------


class ProcessState(str, Enum):
    SPAWNING    = "SPAWNING"     # boot del unikernel en curso
    ACTIVE      = "ACTIVE"       # ejecutando
    SUSPENDING  = "SUSPENDING"   # guardando estado antes de teardown
    TERMINATED  = "TERMINATED"   # unikernel destruido, budget devuelto




class ThreadState(str, Enum):
    READY       = "READY"
    RUNNING     = "RUNNING"
    WAITING     = "WAITING"      # esperando I/O o IPC
    COMPLETED   = "COMPLETED"
    FAILED      = "FAILED"




class CognitiveSignal(str, Enum):
    """
    Señales cognitivas — equivalente a señales UNIX pero semánticas.


    COMPLETE:  terminar limpiamente cuando sea posible (equivalente SIGTERM).
    SUSPEND:   guardar estado y pausar (equivalente SIGSTOP).
    RESUME:    reanudar desde estado guardado (equivalente SIGCONT).
    FREEZE:    detener INMEDIATAMENTE sin cleanup (equivalente SIGKILL, INV-OS.5).
    BUDGET_LOW: advertencia de presupuesto bajo (sin equivalente UNIX).
    """
    COMPLETE   = "COMPLETE"
    SUSPEND    = "SUSPEND"
    RESUME     = "RESUME"
    FREEZE     = "FREEZE"
    BUDGET_LOW = "BUDGET_LOW"




# ---------------------------------------------------------------------------
# CognitiveThread — tarea paralela dentro de un CognitiveProcess
# ---------------------------------------------------------------------------


@dataclass
class CognitiveThread:
    """
    Tarea paralela ejecutándose dentro de un CognitiveProcess.


    COMPARTE el unikernel y el budget del proceso padre (INV-OS.2).
    NO es un subagente — no tiene sesión propia en SessionSchedulerV4.


    Implementado sobre asyncio.Task — la abstracción cognitiva envuelve
    el mecanismo de Python sin exponer los detalles de asyncio al caller.
    """
    thread_id: str
    process_id: str       # PID del CognitiveProcess padre
    tenant_id: str
    name: str
    state: ThreadState = ThreadState.READY
    tokens_consumed: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    _task: Optional[asyncio.Task] = field(default=None, repr=False)


    async def join(self, timeout: Optional[float] = None) -> Any:
        """Espera la completación del thread. Retorna el resultado."""
        if self._task is None:
            raise RuntimeError(f"Thread {self.thread_id} no iniciado")
        try:
            result = await asyncio.wait_for(self._task, timeout=timeout)
            self.state = ThreadState.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
            return result
        except asyncio.TimeoutError:
            self._task.cancel()
            self.state = ThreadState.FAILED
            self.error = "timeout"
            raise
        except Exception as exc:
            self.state = ThreadState.FAILED
            self.error = str(exc)
            raise




# ---------------------------------------------------------------------------
# CognitiveProcess — sesión de agente con abstracciones de SO
# ---------------------------------------------------------------------------


class CognitiveProcess:
    """
    Proceso cognitivo — la unidad de ejecución autónoma en el AI Native OS.


    Envuelve una sesión del SessionSchedulerV4 y agrega abstracciones de SO:
      - Gestión de CognitiveThreads (tareas paralelas internas)
      - Envío y recepción de CognitiveSignals
      - IPC via CognitiveEventMesh (INV-OS.3)
      - Monitoreo de budget en tiempo real (INV-OS.2)


    INV-OS.1: tiene EXACTAMENTE un unikernel_id.
    INV-OS.2: todos sus threads comparten su pool de tokens.
    INV-OS.3: IPC solo via CognitiveEventMesh.
    """


    def __init__(
        self,
        pid: str,                          # = session_id del SessionSchedulerV4
        tenant_id: str,
        agent_id: str,
        unikernel_id: str,
        budget_tokens: int,
        kernel: CognitiveKernelInterface,
        mesh: CognitiveEventMesh,
        soul_md: Optional[str] = None,     # contenido del SOUL.md (RES.231)
    ):
        self.pid = pid
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.unikernel_id = unikernel_id   # INV-OS.1: uno y solo uno
        self.budget_tokens = budget_tokens
        self.soul_md = soul_md
        self._kernel = kernel
        self._mesh = mesh
        self._state = ProcessState.SPAWNING
        self._threads: dict[str, CognitiveThread] = {}
        self._signal_handlers: dict[CognitiveSignal, Callable] = {}
        self._mailbox: asyncio.Queue = asyncio.Queue()
        self._tokens_consumed = 0


    # ------------------------------------------------------------------
    # Estado del proceso
    # ------------------------------------------------------------------


    @property
    def state(self) -> ProcessState:
        return self._state


    @property
    def budget_remaining(self) -> int:
        return self.budget_tokens - self._tokens_consumed


    def activate(self) -> None:
        """Transición SPAWNING → ACTIVE."""
        if self._state != ProcessState.SPAWNING:
            raise OSError(f"PID {self.pid}: activate() requiere estado SPAWNING")
        self._state = ProcessState.ACTIVE
        logger.info("CognitiveProcess ACTIVE pid=%s agent=%s", self.pid, self.agent_id)


    # ------------------------------------------------------------------
    # Gestión de CognitiveThreads (INV-OS.2)
    # ------------------------------------------------------------------


    def spawn_thread(
        self,
        name: str,
        coro: Coroutine,
        token_budget: Optional[int] = None,
    ) -> CognitiveThread:
        """
        Lanza un CognitiveThread dentro de este proceso.


        INV-OS.2: verifica que haya budget suficiente antes de lanzar.
        El thread comparte el pool de tokens del proceso padre.
        """
        if self._state != ProcessState.ACTIVE:
            raise OSError(f"PID {self.pid}: spawn_thread() requiere estado ACTIVE")


        if token_budget and token_budget > self.budget_remaining:
            raise InsufficientProcessBudget(
                pid=self.pid,
                requested=token_budget,
                available=self.budget_remaining,
            )


        tid = str(uuid4())
        thread = CognitiveThread(
            thread_id=tid,
            process_id=self.pid,
            tenant_id=self.tenant_id,
            name=name,
            state=ThreadState.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
        task = asyncio.create_task(coro, name=f"thread:{name}:{tid[:8]}")
        thread._task = task
        self._threads[tid] = thread


        logger.debug("CognitiveThread spawned: pid=%s tid=%s name=%s", self.pid, tid[:8], name)
        return thread


    async def join_all_threads(self, timeout: Optional[float] = None) -> dict[str, Any]:
        """Espera la completación de todos los threads activos."""
        results = {}
        for tid, thread in self._threads.items():
            if thread.state == ThreadState.RUNNING:
                try:
                    results[tid] = await thread.join(timeout=timeout)
                except Exception as exc:
                    results[tid] = exc
                    logger.error("Thread %s falló: %s", tid[:8], exc)
        return results


    def thread_count(self, state: Optional[ThreadState] = None) -> int:
        if state is None:
            return len(self._threads)
        return sum(1 for t in self._threads.values() if t.state == state)


    # ------------------------------------------------------------------
    # CognitiveSignals (INV-OS.5)
    # ------------------------------------------------------------------


    def register_signal_handler(
        self,
        signal: CognitiveSignal,
        handler: Callable,
    ) -> None:
        """Registra un handler para una señal cognitiva."""
        self._signal_handlers[signal] = handler


    async def send_signal(self, signal: CognitiveSignal) -> None:
        """
        Envía una señal cognitiva a este proceso.


        INV-OS.5: FREEZE cancela TODOS los threads inmediatamente.
        Los demás signals invocan el handler registrado si existe.
        """
        logger.info("CognitiveSignal %s → pid=%s", signal.value, self.pid)


        if signal == CognitiveSignal.FREEZE:
            # INV-OS.5: detención inmediata sin gracia period
            for thread in self._threads.values():
                if thread._task and not thread._task.done():
                    thread._task.cancel()
                    thread.state = ThreadState.FAILED
                    thread.error = "FREEZE signal"
            self._state = ProcessState.SUSPENDING
            logger.warning("FREEZE aplicado: pid=%s todos los threads cancelados", self.pid)
            return


        handler = self._signal_handlers.get(signal)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(signal)
            else:
                handler(signal)
        else:
            logger.debug("Sin handler para señal %s en pid=%s", signal.value, self.pid)


    # ------------------------------------------------------------------
    # CognitiveIPC — mailbox y mesh (INV-OS.3)
    # ------------------------------------------------------------------


    async def send_ipc(
        self,
        target_agent_id: str,
        message_type: str,
        payload: dict,
    ) -> str:
        """
        Envía un mensaje IPC a otro CognitiveProcess.


        INV-OS.3: TODA IPC pasa por CognitiveEventMesh — nunca llamada directa.
        Retorna el event_id asignado por el mesh.
        """
        import json
        ipc_payload = {
            "ipc": True,
            "from_pid": self.pid,
            "from_agent": self.agent_id,
            "to_agent": target_agent_id,
            "message_type": message_type,
            "payload": payload,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        event_id = await self._mesh.route_semantic(
            tenant_id=self.tenant_id,
            event_type=f"ipc.{message_type}",
            payload_bytes=json.dumps(ipc_payload).encode(),
            required_specialization="general",
        )
        logger.debug("IPC enviado: pid=%s → agent=%s type=%s", self.pid, target_agent_id, message_type)
        return event_id or ""


    async def receive_ipc(self, timeout: Optional[float] = None) -> Optional[dict]:
        """Lee el próximo mensaje del mailbox del proceso."""
        try:
            return await asyncio.wait_for(self._mailbox.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None


    async def _deliver_ipc(self, message: dict) -> None:
        """Handler interno — CognitiveEventMesh entrega mensajes aquí."""
        await self._mailbox.put(message)


    # ------------------------------------------------------------------
    # Budget tracking
    # ------------------------------------------------------------------


    def consume_tokens(self, tokens: int, reason: str = "") -> None:
        """
        Registra consumo de tokens por el proceso o sus threads.
        INV-OS.2: no puede superar budget_tokens.
        """
        if self._tokens_consumed + tokens > self.budget_tokens:
            raise InsufficientProcessBudget(
                pid=self.pid,
                requested=tokens,
                available=self.budget_remaining,
            )
        self._tokens_consumed += tokens
        logger.debug("Tokens consumidos: pid=%s +%d total=%d reason=%s",
                     self.pid, tokens, self._tokens_consumed, reason)


    def budget_state(self) -> dict:
        return {
            "pid": self.pid,
            "budget_tokens": self.budget_tokens,
            "tokens_consumed": self._tokens_consumed,
            "budget_remaining": self.budget_remaining,
            "pct_used": round(self._tokens_consumed / max(1, self.budget_tokens) * 100, 1),
        }




# ---------------------------------------------------------------------------
# CognitiveIPC — gestión centralizada de IPC entre procesos
# ---------------------------------------------------------------------------


class CognitiveIPC:
    """
    Capa de IPC entre CognitiveProcesses.


    Gestiona el registro de procesos y la entrega de mensajes IPC
    via CognitiveEventMesh (INV-OS.3).


    Tipos de IPC:
      - Mailbox: mensajes asíncronos en cola (fire-and-forget)
      - Semaphore: sincronización entre procesos (P/V operations)
      - Pipe: canal bidireccional entre dos procesos específicos
    """


    def __init__(self, mesh: CognitiveEventMesh):
        self._mesh = mesh
        self._processes: dict[str, CognitiveProcess] = {}  # pid → process
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self._pipes: dict[tuple[str, str], asyncio.Queue] = {}


    def register_process(self, process: CognitiveProcess) -> None:
        self._processes[process.pid] = process
        logger.debug("CognitiveIPC: proceso registrado pid=%s", process.pid)


    def unregister_process(self, pid: str) -> None:
        self._processes.pop(pid, None)


    async def send(
        self,
        from_pid: str,
        to_pid: str,
        message_type: str,
        payload: dict,
    ) -> None:
        """
        Envía un mensaje de proceso a proceso.
        INV-OS.3: pasa por el mesh — el IPC NUNCA es una llamada directa.
        """
        target = self._processes.get(to_pid)
        if not target:
            logger.warning("IPC: proceso destino no encontrado pid=%s", to_pid)
            return
        message = {
            "from_pid": from_pid,
            "to_pid": to_pid,
            "message_type": message_type,
            "payload": payload,
        }
        await target._deliver_ipc(message)


    # --- Semáforos cognitivos ---


    def create_semaphore(self, name: str, value: int = 1) -> asyncio.Semaphore:
        """Crea un semáforo cognitivo compartido entre procesos."""
        sem = asyncio.Semaphore(value)
        self._semaphores[name] = sem
        return sem


    def get_semaphore(self, name: str) -> Optional[asyncio.Semaphore]:
        return self._semaphores.get(name)


    # --- Pipes cognitivos ---


    def create_pipe(self, pid_a: str, pid_b: str) -> asyncio.Queue:
        """Crea un canal bidireccional entre dos procesos."""
        key = tuple(sorted([pid_a, pid_b]))
        pipe = asyncio.Queue()
        self._pipes[key] = pipe
        return pipe


    def get_pipe(self, pid_a: str, pid_b: str) -> Optional[asyncio.Queue]:
        key = tuple(sorted([pid_a, pid_b]))
        return self._pipes.get(key)




# ---------------------------------------------------------------------------
# CognitiveScheduler — asigna tokens de inferencia (equivalente al scheduler de SO)
# ---------------------------------------------------------------------------


class SchedulingPolicy(str, Enum):
    FIFO            = "fifo"
    PRIORITY        = "priority"     # por presupuesto restante
    ROUND_ROBIN     = "round_robin"
    BUDGET_URGENT   = "budget_urgent" # primero el proceso con menos tokens restantes




class CognitiveScheduler:
    """
    Scheduler del AI Native OS.


    Decide qué CognitiveProcess recibe tokens de inferencia en cada ciclo.
    Aplica P7 Conservation Law antes de cualquier asignación (INV-OS.4).


    Analogía SO: el kernel scheduler que decide qué proceso corre en la CPU.
    Diferencia: aquí el "CPU time" son tokens de inferencia del LLM,
    no ciclos de reloj. El scheduler protege el presupuesto global del tenant.
    """


    def __init__(
        self,
        kernel: CognitiveKernelInterface,
        policy: SchedulingPolicy = SchedulingPolicy.PRIORITY,
        total_tenant_budget: int = 100_000,
    ):
        self._kernel = kernel
        self._policy = policy
        self._total_budget = total_tenant_budget
        self._allocated: dict[str, int] = {}   # pid → tokens asignados
        self._queue: list[CognitiveProcess] = []
        self._lock = asyncio.Lock()


    async def enqueue(self, process: CognitiveProcess) -> None:
        """Encola un proceso para recibir tokens de inferencia."""
        async with self._lock:
            self._queue.append(process)
            logger.debug("Scheduler: proceso encolado pid=%s budget=%d",
                         process.pid, process.budget_tokens)


    async def next_process(self) -> Optional[CognitiveProcess]:
        """
        Retorna el próximo proceso a ejecutar según la política.
        INV-OS.4: verifica P7 antes de retornar.
        """
        async with self._lock:
            active = [p for p in self._queue if p.state == ProcessState.ACTIVE]
            if not active:
                return None


            if self._policy == SchedulingPolicy.FIFO:
                candidate = active[0]
            elif self._policy == SchedulingPolicy.PRIORITY:
                # Mayor budget_remaining primero
                candidate = max(active, key=lambda p: p.budget_remaining)
            elif self._policy == SchedulingPolicy.BUDGET_URGENT:
                # Menor budget_remaining primero (urgente = al borde del límite)
                candidate = min(active, key=lambda p: p.budget_remaining)
            else:  # ROUND_ROBIN
                candidate = active[0]
                self._queue.append(self._queue.pop(0))


            # INV-OS.4: P7 Conservation Law
            if candidate.budget_remaining <= 0:
                logger.warning(
                    "Scheduler: proceso sin budget excluido pid=%s", candidate.pid
                )
                return None


            return candidate


    async def release(self, pid: str) -> None:
        """Libera un proceso de la cola (al terminar o hacer teardown)."""
        async with self._lock:
            self._queue = [p for p in self._queue if p.pid != pid]


    def scheduler_stats(self) -> dict:
        return {
            "policy": self._policy.value,
            "queued_processes": len(self._queue),
            "active_processes": sum(1 for p in self._queue if p.state == ProcessState.ACTIVE),
            "total_budget": self._total_budget,
            "allocated": sum(p.budget_tokens for p in self._queue),
        }




# ---------------------------------------------------------------------------
# CognitiveOS — punto de entrada del AI Native OS
# ---------------------------------------------------------------------------


class CognitiveOS:
    """
    AI Native OS — orquesta CognitiveProcesses, CognitiveThreads y CognitiveIPC.


    Es la capa de abstracción de sistema operativo de MPAT4.
    Sobre el CognitiveKernelBridge (microkernel en Rust),
    el CognitiveOS define las primitivas de alto nivel que los
    agentes y subsistemas usan para gestionar su ciclo de vida.


    Analogía pedagógica:
      Linux: kernel (syscalls) + userspace (procesos, hilos, IPC)
      MPAT4: CognitiveKernel (Rust) + CognitiveOS (Python) + Agentes
    """


    def __init__(
        self,
        kernel: CognitiveKernelInterface,
        mesh: CognitiveEventMesh,
        scheduling_policy: SchedulingPolicy = SchedulingPolicy.PRIORITY,
    ):
        self._kernel = kernel
        self._mesh = mesh
        self._ipc = CognitiveIPC(mesh=mesh)
        self._scheduler = CognitiveScheduler(kernel=kernel, policy=scheduling_policy)
        self._processes: dict[str, CognitiveProcess] = {}


    async def spawn_process(
        self,
        tenant_id: str,
        agent_id: str,
        unikernel_id: str,
        budget_tokens: int,
        soul_md: Optional[str] = None,
    ) -> CognitiveProcess:
        """
        Crea y activa un nuevo CognitiveProcess.


        Flujo:
          1. Crear CognitiveProcess en estado SPAWNING.
          2. Registrar en CognitiveIPC.
          3. Encolar en CognitiveScheduler.
          4. Activar → estado ACTIVE.
          5. Emitir cognitive_os.process.spawned via mesh.
        """
        pid = str(uuid4())
        process = CognitiveProcess(
            pid=pid,
            tenant_id=tenant_id,
            agent_id=agent_id,
            unikernel_id=unikernel_id,
            budget_tokens=budget_tokens,
            kernel=self._kernel,
            mesh=self._mesh,
            soul_md=soul_md,
        )
        self._processes[pid] = process
        self._ipc.register_process(process)
        await self._scheduler.enqueue(process)
        process.activate()


        import json
        await self._mesh.broadcast_causal(
            tenant_id=tenant_id,
            event_type="cognitive_os.process.spawned",
            payload_bytes=json.dumps({
                "pid": pid, "agent_id": agent_id,
                "unikernel_id": unikernel_id, "budget_tokens": budget_tokens,
            }).encode(),
        )
        logger.info("CognitiveOS: proceso spawned pid=%s agent=%s", pid, agent_id)
        return process


    async def terminate_process(self, pid: str, reason: str = "task_completed") -> None:
        """
        Termina un CognitiveProcess.
        Cancela todos sus threads, libera del scheduler, emite evento.
        """
        process = self._processes.pop(pid, None)
        if not process:
            logger.warning("terminate_process: pid=%s no encontrado", pid)
            return


        # Cancelar threads pendientes
        await process.send_signal(CognitiveSignal.FREEZE)
        process._state = ProcessState.TERMINATED


        self._ipc.unregister_process(pid)
        await self._scheduler.release(pid)


        import json
        await self._mesh.broadcast_causal(
            tenant_id=process.tenant_id,
            event_type="cognitive_os.process.terminated",
            payload_bytes=json.dumps({
                "pid": pid, "agent_id": process.agent_id,
                "reason": reason, "tokens_consumed": process._tokens_consumed,
            }).encode(),
        )
        logger.info("CognitiveOS: proceso terminado pid=%s reason=%s", pid, reason)


    @property
    def ipc(self) -> CognitiveIPC:
        return self._ipc


    @property
    def scheduler(self) -> CognitiveScheduler:
        return self._scheduler


    def os_stats(self) -> dict:
        return {
            "total_processes": len(self._processes),
            "active_processes": sum(
                1 for p in self._processes.values() if p.state == ProcessState.ACTIVE
            ),
            "scheduler": self._scheduler.scheduler_stats(),
        }




# ---------------------------------------------------------------------------
# Excepciones del AI Native OS
# ---------------------------------------------------------------------------


class InsufficientProcessBudget(Exception):
    def __init__(self, pid: str, requested: int, available: int):
        self.pid = pid
        self.requested = requested
        self.available = available
        super().__init__(
            f"INV-OS.2: pid={pid} solicitó {requested} tokens, disponible={available}"
        )




class ProcessNotFound(Exception):
    pass




class ThreadSpawnError(Exception):
    pass