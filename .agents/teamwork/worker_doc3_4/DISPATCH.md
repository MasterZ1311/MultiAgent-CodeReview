## 2026-09-24T14:28:43Z

You are worker_doc3_4, a specialist database architect and backend API engineer.
Working directory: e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\worker_doc3_4
Parent conversation ID: 40dd2dae-3b0b-4a1f-aff5-27055825037a

MANDATORY FIRST STEP: Read the authoritative requirements in:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

Reference survey report (contains pre-extracted schemas, SQL, and API code):
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\survey_miner_2\survey_doc3_4.md

Additional context:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ENTERPRISE_MULTI_AGENT_CODE_REVIEW_SPEC.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You have exclusive write ownership of these two files in the root directory:
1. `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\DATABASE_DESIGN.md`
2. `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\API_SPECIFICATIONS.md`

REQUIREMENTS FOR DELIVERABLE 3 (`DATABASE_DESIGN.md`):
- Begin with `# Database Design & Optimization Specification`
- Include a complete markdown Table of Contents.
- Complete PostgreSQL schemas (50+ SQL statements) covering all 11 core domain tables:
  1. `reviews`
  2. `security_findings`
  3. `performance_findings`
  4. `testing_findings`
  5. `compliance_results`
  6. `cost_analysis`
  7. `accessibility_reports`
  8. `ml_predictions`
  9. `team_expertise`
  10. `knowledge_base`
  11. `metrics_history`
  Plus auxiliary tables: `api_keys`, `custom_rules`, `review_feedback`.
- All composite indexes (B-tree, GIN for JSONB and arrays, GiST/tsvector for full-text search).
- Foreign keys with strict ON DELETE CASCADE / RESTRICT rules and CHECK constraints.
- Complete sample data insertion SQL statements for all 11 tables.
- Complete Alembic migration scripts (`alembic/env.py` with asyncpg NullPool and revision `alembic/versions/001_initial_schema.py` with complete `upgrade()` and `downgrade()`).
- Disaster recovery & backup runbooks: WAL archiving (`archive_mode = on`), physical `pg_basebackup`, multi-threaded `pg_dump` (-j 4), and 8-step step-by-step Point-In-Time Recovery (PITR) restore runbook.
- Redis caching strategy: keyspace design (`cvai:cache:{sha256}`, `cvai:ratelimit:{hash}`, `cvai:review:status:{id}`), orjson serialization, TTLs, and cache invalidation matrix.
- Connection pooling strategy: client-side `asyncpg` engine configuration (`pool_size=25`, `max_overflow=15`) and enterprise `PgBouncer` transaction pooling (`pool_mode = transaction`, 1,000 client conns).
- Database diagnostic monitoring queries: slow queries via `pg_stat_statements`, index hit ratio, buffer cache hit ratio, dead tuples/table bloat, and connection state analysis.
- End with Summary and pointer to Next Document (`API_SPECIFICATIONS.md`).

REQUIREMENTS FOR DELIVERABLE 4 (`API_SPECIFICATIONS.md`):
- Begin with `# API Specifications & FastAPI Setup`
- Include a complete markdown Table of Contents.
- Full OpenAPI 3.1 YAML specification covering all 15+ endpoints, request bodies, responses, security schemes, and status codes.
- Complete copy-paste ready FastAPI application code with modular file structure (`# File: src/...`):
  - `src/main.py`: Application factory, lifespan, router inclusion, CORS, middleware.
  - `src/config.py`: Pydantic Settings with environment validation and secret key checks.
  - `src/middleware/error_handler.py`: RFC 7807 problem details exception handler.
  - `src/middleware/rate_limit.py`: Redis sliding-window rate limiting.
  - `src/dependencies/auth.py`: OAuth2 Bearer token authentication with cryptographic hash verification against active DB records and scope enforcement.
  - Complete router implementations:
    - `POST /reviews`: Submit code review job (async with Redis task queue).
    - `GET /reviews/{id}`: Retrieve review results.
    - `GET /reviews/{id}/status`: Poll review status.
    - `POST /reviews/{id}/approve`: Approve review / PR sign-off.
    - `POST /reviews/{id}/feedback`: Submit developer feedback.
    - `POST /reviews/batch`: Bounded concurrency batch review submission.
    - `GET /analytics/trends`: Historical review metrics and quality trends.
    - `GET /analytics/repositories/{owner}/{repo}`: Repository quality summary.
    - `POST /rules/custom`: Register custom review rule.
    - `GET /rules/custom`: List active custom rules.
    - `POST /teams/expertise`: Register team domain expertise mapping.
    - `GET /teams/expertise/{team_id}`: Retrieve team expertise profile.
    - `WebSocket /reviews/{id}/stream`: Real-time finding event stream with auth check and disconnect cleanup.
    - `GET /agents`: List available review agents and health status.
    - `GET /config`: Retrieve active system configuration.
    - `PUT /config`: Update dynamic thresholds.
    - `GET /health` & `GET /ready`: Kubernetes health and readiness probes.
    - `POST /webhooks/github`: GitHub pull request webhook handler.
  - Pydantic v2 schemas for all requests and responses.
  - Logging configuration and API versioning (`/api/v1`).
- End with Summary and pointer to Next Document (`DEPLOYMENT_GUIDE.md`).

STRICT ACCEPTANCE CRITERIA FOR BOTH FILES:
- All code blocks must specify syntax language (`python`, `yaml`, `sql`, `bash`, `json`) and contain file paths (`# File: src/...`).
- No pseudo-code, placeholders, or `TODO` markers; all configurations, schemas, and code implementations are complete and copy-paste ready.

REPORTING:
- Update `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\worker_doc3_4\progress.md`
- Write `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\teamwork\worker_doc3_4\handoff.md`
- Send completion message to parent (40dd2dae-3b0b-4a1f-aff5-27055825037a).
