## 2026-09-22T05:56:47Z
You are the implementation worker for Milestone 1: Authentication & Security Hardening.
Your archetype is teamwork_preview_worker.
Your working directory is e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m1.

You MUST read ORIGINAL_REQUEST.md at:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

You MUST also read:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\PROJECT.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\explorer_survey_1\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership (you have exclusive write ownership for Milestone 1):
- cerberus/config.py
- cerberus/api/app.py
- cerberus/api/dependencies.py
- cerberus/cli/main.py
- cerberus/core/database.py

Implementation Tasks:
1. cerberus/config.py:
   - Add CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000"
   - Add property cors_origins_list returning parsed origin list.
   - Add Pydantic validator (@model_validator(mode="after")) to reject default/insecure secret keys (and ensure length >= 32) when ENVIRONMENT is production.
2. cerberus/api/app.py:
   - Update CORSMiddleware configuration to use settings.cors_origins_list.
   - Explicitly ensure wildcard "*" origins cannot be combined with allow_credentials=True.
3. cerberus/core/database.py:
   - In init_db(), ensure tables are created and in development mode (settings.ENVIRONMENT == "development"), seed the default development API key (settings.DEFAULT_DEV_API_KEY) into ApiKeyRecord in the database with active status if not already present.
4. cerberus/api/dependencies.py:
   - In verify_api_key(), eliminate arbitrary prefix bypass (e.g. accepting any token starting with cvai_).
   - Require valid Bearer token format. Compute token_hash = hash_api_key(token).
   - Query ApiKeyRecord from database via AsyncSessionLocal. Verify key is active (is_active=True) and not expired (expires_at is None or in future).
   - In development mode, provide fallback check for settings.DEFAULT_DEV_API_KEY if DB seed was not present, but strictly reject fabricated/unregistered tokens.
   - Raise HTTP 401 for invalid, unregistered, expired, or inactive tokens.
   - Call rate_limiter.is_allowed(token) and return token.
5. cerberus/cli/main.py:
   - In create_api_key CLI command, persist the newly generated key into the database table api_keys as an active ApiKeyRecord.
6. Verification:
   - Execute `python -m pytest` to ensure all existing 23 tests pass with zero regressions.
7. Output:
   - Keep progress.md updated in your working directory.
   - Write full handoff report to e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m1\handoff.md detailing files modified, diff summary, and verification command output.
   - Notify orchestrator upon completion.
