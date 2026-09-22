"""
Security Agent: Specializes in Threat Modeling, Vulnerability Detection, and OWASP Compliance.
"""

import time
from typing import Any, Dict, List, Optional
from cerberus.agents.base import BaseAgent
from cerberus.models.schemas import AgentResult
from cerberus.providers.heuristic_engine import HeuristicEngine


class SecurityAgent(BaseAgent):
    name = "security"
    version = "1.2.0"
    purpose = "Identify security vulnerabilities, secrets leakage, injection flaws, and CVSS risks"

    def get_capabilities(self) -> List[str]:
        return [
            "SQL Injection Detection (CWE-89)",
            "Command Injection (CWE-78)",
            "Hardcoded Credentials & API Secrets (CWE-798)",
            "Weak Cryptographic Algorithms (CWE-328)",
            "Insecure Object Deserialization (CWE-502)",
            "CVSS 3.1 Severity Scoring",
            "OWASP Top 10 Threat Analysis",
            "Exploitability Probability Estimation"
        ]

    async def analyze(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        start_time = time.perf_counter()
        
        # Analyze via Heuristic & AST rules
        findings, score = HeuristicEngine.analyze_security(code, language=language)

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return AgentResult(
            name=self.name,
            status="completed",
            score=round(score, 1),
            execution_time_ms=elapsed_ms,
            findings=findings
        )
