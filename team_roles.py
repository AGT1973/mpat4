# team_roles.py
# RES.176 -- Synthetic Software Teams -- Roles
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# que has usado el formato de razonamiento adaptado por AGT


from __future__ import annotations


import logging
from collections.abc import Callable
from typing import Any


from schema_res176 import (
    ArchitectureDocument,
    CodeArtifact,
    DocumentationArtifact,
    PMEvaluation,
    PRDDocument,
    ProjectResult,
    QAVerdict,
    ReviewResult,
    TeamArtifact,
    TeamContext,
    TeamPhase,
    TeamRole,
    TestArtifact,
)


logger = logging.getLogger("mpat4.synthetic_teams.roles")
LLMFn = Callable[[str], "Awaitable[str]"]




# ===========================================================================
# RoleAgent -- base
# ===========================================================================


class RoleAgent:
    """Agente de rol base. Cada rol especializado lo extiende."""


    def __init__(self, role: TeamRole, llm_fn: LLMFn) -> None:
        self.role   = role
        self._llm   = llm_fn


    async def execute(self, context: TeamContext) -> TeamArtifact:
        raise NotImplementedError


    def _token_count(self, text: str) -> int:
        return len(text.split())




# ===========================================================================
# PMAgent
# ===========================================================================


class PMAgent(RoleAgent):
    """
    Product Manager: convierte el ProjectBrief en un PRD estructurado.
    Tambien ejecuta Self-Rewarding al final (INV-TEAM.5).
    """


    def __init__(self, llm_fn: LLMFn) -> None:
        super().__init__(TeamRole.PM, llm_fn)


    async def execute(self, context: TeamContext) -> PRDDocument:
        brief = context.brief
        prompt = (
            f"Eres un Product Manager senior. Genera un PRD (Product Requirements Document) completo.\n\n"
            f"Proyecto: {brief.title}\n"
            f"Descripcion: {brief.description}\n"
            f"Requerimientos del usuario: {'; '.join(brief.requirements)}\n"
            f"Stack tecnologico: {', '.join(brief.tech_stack) or 'Python'}\n"
            f"Restricciones: {'; '.join(brief.constraints)}\n\n"
            f"Genera el PRD con estas secciones:\n"
            f"## Objetivo\n## Alcance\n## Requerimientos Funcionales\n"
            f"## Requerimientos No Funcionales\n## Criterios de Exito\n## Riesgos\n\n"
            f"Sé concreto y preciso. El output sera usado por el arquitecto para disenar la solucion."
        )
        content = await self._llm(prompt)
        reqs   = [l.strip() for l in content.splitlines() if l.strip().startswith("-")]
        return PRDDocument(
            project_id=context.project_id,
            content=content,
            requirements_extracted=reqs[:20],
            success_criteria=_extract_section(content, "Criterios de Exito"),
        )


    async def self_reward(self, context: TeamContext, result: ProjectResult) -> PMEvaluation:
        """INV-TEAM.5: PM evalua el output final del equipo."""
        prd_reqs   = context.prd.requirements_extracted if context.prd else []
        final_docs = context.docs_artifact.content[:500] if context.docs_artifact else ""
        final_code = "\n".join(a.content[:200] for a in context.code_artifacts[:3])


        prompt = (
            f"Eres el PM que definiste el PRD. Evalua si el resultado del equipo cumple los requerimientos.\n\n"
            f"Requerimientos del PRD: {'; '.join(prd_reqs[:10])}\n"
            f"Codigo generado (extracto): {final_code}\n"
            f"Documentacion (extracto): {final_docs}\n\n"
            f"Responde con:\n"
            f"SCORE: 0.0-1.0\n"
            f"MEETS_PRD: si | no\n"
            f"NOTES: <observaciones en 2-3 oraciones>"
        )
        response = await self._llm(prompt)
        score, meets, notes = _parse_pm_eval(response)
        return PMEvaluation(
            project_id=context.project_id,
            score=score,
            meets_prd=meets,
            quality_notes=notes,
            approved=score >= 0.7,
        )




# ===========================================================================
# ARCHAgent
# ===========================================================================


class ARCHAgent(RoleAgent):
    """Arquitecto: convierte el PRD en un Architecture Document."""


    def __init__(self, llm_fn: LLMFn) -> None:
        super().__init__(TeamRole.ARCH, llm_fn)


    async def execute(self, context: TeamContext) -> ArchitectureDocument:
        prd_content = context.prd.content if context.prd else context.brief.description
        stack       = ", ".join(context.brief.tech_stack) or "Python, pydantic"


        prompt = (
            f"Eres un Arquitecto de Software senior. Disenha la arquitectura para este proyecto.\n\n"
            f"PRD:\n{prd_content[:1500]}\n\n"
            f"Stack: {stack}\n\n"
            f"Genera el Architecture Document con:\n"
            f"## Patron Arquitectonico\n## Componentes Principales\n"
            f"## Interfaces y Contratos\n## Estructura de Archivos\n"
            f"## Decisiones de Diseno (ADRs)\n## Dependencias\n\n"
            f"Sé especifico: nombra clases, metodos y tipos. El DEV lo implementara directamente."
        )
        content    = await self._llm(prompt)
        components = _extract_items(content, "Componentes")
        patterns   = _extract_items(content, "Patron")


        return ArchitectureDocument(
            project_id=context.project_id,
            content=content,
            components=components[:10],
            patterns=patterns[:5],
        )




# ===========================================================================
# DEVAgent
# ===========================================================================


class DEVAgent(RoleAgent):
    """
    Desarrollador: implementa el codigo segun la arquitectura.
    Max 500 lineas por archivo generado.
    """


    def __init__(self, llm_fn: LLMFn) -> None:
        super().__init__(TeamRole.DEV, llm_fn)


    async def execute(self, context: TeamContext) -> CodeArtifact:
        arch_content = context.architecture.content if context.architecture else ""
        last_review  = context.last_review


        feedback_section = ""
        if last_review and not last_review.approved:
            issues_str    = "\n".join(f"- {i}" for i in last_review.issues)
            feedback_section = (
                f"\n\nFEEDBACK DE QA (intento {last_review.attempt}):\n{issues_str}\n"
                f"Corrije estos problemas en esta nueva version.\n"
            )


        prompt = (
            f"Eres un Desarrollador Python senior. Implementa el proyecto segun la arquitectura.\n\n"
            f"Titulo: {context.brief.title}\n"
            f"Arquitectura:\n{arch_content[:2000]}\n"
            f"{feedback_section}\n"
            f"Genera el codigo Python completo y funcional.\n"
            f"Maximo 500 lineas. Usa pydantic, type hints, docstrings.\n"
            f"Incluye solo el codigo, sin explicaciones adicionales.\n"
            f"Formato: un bloque de codigo Python coherente y ejecutable."
        )
        content = await self._llm(prompt)
        # Limpiar marcadores de codigo si el LLM los incluye
        content = _clean_code_block(content)
        # Truncar a 500 lineas
        lines   = content.splitlines()
        if len(lines) > 500:
            content = "\n".join(lines[:500])
            logger.info("DEVAgent: codigo truncado a 500 lineas")


        return CodeArtifact(
            project_id=context.project_id,
            content=content,
            filename=_infer_filename(context.brief.title),
        )




# ===========================================================================
# QAAgent
# ===========================================================================


class QAAgent(RoleAgent):
    """
    QA: genera tests y revisa el codigo de DEV. INV-TEAM.3: obligatorio antes de DOCS.
    """


    def __init__(self, llm_fn: LLMFn) -> None:
        super().__init__(TeamRole.QA, llm_fn)


    async def execute(self, context: TeamContext) -> TestArtifact:
        """Genera el test suite para el codigo de DEV."""
        last_code = context.code_artifacts[-1].content if context.code_artifacts else ""
        prompt = (
            f"Eres un QA Engineer senior. Genera un test suite pytest para este codigo.\n\n"
            f"Codigo a testear:\n```python\n{last_code[:2000]}\n```\n\n"
            f"Genera tests que verifiquen:\n"
            f"1. Casos nominales (happy path)\n"
            f"2. Casos de error y edge cases\n"
            f"3. Invariantes del sistema\n\n"
            f"Usa pytest. Incluye fixtures si es necesario.\n"
            f"Solo el codigo de tests, sin explicaciones."
        )
        content    = await self._llm(prompt)
        content    = _clean_code_block(content)
        tests_count = content.count("def test_")


        return TestArtifact(
            project_id=context.project_id,
            content=content,
            filename=f"test_{_infer_filename(context.brief.title)}",
            tests_count=tests_count,
        )


    async def review(self, artifact: CodeArtifact, context: TeamContext) -> ReviewResult:
        """Revisa el codigo de DEV y decide APPROVED o REJECTED."""
        arch_content = context.architecture.content[:800] if context.architecture else ""
        attempt      = context.dev_attempts


        prompt = (
            f"Eres un QA Engineer. Revisa este codigo Python contra la arquitectura.\n\n"
            f"Arquitectura (extracto):\n{arch_content}\n\n"
            f"Codigo a revisar:\n```python\n{artifact.content[:2000]}\n```\n\n"
            f"Evalua:\n"
            f"1. Cumple los contratos de la arquitectura\n"
            f"2. Tiene type hints y docstrings\n"
            f"3. Maneja errores correctamente\n"
            f"4. No tiene codigo muerto ni imports sin usar\n\n"
            f"Responde con:\n"
            f"VERDICT: approved | rejected\n"
            f"SCORE: 0.0-1.0\n"
            f"ISSUES: <lista de problemas, uno por linea con '-'>\n"
            f"SUGGESTIONS: <lista de mejoras, uno por linea con '+'>"
        )
        response = await self._llm(prompt)
        verdict, score, issues, suggestions = _parse_qa_review(response)


        return ReviewResult(
            project_id=context.project_id,
            artifact_id=artifact.artifact_id,
            verdict=verdict,
            issues=issues,
            suggestions=suggestions,
            score=score,
            attempt=attempt,
        )




# ===========================================================================
# DOCSAgent
# ===========================================================================


class DOCSAgent(RoleAgent):
    """Documentador: genera README + docstrings + API reference."""


    def __init__(self, llm_fn: LLMFn) -> None:
        super().__init__(TeamRole.DOCS, llm_fn)


    async def execute(self, context: TeamContext) -> DocumentationArtifact:
        code_content  = "\n\n".join(a.content[:500] for a in context.code_artifacts[:3])
        arch_content  = context.architecture.content[:600] if context.architecture else ""
        test_count    = context.test_artifact.tests_count if context.test_artifact else 0
        qa_score      = context.last_review.score if context.last_review else 1.0


        prompt = (
            f"Eres un Technical Writer. Genera la documentacion completa para este proyecto.\n\n"
            f"Titulo: {context.brief.title}\n"
            f"Descripcion: {context.brief.description}\n"
            f"Arquitectura (extracto):\n{arch_content}\n"
            f"Codigo (extracto):\n```python\n{code_content}\n```\n"
            f"Tests: {test_count} tests generados. QA score: {qa_score:.2f}\n\n"
            f"Genera un README.md completo con:\n"
            f"## Overview\n## Instalacion\n## Uso\n## API Reference\n"
            f"## Arquitectura\n## Tests\n## Contribucion\n\n"
            f"En markdown. Incluye ejemplos de codigo donde sea relevante."
        )
        content = await self._llm(prompt)
        return DocumentationArtifact(
            project_id=context.project_id,
            content=content,
            filename="README.md",
        )




# ===========================================================================
# Factory
# ===========================================================================


def create_team(llm_fn: LLMFn, role_fns: dict[str, LLMFn] | None = None) -> dict[str, RoleAgent]:
    """
    Factory de agentes por rol.
    Si role_fns tiene LLMFn especializadas por rol, las usa. Sino, usa llm_fn para todos.
    DT-RES176-01: en produccion cada rol usara su propio LLM especializado.
    """
    rf = role_fns or {}
    return {
        TeamRole.PM:   PMAgent(rf.get(TeamRole.PM, llm_fn)),
        TeamRole.ARCH: ARCHAgent(rf.get(TeamRole.ARCH, llm_fn)),
        TeamRole.DEV:  DEVAgent(rf.get(TeamRole.DEV, llm_fn)),
        TeamRole.QA:   QAAgent(rf.get(TeamRole.QA, llm_fn)),
        TeamRole.DOCS: DOCSAgent(rf.get(TeamRole.DOCS, llm_fn)),
    }




# ===========================================================================
# Helpers internos
# ===========================================================================


def _extract_section(content: str, section_name: str) -> list[str]:
    lines   = content.splitlines()
    in_sec  = False
    results = []
    for line in lines:
        if section_name.lower() in line.lower() and line.startswith("#"):
            in_sec = True
            continue
        if in_sec:
            if line.startswith("#"):
                break
            if line.strip().startswith("-"):
                results.append(line.strip().lstrip("- "))
    return results[:10]




def _extract_items(content: str, keyword: str) -> list[str]:
    lines = content.splitlines()
    items = []
    for i, line in enumerate(lines):
        if keyword.lower() in line.lower():
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip().startswith(("-", "*", "•")):
                    items.append(lines[j].strip().lstrip("-*• "))
                elif lines[j].startswith("#"):
                    break
    return items[:10]




def _clean_code_block(text: str) -> str:
    """Elimina marcadores ```python y ``` del texto del LLM."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)




def _infer_filename(title: str) -> str:
    """Convierte el titulo del proyecto en un nombre de archivo Python."""
    name = title.lower().replace(" ", "_")
    name = "".join(c for c in name if c.isalnum() or c == "_")
    return f"{name[:40]}.py"




def _parse_qa_review(response: str) -> tuple[QAVerdict, float, list[str], list[str]]:
    verdict     = QAVerdict.APPROVED
    score       = 0.8
    issues      = []
    suggestions = []


    for line in response.splitlines():
        low = line.lower().strip()
        if low.startswith("verdict:"):
            if "rejected" in low:
                verdict = QAVerdict.REJECTED
        elif low.startswith("score:"):
            try:
                score = float(low.split(":", 1)[-1].strip())
            except ValueError:
                pass
        elif line.strip().startswith("-"):
            issues.append(line.strip().lstrip("- "))
        elif line.strip().startswith("+"):
            suggestions.append(line.strip().lstrip("+ "))


    return verdict, min(1.0, max(0.0, score)), issues, suggestions




def _parse_pm_eval(response: str) -> tuple[float, bool, str]:
    score   = 0.8
    meets   = True
    notes   = ""


    for line in response.splitlines():
        low = line.lower().strip()
        if low.startswith("score:"):
            try:
                score = float(low.split(":", 1)[-1].strip())
            except ValueError:
                pass
        elif low.startswith("meets_prd:"):
            meets = "si" in low or "yes" in low or "true" in low
        elif low.startswith("notes:"):
            notes = line.split(":", 1)[-1].strip()


    return min(1.0, max(0.0, score)), meets, notes