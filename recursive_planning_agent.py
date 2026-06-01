# recursive_planning_agent.py
# RES.175 -- RecursivePlanningAgent -- Agente principal
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# Contrato: CONTRACT_RES175_v1.md (ID: 1hi3kxBupZWoAAx2FBETmAAoUy_xbST0z4WV3bbWqvBU)
# que has usado el formato de razonamiento adaptado por AGT
#
# INVARIANTES:
#   INV-PLAN.1: NUNCA ejecuta sin DAG validado
#   INV-PLAN.2: solo PrimitiveTasks llaman a agentes externos
#   INV-PLAN.3: MaxDepth=5 (en HTNDecomposer)
#   INV-PLAN.4: Mutacion solo reemplaza nodos fallidos, nunca completados
#   INV-PLAN.5: Max 3 mutaciones por DAG
#   INV-PLAN.6: asyncio.gather(return_exceptions=True) para tareas paralelas
#   INV-PLAN.7: solo emit inyectado


from __future__ import annotations


import asyncio
import logging
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any


from htn_decomposer import HTNDecomposer
from schema_res175 import (
    AgentRole,
    DecompositionMethod,
    ExecutionResult,
    PlanStatus,
    PrimitiveTask,
    Task,
    TaskComplexity,
    TaskDAG,
    TaskDelta,
    TaskExecutionRecord,
    TaskStatus,
)


logger = logging.getLogger("mpat4.planner.recursive")


EmitFn  = Callable[[str, dict[str, Any]], None]
LLMFn   = Callable[[str], "Awaitable[str]"]
MCTSFn  = Callable[[list[TaskDAG]], "Awaitable[TaskDAG]"]


MAX_MUTATIONS    = 3   # INV-PLAN.5
PARALLEL_LIMIT   = 8   # max sub-tareas paralelas simultaneas
TASK_TIMEOUT     = 120 # segundos por sub-tarea


# Eventos (INV-PLAN.7)
_EVT_DECOMPOSED    = "plan.decomposed"
_EVT_TASK_STARTED  = "plan.task_started"
_EVT_TASK_COMPLETE = "plan.task_complete"
_EVT_TASK_FAILED   = "plan.task_failed"
_EVT_MUTATED       = "plan.mutated"
_EVT_COMPLETED     = "plan.completed"
_EVT_AUDIT         = "plan.audit"




class RecursivePlanningAgent:
    """
    Agente de planificacion recursiva para MPAT4 (SWE pattern extendido a multi-agente).


    Patron CEO Agent: descompone, delega, coordina, sintetiza.


    Ciclo:
      1. decompose(task) -> TaskDAG via HTN
      2. execute_dag(dag) -> ejecuta en orden topologico con paralelismo
      3. Si sub-tarea falla: _mutate_dag() replanifica ese nodo (max 3 veces)
      4. Sintetiza outputs de todas las hojas en un resultado final


    INV-PLAN.1: execute_dag() valida dag.status == READY antes de ejecutar.
    INV-PLAN.7: No importa nada de MPAT4 -- solo emit + funciones inyectadas.
    """


    def __init__(
        self,
        agent_id:  str,
        tenant_id: str,
        llm_fn:    LLMFn,
        emit:      EmitFn,
        mcts_fn:   MCTSFn | None = None,
        role_fns:  dict[str, LLMFn] | None = None,
    ) -> None:
        self._agent_id  = agent_id
        self._tenant_id = tenant_id
        self._llm_fn    = llm_fn
        self._emit      = emit
        self._mcts_fn   = mcts_fn
        # role_fns: mapa AgentRole -> LLMFn especializada (DT-RES175-05)
        # Si no se inyecta, todos los roles usan llm_fn general
        self._role_fns  = role_fns or {}
        self._decomposer = HTNDecomposer(llm_fn)
        self._active_dags: dict[str, TaskDAG] = {}


    # -----------------------------------------------------------------------
    # decompose -- puerta de entrada
    # -----------------------------------------------------------------------


    async def decompose(self, task: Task) -> TaskDAG:
        """
        Descompone la tarea raiz en un TaskDAG via HTN.
        Si MCTS esta inyectado y complejidad > umbral, evalua alternativas.
        INV-PLAN.1: retorna DAG con status=READY listo para execute_dag().
        """
        complexity = self._decomposer.score_complexity(task)


        if self._mcts_fn and complexity.use_mcts:
            logger.info(
                "decompose: usando MCTS para tarea '%s' (score=%.2f)",
                task.title, complexity.score,
            )
            # Generar 2 DAGs alternativos y dejar que MCTS elija
            dag_a = await self._decomposer.build_dag(task)
            # Segunda variante: prompt ligeramente diferente (parallel-first)
            task_b = task.model_copy(update={"metadata": {"prefer": "parallel"}})
            dag_b = await self._decomposer.build_dag(task_b)
            dag = await self._mcts_fn([dag_a, dag_b])
        else:
            dag = await self._decomposer.build_dag(task)


        dag.status = PlanStatus.READY
        self._active_dags[dag.dag_id] = dag


        self._emit(_EVT_DECOMPOSED, {
            "dag_id":    dag.dag_id,
            "agent_id":  self._agent_id,
            "tenant_id": self._tenant_id,
            "root_task": task.title,
            "task_count": len(dag.tasks),
        })
        logger.info(
            "decompose: DAG '%s' listo con %d tareas", dag.dag_id, len(dag.tasks)
        )
        return dag


    # -----------------------------------------------------------------------
    # execute_dag -- INV-PLAN.1, INV-PLAN.4, INV-PLAN.5, INV-PLAN.6
    # -----------------------------------------------------------------------


    async def execute_dag(self, dag: TaskDAG) -> ExecutionResult:
        """
        Ejecuta el DAG en orden topologico con paralelismo donde sea posible.
        INV-PLAN.1: verifica dag.status == READY antes de ejecutar.
        INV-PLAN.4: mutaciones solo en nodos fallidos.
        INV-PLAN.5: max MAX_MUTATIONS=3 por DAG.
        INV-PLAN.6: asyncio.gather(return_exceptions=True) para paralelas.
        """
        if dag.status != PlanStatus.READY:
            raise ValueError(
                f"INV-PLAN.1: DAG {dag.dag_id} no esta en estado READY "
                f"(estado actual: {dag.status})"
            )


        dag.status = PlanStatus.RUNNING
        t0 = time.monotonic()
        records: list[TaskExecutionRecord] = []


        while not dag.is_complete:
            ready = dag.get_ready_tasks()
            if not ready:
                # No hay tareas listas -- posible deadlock o todas done
                break


            # Agrupar en batches de PARALLEL_LIMIT
            batch   = ready[:PARALLEL_LIMIT]
            results = await asyncio.gather(
                *[self._execute_task(t, dag) for t in batch],
                return_exceptions=True,   # INV-PLAN.6
            )


            for task, result in zip(batch, results):
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error  = str(result)
                    logger.error("execute_dag: tarea '%s' excepcion: %s", task.title, result)
                    self._emit(_EVT_TASK_FAILED, {
                        "dag_id":  dag.dag_id,
                        "task_id": task.task_id,
                        "error":   str(result),
                    })
                elif isinstance(result, TaskExecutionRecord):
                    records.append(result)


            # INV-PLAN.4/5: mutacion si hay fallos y quedan intentos
            failed = dag.failed_tasks
            if failed and dag.mutations < MAX_MUTATIONS:
                for failed_task in failed:
                    delta = await self._mutate_dag(dag, failed_task)
                    if delta:
                        dag.mutations += 1
                        self._emit(_EVT_MUTATED, {
                            "dag_id":         dag.dag_id,
                            "failed_task_id": failed_task.task_id,
                            "mutations":      dag.mutations,
                        })
                        if dag.mutations >= MAX_MUTATIONS:
                            break
            elif failed:
                # Agotadas las mutaciones
                dag.status = PlanStatus.FAILED
                break


        # Sintetizar resultado final
        if dag.status != PlanStatus.FAILED:
            dag.status = (
                PlanStatus.MUTATED if dag.mutations > 0 else PlanStatus.COMPLETED
            )


        dag.completed_at = datetime.utcnow()
        total_ms = int((time.monotonic() - t0) * 1000)


        # Sintetizar outputs de hojas completadas
        completed_outputs = [
            r.output for r in records if r.status == TaskStatus.COMPLETED
        ]
        final_output = await self._synthesize(completed_outputs, dag)


        result = ExecutionResult(
            dag_id=dag.dag_id,
            status=dag.status,
            tasks_total=len(dag.tasks),
            tasks_completed=sum(1 for t in dag.tasks.values() if t.status == TaskStatus.COMPLETED),
            tasks_failed=len(dag.failed_tasks),
            mutations_applied=dag.mutations,
            final_output=final_output,
            records=records,
            total_duration_ms=total_ms,
            total_tokens=sum(r.tokens_used for r in records),
        )


        self._emit(_EVT_COMPLETED, {
            "dag_id":     dag.dag_id,
            "status":     dag.status,
            "tasks_done": result.tasks_completed,
            "mutations":  dag.mutations,
            "duration_ms": total_ms,
        })
        self._emit(_EVT_AUDIT, {
            "dag_id":       dag.dag_id,
            "agent_id":     self._agent_id,
            "tenant_id":    self._tenant_id,
            "status":       dag.status,
            "total_tokens": result.total_tokens,
        })


        return result


    # -----------------------------------------------------------------------
    # _execute_task -- INV-PLAN.2
    # -----------------------------------------------------------------------


    async def _execute_task(
        self, task: Task, dag: TaskDAG
    ) -> TaskExecutionRecord:
        """
        Ejecuta una tarea. INV-PLAN.2: solo PrimitiveTasks llaman al agente.
        """
        if task.complexity == TaskComplexity.COMPOUND:
            # Las COMPOUND no se ejecutan directamente -- error de DAG
            raise ValueError(
                f"INV-PLAN.2: tarea COMPOUND '{task.title}' no debe llegar a execute_task"
            )


        task.status     = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()


        self._emit(_EVT_TASK_STARTED, {
            "dag_id":  dag.dag_id,
            "task_id": task.task_id,
            "title":   task.title,
            "role":    task.assigned_role,
        })


        t0 = time.monotonic()
        primitive = task if isinstance(task, PrimitiveTask) else _coerce_to_primitive(task)


        # Seleccionar LLM segun el rol (DT-RES175-05: especializado por rol)
        role_key = task.assigned_role.value if task.assigned_role else AgentRole.ANALYSIS.value
        llm      = self._role_fns.get(role_key, self._llm_fn)


        try:
            output = await asyncio.wait_for(
                llm(primitive.prompt or f"Ejecuta: {task.title}\n{task.description}"),
                timeout=TASK_TIMEOUT,
            )
            task.status       = TaskStatus.COMPLETED
            task.result       = output
            task.completed_at = datetime.utcnow()


            record = TaskExecutionRecord(
                task_id=task.task_id,
                agent_role=task.assigned_role or AgentRole.ANALYSIS,
                input_prompt=primitive.prompt[:500],
                output=output[:2000],
                status=TaskStatus.COMPLETED,
                duration_ms=int((time.monotonic() - t0) * 1000),
                tokens_used=len(output.split()),
            )
            self._emit(_EVT_TASK_COMPLETE, {
                "dag_id":  dag.dag_id,
                "task_id": task.task_id,
                "tokens":  record.tokens_used,
            })
            return record


        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error  = f"timeout ({TASK_TIMEOUT}s)"
            raise RuntimeError(task.error)
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error  = str(exc)
            raise


    # -----------------------------------------------------------------------
    # _mutate_dag -- INV-PLAN.4
    # -----------------------------------------------------------------------


    async def _mutate_dag(
        self, dag: TaskDAG, failed_task: Task
    ) -> TaskDelta | None:
        """
        Genera una mutacion del DAG para reemplazar el nodo fallido.
        INV-PLAN.4: NUNCA modifica nodos COMPLETED.
        """
        if failed_task.status == TaskStatus.COMPLETED:
            logger.error(
                "INV-PLAN.4 violacion: intento de mutar tarea COMPLETED '%s'",
                failed_task.title,
            )
            return None


        prompt = (
            f"La siguiente sub-tarea del plan fallo. Propone una alternativa.\n"
            f"Tarea: {failed_task.title}\n"
            f"Descripcion: {failed_task.description}\n"
            f"Error: {failed_task.error}\n\n"
            f"Genera UNA tarea alternativa mas simple que logre el mismo objetivo.\n"
            f"Formato:\n"
            f"TASK: <titulo>\n"
            f"DESC: <descripcion breve>\n"
            f"Solo el formato, sin explicaciones."
        )
        try:
            response = await self._llm_fn(prompt)
            lines    = response.strip().splitlines()
            alt_title = ""
            alt_desc  = ""
            for line in lines:
                if line.lower().startswith("task:"):
                    alt_title = line.split(":", 1)[-1].strip()
                elif line.lower().startswith("desc:"):
                    alt_desc = line.split(":", 1)[-1].strip()


            if not alt_title:
                return None


            from htn_decomposer import _force_primitive, _infer_role
            alt_task = Task(
                title=alt_title,
                description=alt_desc,
                dag_id=dag.dag_id,
                parent_id=failed_task.parent_id,
                depends_on=failed_task.depends_on,
                depth=failed_task.depth,
                complexity=TaskComplexity.PRIMITIVE,
                assigned_role=_infer_role(alt_title, alt_desc),
            )
            # Reemplazar el nodo fallido en el DAG
            failed_task.status = TaskStatus.SKIPPED
            dag.add_task(alt_task)


            # Redirigir dependencias que apuntaban al nodo fallido
            for t in dag.tasks.values():
                if failed_task.task_id in t.depends_on:
                    t.depends_on = [
                        alt_task.task_id if d == failed_task.task_id else d
                        for d in t.depends_on
                    ]


            delta = TaskDelta(
                dag_id=dag.dag_id,
                failed_task_id=failed_task.task_id,
                replacement_tasks=[alt_task],
                rationale=f"Reemplazo de '{failed_task.title}' por '{alt_title}'",
            )
            logger.info(
                "_mutate_dag: nodo '%s' reemplazado por '%s'",
                failed_task.title, alt_title,
            )
            return delta


        except Exception as exc:
            logger.error("_mutate_dag error: %s", exc)
            return None


    # -----------------------------------------------------------------------
    # _synthesize -- combina outputs de las hojas en resultado final
    # -----------------------------------------------------------------------


    async def _synthesize(self, outputs: list[str], dag: TaskDAG) -> str:
        """Sintetiza los outputs de las PrimitiveTasks completadas."""
        if not outputs:
            return ""
        if len(outputs) == 1:
            return outputs[0]


        combined = "\n\n---\n\n".join(
            f"[Sub-tarea {i+1}]:\n{out}" for i, out in enumerate(outputs[:10])
        )
        prompt = (
            f"Sintetiza los siguientes outputs de sub-tareas en una respuesta cohesiva y completa.\n"
            f"La tarea raiz era: {dag.tasks.get(dag.root_task_id, Task(title='desconocida')).title}\n\n"
            f"{combined}\n\n"
            f"Genera una respuesta final integrada. Sin cabeceras innecesarias."
        )
        try:
            return await asyncio.wait_for(self._llm_fn(prompt), timeout=60)
        except Exception as exc:
            logger.warning("_synthesize: error en LLM (%s), retornando concatenacion", exc)
            return combined


    # -----------------------------------------------------------------------
    # API publica
    # -----------------------------------------------------------------------


    def get_plan_status(self, dag_id: str) -> PlanStatus | None:
        dag = self._active_dags.get(dag_id)
        return dag.status if dag else None


    def cancel_plan(self, dag_id: str) -> None:
        """Cancela todas las tasks asyncio activas del DAG."""
        dag = self._active_dags.get(dag_id)
        if dag:
            for task in dag.tasks.values():
                if task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.CANCELLED
            dag.status = PlanStatus.FAILED
            self._emit(_EVT_AUDIT, {
                "event":    "plan_cancelled",
                "dag_id":   dag_id,
                "agent_id": self._agent_id,
            })


    async def plan_and_execute(self, task: Task) -> ExecutionResult:
        """Shortcut: decompose + execute_dag en un solo paso."""
        dag = await self.decompose(task)
        return await self.execute_dag(dag)




# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _coerce_to_primitive(task: Task) -> PrimitiveTask:
    from htn_decomposer import _force_primitive
    return _force_primitive(task, task.depth)