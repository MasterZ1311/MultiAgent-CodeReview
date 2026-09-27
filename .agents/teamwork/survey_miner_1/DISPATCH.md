## 2026-09-24T14:22:07Z
You are survey_miner_1, an authoritative specification miner and code explorer.
Working directory: e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_1
Parent conversation ID: 40dd2dae-3b0b-4a1f-aff5-27055825037a

MANDATORY FIRST STEP: Read the authoritative requirements in:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

Context & Reference files to inspect:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ENTERPRISE_MULTI_AGENT_CODE_REVIEW_SPEC.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\DOCUMENTATION_SUMMARY.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\codevault\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\docs\

TASK:
Perform a comprehensive survey and extract complete technical specifications for the first 2 target documentation deliverables:
1. `PHASE_1_DETAILED_IMPLEMENTATION.md`:
   - Enumerate all 4 weeks and daily tasks (28 days × 4 weeks: Days 1-7 Week 1, Days 8-14 Week 2, Days 15-21 Week 3, Days 22-28 Week 4) with daily engineering deliverables and acceptance criteria.
   - Design and extract the complete production-ready Python code (500+ lines) for Master Orchestrator Agent using LangGraph, state management (`ReviewState`), tool calling abstraction, result aggregation service, 5 core review agents (Security, Performance, Testing, Documentation, Best Practices), FastAPI application setup, and PostgreSQL connection pooling.
   - Outline 5 comprehensive troubleshooting scenarios with symptoms, diagnosis, and remediation.
   - Detail the CI/CD GitHub Actions pipeline.

2. `AGENT_SPECIFICATIONS.md`:
   - Design and extract full architectural specifications for all 20 agents:
     1. Predictive Bug Detection
     2. Supply Chain Security
     3. Performance Regression
     4. Architecture Violation
     5. Technical Debt Quantifier
     6. Code Fixer
     7. Custom Rule Engine
     8. Multi-Language Reviewer (Python, JavaScript/TypeScript, Java, Go, Rust)
     9. Historical Trend Analysis
     10. ML Code Auditor
     11. Compliance Standards (SOC2, HIPAA, PCI-DSS, ISO27001)
     12. IDE Integration
     13. Cost Analysis (Cloud & LLM)
     14. Accessibility Checker (WCAG 2.2)
     15. Anomaly Detection
     16. Codebase Fine-tuning
     17. Team Expertise Router
     18. Knowledge Base Builder
     19. Burndown Predictor
     20. Collaborative Review
   - For every single one of the 20 agents, specify: ASCII state machine diagram, TypedDict I/O schemas, tool definitions with parameters, watsonx-optimized system/user prompts, error handling, memory management, testing strategy, and integration points.

OUTPUT REQUIREMENTS:
1. Write your detailed technical survey report to:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_1\survey_doc1_2.md
2. Write a complete handoff report following the Handoff Protocol to:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_1\handoff.md
   Include: Observation, Logic Chain, Caveats, Conclusion, Verification Method.
3. Update your progress in:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_1\progress.md
4. Send a completion message to the parent (40dd2dae-3b0b-4a1f-aff5-27055825037a) using send_message with the paths and summary.
