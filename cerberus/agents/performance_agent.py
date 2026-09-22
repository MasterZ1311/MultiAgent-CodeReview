"""
Performance Agent: Specializes in Algorithmic Profiling, Bottlenecks, and Resource Optimization.
"""

import time
from typing import Any, Dict, List, Optional
from cerberus.agents.base import BaseAgent
from cerberus.models.schemas import AgentResult
from cerberus.providers.heuristic_engine import HeuristicEngine


class PerformanceAgent(BaseAgent):
    name = "performance"
    version = "1.1.0"
    purpose = "Detect algorithmic bottlenecks, O(n²) loops, N+1 queries, and memory inefficiencies"

    def get_capabilities(self) -> List[str]:
        return [
            "Algorithmic Complexity Analysis (Big-O)",
            "Nested Iteration Detection (O(n²))",
            "Database N+1 Query Antipatterns",
            "String Concatenation Memory Leaks",
            "Caching Opportunity Identification",
            "Estimated Latency Improvement Calculations"
        ]

    async def analyze(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        start_time = time.perf_counter()

        findings, score = HeuristicEngine.analyze_performance(code, language=language)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return AgentResult(
            name=self.name,
            status="completed",
            score=round(score, 1),
            execution_time_ms=elapsed_ms,
            findings=findings
        )
