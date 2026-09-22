"""
Architecture Agent: Specializes in Modular Design, Coupling, and Anti-Patterns.
"""

import time
from typing import Any, Dict, List, Optional
from cerberus.agents.base import BaseAgent
from cerberus.models.schemas import AgentResult
from cerberus.providers.heuristic_engine import HeuristicEngine


class ArchitectureAgent(BaseAgent):
    name = "architecture"
    version = "1.0.0"
    purpose = "Validate system architecture, module coupling, and structural anti-patterns"

    def get_capabilities(self) -> List[str]:
        return [
            "Deep Coupling & Relative Import Detection",
            "Cyclic Dependency Risk Analysis",
            "Single Responsibility Principle (SRP) Verification",
            "Architectural Modularity Scoring"
        ]

    async def analyze(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        start_time = time.perf_counter()

        findings, score = HeuristicEngine.analyze_architecture(code, language=language)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return AgentResult(
            name=self.name,
            status="completed",
            score=round(score, 1),
            execution_time_ms=elapsed_ms,
            findings=findings
        )
