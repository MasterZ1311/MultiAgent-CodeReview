"""
Code Quality Agent: Specializes in Clean Code, Maintainability, and Cognitive Complexity.
"""

import time
from typing import Any, Dict, List, Optional
from cerberus.agents.base import BaseAgent
from cerberus.models.schemas import AgentResult
from cerberus.providers.heuristic_engine import HeuristicEngine


class QualityAgent(BaseAgent):
    name = "quality"
    version = "1.1.0"
    purpose = "Evaluate readability, maintainability, docstring coverage, and clean coding standards"

    def get_capabilities(self) -> List[str]:
        return [
            "Docstring Completeness & API Documentation",
            "Cognitive & Cyclomatic Complexity",
            "Long Method & Monolith Detection",
            "Dangerous Bare Except Clauses",
            "Wildcard Import Pollution",
            "Refactoring & Clean Code Suggestions"
        ]

    async def analyze(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        start_time = time.perf_counter()

        findings, score = HeuristicEngine.analyze_quality(code, language=language)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return AgentResult(
            name=self.name,
            status="completed",
            score=round(score, 1),
            execution_time_ms=elapsed_ms,
            findings=findings
        )
