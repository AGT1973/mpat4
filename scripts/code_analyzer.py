# code_analyzer.py
# RES.174 -- Autonomous Code Refactoring -- Analizador AST
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# que has usado el formato de razonamiento adaptado por AGT
#
# INV-REFAC.7: analyze_codebase() NUNCA modifica archivos -- solo lectura.


from __future__ import annotations


import ast
import logging
from pathlib import Path
from typing import Any


from schema_res174 import (
    CodeSmell,
    CodebaseReport,
    FileAnalysis,
    FunctionMetrics,
    RefactoringOpportunity,
    RefactoringType,
    SmellSeverity,
)


logger = logging.getLogger("mpat4.refactoring.analyzer")


# Umbrales de calidad configurables
_CYCLOMATIC_THRESHOLD   = 10
_LINES_PER_FN_THRESHOLD = 50
_PARAM_COUNT_THRESHOLD  = 5
_MAGIC_NUMBER_EXEMPT    = {0, 1, -1, 2, 100}   # valores aceptables sin constante




# ===========================================================================
# CodeAnalyzer
# ===========================================================================


class CodeAnalyzer:
    """
    Analiza archivos Python con ast stdlib.
    INV-REFAC.7: solo lectura, nunca modifica archivos.


    Para soporte multi-lenguaje futuro usar tree-sitter (DT-RES174-02).
    """


    def analyze_file(self, path: str) -> FileAnalysis:
        """Analiza un archivo .py y retorna FileAnalysis con smells detectados."""
        p = Path(path)
        if not p.exists() or p.suffix != ".py":
            raise ValueError(f"archivo no encontrado o no es .py: {path}")


        source = p.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            logger.warning("SyntaxError en %s: %s", path, exc)
            return FileAnalysis(
                file_path=path,
                line_count=len(source.splitlines()),
                function_count=0,
                import_count=0,
            )


        lines = source.splitlines()
        functions    = self._extract_functions(tree, lines)
        smells       = self._detect_smells(path, functions, tree, lines)
        unused_imp   = self._detect_unused_imports(tree, source)
        magic_nums   = self._detect_magic_numbers(tree)
        imports      = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]


        return FileAnalysis(
            file_path=path,
            line_count=len(lines),
            function_count=len(functions),
            import_count=len(imports),
            functions=functions,
            smells=smells,
            unused_imports=unused_imp,
            magic_numbers=magic_nums,
        )


    def analyze_directory(self, root: str, exclude: list[str] | None = None) -> CodebaseReport:
        """Recorre directorio y analiza todos los .py. INV-REFAC.7: solo lectura."""
        exclude = exclude or ["__pycache__", ".git", ".venv", "venv", "node_modules"]
        root_path = Path(root)
        analyses: list[FileAnalysis] = []


        for py_file in sorted(root_path.rglob("*.py")):
            if any(ex in py_file.parts for ex in exclude):
                continue
            try:
                fa = self.analyze_file(str(py_file))
                analyses.append(fa)
            except Exception as exc:
                logger.warning("Error analizando %s: %s", py_file, exc)


        total_smells = sum(fa.smell_count for fa in analyses)
        overall_score = (
            sum(fa.quality_score for fa in analyses) / len(analyses)
            if analyses else 1.0
        )


        return CodebaseReport(
            root_path=root,
            files_analyzed=len(analyses),
            total_smells=total_smells,
            file_analyses=analyses,
            overall_score=overall_score,
        )


    def detect_opportunities(self, analysis: FileAnalysis) -> list[RefactoringOpportunity]:
        """Convierte CodeSmells en RefactoringOpportunities priorizadas."""
        opportunities: list[RefactoringOpportunity] = []
        for smell in analysis.smells:
            opp = RefactoringOpportunity(
                file_path=smell.file_path,
                refactoring_type=smell.smell_type,
                severity=smell.severity,
                description=smell.description,
                related_smells=[smell.smell_id],
                estimated_effort=_effort_for_type(smell.smell_type),
                line_start=smell.line_start,
                line_end=smell.line_end,
            )
            opportunities.append(opp)


        # Agregar oportunidades de imports sin usar
        if analysis.unused_imports:
            opportunities.append(RefactoringOpportunity(
                file_path=analysis.file_path,
                refactoring_type=RefactoringType.REMOVE_DEAD_CODE,
                severity=SmellSeverity.LOW,
                description=f"Imports sin usar: {', '.join(analysis.unused_imports)}",
                estimated_effort="low",
                line_start=1,
                line_end=1,
            ))


        return sorted(opportunities)  # HIGH primero via __lt__


    # -----------------------------------------------------------------------
    # Extraccion de funciones
    # -----------------------------------------------------------------------


    def _extract_functions(
        self, tree: ast.AST, lines: list[str]
    ) -> list[FunctionMetrics]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno)
                line_count = end_line - node.lineno + 1
                has_hints  = any(
                    arg.annotation is not None
                    for arg in node.args.args
                ) or node.returns is not None
                has_doc = (
                    isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ) if node.body else False


                functions.append(FunctionMetrics(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=end_line,
                    cyclomatic_complexity=_cyclomatic_complexity(node),
                    line_count=line_count,
                    parameter_count=len(node.args.args),
                    has_type_hints=has_hints,
                    has_docstring=has_doc,
                ))
        return functions


    # -----------------------------------------------------------------------
    # Deteccion de smells
    # -----------------------------------------------------------------------


    def _detect_smells(
        self,
        path: str,
        functions: list[FunctionMetrics],
        tree: ast.AST,
        lines: list[str],
    ) -> list[CodeSmell]:
        smells: list[CodeSmell] = []


        for fn in functions:
            # Funcion demasiado larga
            if fn.line_count > _LINES_PER_FN_THRESHOLD:
                smells.append(CodeSmell(
                    file_path=path,
                    line_start=fn.line_start,
                    line_end=fn.line_end,
                    smell_type=RefactoringType.EXTRACT_FUNCTION,
                    severity=SmellSeverity.HIGH if fn.line_count > 100 else SmellSeverity.MEDIUM,
                    description=f"Funcion '{fn.name}' tiene {fn.line_count} lineas (umbral: {_LINES_PER_FN_THRESHOLD})",
                    metric_value=float(fn.line_count),
                    metric_name="line_count",
                ))


            # Complejidad ciclomatica alta
            if fn.cyclomatic_complexity > _CYCLOMATIC_THRESHOLD:
                smells.append(CodeSmell(
                    file_path=path,
                    line_start=fn.line_start,
                    line_end=fn.line_end,
                    smell_type=RefactoringType.SIMPLIFY_CONDITION,
                    severity=SmellSeverity.HIGH if fn.cyclomatic_complexity > 20 else SmellSeverity.MEDIUM,
                    description=f"Funcion '{fn.name}' CC={fn.cyclomatic_complexity} (umbral: {_CYCLOMATIC_THRESHOLD})",
                    metric_value=float(fn.cyclomatic_complexity),
                    metric_name="cyclomatic_complexity",
                ))


            # Demasiados parametros
            if fn.parameter_count > _PARAM_COUNT_THRESHOLD:
                smells.append(CodeSmell(
                    file_path=path,
                    line_start=fn.line_start,
                    line_end=fn.line_end,
                    smell_type=RefactoringType.EXTRACT_FUNCTION,
                    severity=SmellSeverity.MEDIUM,
                    description=f"Funcion '{fn.name}' tiene {fn.parameter_count} parametros (umbral: {_PARAM_COUNT_THRESHOLD})",
                    metric_value=float(fn.parameter_count),
                    metric_name="parameter_count",
                ))


            # Sin type hints
            if not fn.has_type_hints and fn.line_count > 5:
                smells.append(CodeSmell(
                    file_path=path,
                    line_start=fn.line_start,
                    line_end=fn.line_start,
                    smell_type=RefactoringType.ADD_TYPE_HINTS,
                    severity=SmellSeverity.LOW,
                    description=f"Funcion '{fn.name}' sin type hints",
                ))


        return smells


    def _detect_unused_imports(self, tree: ast.AST, source: str) -> list[str]:
        """Detecta imports que no aparecen en el resto del codigo."""
        imported_names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imported_names.append(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names.append(name)


        # Contar usos (simple: buscar nombre en el source sin contar la linea de import)
        unused = []
        for name in imported_names:
            if name == "*":
                continue
            count = source.count(name)
            # Aparece solo 1 vez (en la linea de import misma)
            if count <= 1:
                unused.append(name)
        return unused


    def _detect_magic_numbers(self, tree: ast.AST) -> list[tuple[int, float]]:
        """Detecta literales numericos fuera de contextos aceptables."""
        magic: list[tuple[int, float]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in _MAGIC_NUMBER_EXEMPT:
                    magic.append((node.lineno, float(node.value)))
        return magic




# ===========================================================================
# Helpers
# ===========================================================================


def _cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Calcula CC (McCabe) como 1 + numero de branching points."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (
            ast.If, ast.While, ast.For, ast.AsyncFor,
            ast.ExceptHandler, ast.With, ast.AsyncWith,
            ast.comprehension, ast.Assert,
        )):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # cada 'and'/'or' agrega un camino
            complexity += len(child.values) - 1
    return complexity




def _effort_for_type(rtype: RefactoringType) -> str:
    _map = {
        RefactoringType.EXTRACT_FUNCTION:   "high",
        RefactoringType.REMOVE_DUPLICATION: "high",
        RefactoringType.SIMPLIFY_CONDITION: "medium",
        RefactoringType.RENAME_VARIABLE:    "low",
        RefactoringType.ADD_TYPE_HINTS:     "low",
        RefactoringType.REMOVE_DEAD_CODE:   "low",
        RefactoringType.EXTRACT_CONSTANT:   "low",
    }
    return _map.get(rtype, "medium")