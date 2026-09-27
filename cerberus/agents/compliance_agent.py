"""
Compliance Agent: Backward-compatible alias for ComprehensiveComplianceAgent.
Specializes in Regulatory Standards (HIPAA, GDPR, SOC 2, PCI-DSS, CCPA).
"""

from cerberus.agents.compliance.agent import ComprehensiveComplianceAgent

# Alias for seamless backward compatibility with ReviewOrchestrator
ComplianceAgent = ComprehensiveComplianceAgent

__all__ = ["ComplianceAgent", "ComprehensiveComplianceAgent"]
