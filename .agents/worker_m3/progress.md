# Progress — Milestone 3: Orchestrator Reliability & WebSocket Safety

Last visited: 2026-09-22T06:59:32Z

## Current Status: Investigating & Baseline Testing

### Plan & Checklist
- [ ] Task 0: Establish baseline by running pytest on current codebase (confirming 301 passing tests).
- [ ] Task 1: Investigate current implementations of:
  - `cerberus/agents/orchestrator.py`
  - `cerberus/api/v1/review.py`
  - `cerberus/models/database.py`
  - `cerberus/core/security.py` and `cerberus/api/dependencies.py` (for auth/hashing references)
- [ ] Task 2: Implement `cerberus/models/database.py`:
  - Add `api_key_hash = Column(String(128), nullable=True, index=True)` to `CodeReviewRecord`.
- [ ] Task 3: Implement `cerberus/agents/orchestrator.py`:
  - Agent crash returns `AgentResult(name=agent_name, status="failed", score=0.0, ...)`
  - Overall score calculation: failed agents contribute 0.0 points to weighted average
  - Review status: if all failed -> overall_score=0.0, status="failed"; if any failed -> status="degraded"; if all succeeded -> status="completed"
  - Cache poisoning prevention: only cache if status == "completed" and no failed agents; never cache "degraded" or "failed".
- [ ] Task 4: Implement `cerberus/api/v1/review.py`:
  - WebSocket authentication: query params `token` or `authorization` header, validate against `ApiKeyRecord` or dev fallback. Close with 1008 if invalid.
  - WebSocket connection lifecycle & cleanup: try...finally removing socket, deleting empty review_id key.
  - Broadcast dead socket removal: delete failed sockets immediately, prune empty keys.
  - Review history authorization: `verify_api_key` dependency, persist `api_key_hash` in `_persist_review_record`, verify matching caller hash or "admin" scope in `get_review_status()` and `get_review_results()`, check `reviews_store` caller isolation as well.
- [ ] Task 5: Add tests for Milestone 3 requirements:
  - Agent crash scoring (0.0) & degradation / failed statuses
  - Cache poisoning prevention on crash
  - WebSocket stream authentication (valid token, invalid token, missing token)
  - WebSocket cleanup on disconnect and broadcast failure
  - Review history tenant isolation (same tenant access vs cross-tenant rejection)
- [ ] Task 6: Run full pytest suite, ensure 0 regressions, all new tests pass.
- [ ] Task 7: Self-critique, write handoff report in `handoff.md`, notify orchestrator.
