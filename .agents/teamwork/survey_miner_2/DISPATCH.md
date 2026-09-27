# Dispatch: survey_miner_2
Role: Spec Miner for Database Design & API Specifications
Working Directory: e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2
Mission: Survey authoritative requirements and design specifications for DATABASE_DESIGN.md and API_SPECIFICATIONS.md
Target Files:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ENTERPRISE_MULTI_AGENT_CODE_REVIEW_SPEC.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\models\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\api\

## 2026-09-24T14:22:07Z
You are survey_miner_2, an authoritative specification miner and code explorer.
Working directory: e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2
Parent conversation ID: 40dd2dae-3b0b-4a1f-aff5-27055825037a

MANDATORY FIRST STEP: Read the authoritative requirements in:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

Context & Reference files to inspect:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ENTERPRISE_MULTI_AGENT_CODE_REVIEW_SPEC.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\models\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\api\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\cerberus\core\
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\docs\

TASK:
Perform a comprehensive survey and extract complete technical specifications for deliverables 3 and 4:
3. `DATABASE_DESIGN.md`:
   - Complete PostgreSQL DDL schemas (50+ SQL statements) covering all 11 domain tables: `reviews`, `security_findings`, `performance_findings`, `testing_findings`, `compliance_results`, `cost_analysis`, `accessibility_reports`, `ml_predictions`, `team_expertise`, `knowledge_base`, `metrics_history`.
   - Complete composite indexes, foreign keys with ON DELETE rules, constraints (CHECK, UNIQUE).
   - Sample data insertion statements for all 11 tables.
   - Complete Alembic migration script (`env.py` and revision `001_initial_schema.py`).
   - Backup/recovery runbooks (WAL archiving, pg_dump, PITR restore step-by-step).
   - Redis caching strategy (keyspace design, serialization, TTLs, cache invalidation events).
   - Connection pooling strategy (asyncpg pool settings, PgBouncer transaction pooling config).
   - Monitoring queries (slow queries, index hit ratio, cache hit ratio, dead tuples/table bloat).

4. `API_SPECIFICATIONS.md`:
   - Full OpenAPI 3.1 YAML specification for all 15+ endpoints.
   - Complete copy-paste ready FastAPI application code with modular file structure (`# File: src/...`).
   - OAuth2 bearer authentication dependency (`verify_api_key`), sliding-window rate limiting middleware, structured RFC 7807 error handling middleware, Pydantic v2 schemas for all requests and responses, logging configuration, API versioning (`/api/v1`).
   - All 15+ endpoints: POST /reviews, GET /reviews/{id}, GET /reviews/{id}/status, POST /reviews/{id}/approve, GET /analytics/trends, POST /rules/custom, POST /teams/expertise, WebSocket /reviews/{id}/stream, etc.

OUTPUT REQUIREMENTS:
1. Write your detailed technical survey report to:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2\survey_doc3_4.md
2. Write a complete handoff report following the Handoff Protocol to:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2\handoff.md
   Include: Observation, Logic Chain, Caveats, Conclusion, Verification Method.
3. Update your progress in:
   e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2\progress.md
4. Send a completion message to the parent (40dd2dae-3b0b-4a1f-aff5-27055825037a) using send_message with the paths and summary.
