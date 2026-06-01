# htn_decomposer.py
# RES.175 -- HTN Decomposer (Hierarchical Task Network)
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# que has usado el formato de razonamiento adaptado por AGT
#
# INV-PLAN.2: solo PrimitiveTasks llaman a agentes externos
# INV-PLAN.3: MaxDepth=5


from __future__ import annotations


import logging
from collections.abc import Callable
from typing import Any


from schema_res175 import (
    AgentRole,
    ComplexityScore,
    DecompositionMethod,
    DecompositionResult,
    PrimitiveTask,
    Task,
    TaskComplexity,
    TaskDAG,
)


logger = logging.getLogger("mpat4.planner.htn")


MAX_DEPTH  = 5   # INV-PLAN.3
LLMFn      = Callable[[str], "Awaitable[str]"]


# Palabras clave que indican una tarea COMPOUND
_COMPOUND_SIGNALS = {
    "analiza", "investiga", "desarrolla", "implementa", "crea", "diseña",
    "planifica", "coordina", "sintetiza", "compara", "evalua", "gestiona",
    "analyze", "research", "develop", "implement", "create", "design",
    "plan", "coordinate", "synthesize", "compare", "evaluate", "manage",
}


_PRIMITIVE_SIGNALS = {
    "busca", "extrae", "escribe", "genera", "ejecuta", "verifica",
    "resume", "traduce", "calcula", "lista", "formatea",
    "search", "extract", "write", "generate", "execute", "verify",
    "summarize", "translate", "calculate", "list", "format",
}




class HTNDecomposer:
    """
    Descomposicion Hierarchical Task Network para MPAT4.


    Convierte una Task COMPOUND en un grafo de PrimitiveTasks
    asignando roles de agentes especializados a cada hoja.


    INV-PLAN.2: solo las hojas (PrimitiveTask) interactuan con agentes.
    INV-PLAN.3: profundidad maxima = MAX_DEPTH = 5.
    """


    def __init__(self, llm_fn: LLMFn) -> None:
        self._llm_fn = llm_fn


    async def decompose(self, task: Task, depth: int = 0) -> DecompositionResult:
        """
        Descompone una Task recursivamente hasta alcanzar PrimitiveTasks.
        INV-PLAN.3: si depth >= MAX_DEPTH, convierte en PRIMITIVE directamente.
        """
        if depth >= MAX_DEPTH:
            logger.warning(
                "HTNDecomposer: MaxDepth alcanzado en tarea '%s', forzando PRIMITIVE",
                task.title,
            )
            primitive = _force_primitive(task, depth)
            return DecompositionResult(
                parent_task_id=task.task_id,
                method=DecompositionMethod.SEQUENTIAL,
                sub_tasks=[primitive],
                depth=depth,
                rationale="MaxDepth alcanzado -- convertido a PRIMITIVE",
            )


        complexity = self.classify_task(task)
        if complexity == TaskComplexity.PRIMITIVE:
            primitive = _to_primitive(task, depth)
            return DecompositionResult(
                parent_task_id=task.task_id,
                method=DecompositionMethod.SEQUENTIAL,
                sub_tasks=[primitive],
                depth=depth,
                rationale="Tarea clasificada como PRIMITIVE",
            )


        # Pedir al LLM que descomponga
        prompt = _build_decompose_prompt(task, depth)
        response = await self._llm_fn(prompt)
        method, sub_tasks_raw = _parse_decompose_response(response, task, depth)


        # Asignar roles a cada sub-tarea
        for st in sub_tasks_raw:
            st.assigned_role = _infer_role(st.title, st.description)


        return DecompositionResult(
            parent_task_id=task.task_id,
            method=method,
            sub_tasks=sub_tasks_raw,
            depth=depth,
            rationale=f"Descompuesta en {len(sub_tasks_raw)} sub-tareas via LLM",
        )


    def classify_task(self, task: Task) -> TaskComplexity:
        """
        Clasifica una tarea como PRIMITIVE o COMPOUND.
        Heuristica basada en: senales en titulo, descripcion corta, estimacion de pasos.
        """
        text = (task.title + " " + task.description).lower()
        words = set(text.split())


        compound_hits  = len(words & _COMPOUND_SIGNALS)
        primitive_hits = len(words & _PRIMITIVE_SIGNALS)


        # Descripcion muy corta (< 10 palabras) generalmente es primitiva
        if len(text.split()) < 10 and primitive_hits >= 1:
            return TaskComplexity.PRIMITIVE


        if compound_hits > primitive_hits and len(text.split()) > 15:
            return TaskComplexity.COMPOUND


        # Por defecto: si hay sub-objetivos implicitos (":"), es COMPOUND
        if ":" in task.title or "y" in task.title.lower():
            return TaskComplexity.COMPOUND


        return TaskComplexity.PRIMITIVE


    def score_complexity(self, task: Task) -> ComplexityScore:
        """Estima complejidad numerica para decidir si invocar MCTS."""
        text  = task.title + " " + task.description
        words = text.split()


        estimated_steps  = max(1, len(words) // 10)
        estimated_tokens = len(words) * 20  # estimacion gruesa
        sub_objectives   = text.count(":") + text.count(" y ") + text.count(" and ")


        score = min(1.0, (estimated_steps * 0.3 + sub_objectives * 0.4 +
                          (1 if self.classify_task(task) == TaskComplexity.COMPOUND else 0) * 0.3))


        return ComplexityScore(
            task_id=task.task_id,
            score=score,
            estimated_steps=estimated_steps,
            estimated_tokens=estimated_tokens,
            sub_objectives=sub_objectives,
            use_mcts=score >= 0.7,
        )


    async def build_dag(self, root_task: Task) -> TaskDAG:
        """
        Construye el TaskDAG completo a partir de la tarea raiz.
        Descompone recursivamente hasta que todas las hojas sean PRIMITIVE.
        """
        dag = TaskDAG(root_task_id=root_task.task_id)
        dag.add_task(root_task)
        await self._expand_task(root_task, dag, depth=0)
        return dag


    async def _expand_task(self, task: Task, dag: TaskDAG, depth: int) -> None:
        """Expande recursivamente una tarea en el DAG."""
        result = await self.decompose(task, depth)


        prev_id: str | None = None
        for i, sub in enumerate(result.sub_tasks):
            # Dependencias segun el metodo
            if result.method == DecompositionMethod.SEQUENTIAL and prev_id:
                sub.depends_on = [prev_id]
            elif result.method == DecompositionMethod.PARALLEL:
                sub.depends_on = []   # independientes
            else:
                if prev_id:
                    sub.depends_on = [prev_id]


            sub.parent_id = task.task_id
            sub.depth     = depth + 1
            dag.add_task(sub)


            if sub.complexity == TaskComplexity.COMPOUND and depth + 1 < MAX_DEPTH:
                await self._expand_task(sub, dag, depth + 1)


            if result.method == DecompositionMethod.SEQUENTIAL:
                prev_id = sub.task_id




# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_decompose_prompt(task: Task, depth: int) -> str:
    return (
        f"Descompone la siguiente tarea en sub-tareas atomicas y ejecutables.\n"
        f"Nivel de profundidad actual: {depth}/{MAX_DEPTH}\n"
        f"Tarea: {task.title}\n"
        f"Descripcion: {task.description}\n\n"
        f"Responde con una lista de sub-tareas en este formato:\n"
        f"METHOD: sequential | parallel | conditional\n"
        f"TASK: <titulo breve>\n"
        f"DESC: <descripcion de una oracion>\n"
        f"(repite TASK/DESC para cada sub-tarea)\n\n"
        f"Reglas:\n"
        f"- Maximo 5 sub-tareas\n"
        f"- Cada sub-tarea debe ser concreta y ejecutable\n"
        f"- Prefiere parallel cuando las sub-tareas son independientes\n"
        f"- Usa sequential cuando una depende del resultado de la anterior\n"
        f"Solo el formato pedido, sin explicaciones adicionales."
    )




def _parse_decompose_response(
    response: str, parent: Task, depth: int
) -> tuple[DecompositionMethod, list[Task]]:
    lines   = response.strip().splitlines()
    method  = DecompositionMethod.SEQUENTIAL
    tasks:  list[Task] = []
    current_title = ""
    current_desc  = ""


    for line in lines:
        low = line.lower().strip()
        if low.startswith("method:"):
            method_str = low.split(":", 1)[-1].strip()
            if "parallel" in method_str:
                method = DecompositionMethod.PARALLEL
            elif "conditional" in method_str:
                method = DecompositionMethod.CONDITIONAL
        elif low.startswith("task:"):
            if current_title:
                tasks.append(Task(
                    title=current_title,
                    description=current_desc,
                    depth=depth + 1,
                    parent_id=parent.task_id,
                ))
            current_title = line.split(":", 1)[-1].strip()
            current_desc  = ""
        elif low.startswith("desc:"):
            current_desc = line.split(":", 1)[-1].strip()


    if current_title:
        tasks.append(Task(
            title=current_title,
            description=current_desc,
            depth=depth + 1,
            parent_id=parent.task_id,
        ))


    if not tasks:
        # Fallback: la tarea original como PRIMITIVE
        tasks = [_force_primitive(parent, depth)]


    return method, tasks[:5]  # max 5 sub-tareas




def _to_primitive(task: Task, depth: int) -> PrimitiveTask:
    return PrimitiveTask(
        task_id=task.task_id,
        dag_id=task.dag_id,
        title=task.title,
        description=task.description,
        depth=depth,
        parent_id=task.parent_id,
        depends_on=task.depends_on,
        assigned_role=task.assigned_role or _infer_role(task.title, task.description),
        prompt=f"Ejecuta la siguiente tarea: {task.title}\n{task.description}",
    )




def _force_primitive(task: Task, depth: int) -> PrimitiveTask:
    """Convierte cualquier tarea en PRIMITIVE (MaxDepth o fallback)."""
    return PrimitiveTask(
        task_id=task.task_id,
        title=task.title,
        description=task.description,
        depth=depth,
        parent_id=task.parent_id,
        depends_on=task.depends_on,
        assigned_role=task.assigned_role or AgentRole.ANALYSIS,
        prompt=f"{task.title}: {task.description}",
    )




def _infer_role(title: str, description: str) -> AgentRole:
    """Infiere el AgentRole apropiado basado en el titulo y descripcion."""
    text = (title + " " + description).lower()
    if any(w in text for w in ("busca", "investiga", "search", "research", "fuente", "source")):
        return AgentRole.RESEARCH
    if any(w in text for w in ("codigo", "code", "implementa", "implement", "script", "funcion")):
        return AgentRole.CODE
    if any(w in text for w in ("escribe", "redacta", "write", "draft", "documento", "report")):
        return AgentRole.WRITE
    if any(w in text for w in ("verifica", "revisa", "review", "test", "valida", "validate")):
        return AgentRole.REVIEW
    if any(w in text for w in ("planifica", "plan", "descompone", "decompose", "coordina")):
        return AgentRole.PLAN
    return AgentRole.ANALYSIS