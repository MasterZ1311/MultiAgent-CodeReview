## 2026-09-22T06:59:32Z

You are the implementation worker for Milestone 3: Orchestrator Reliability & WebSocket Safety.
Your archetype is teamwork_preview_worker.
Your working directory is e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m3.

You MUST read ORIGINAL_REQUEST.md at:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

You MUST also read:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\PROJECT.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\spec_miner_survey_3\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership (you have exclusive write ownership for Milestone 3):
- cerberus/agents/orchestrator.py
- cerberus/api/v1/review.py
- cerberus/models/database.py

Implementation Tasks:
1. cerberus/agents/orchestrator.py:
   - In run_agent(agent_name):
     When an agent crashes or raises an exception during agent.analyze(), return:
     AgentResult(name=agent_name, status="failed", score=0.0, execution_time_ms=..., error=str(e), findings=[])
     (Assign 0.0 failing score, NOT 100.0).
   - In execute_review(request):
     - In weighted score calculation: crashed/failed agents contribute 0.0 points to the weighted average.
     - Review status determination:
       - If ALL requested agents failed, set overall_score = 0.0 and status = "failed".
       - If ANY agent failed (but not all), set status = "degraded".
       - If ALL agents succeeded, set status = "completed".
     - Cache poisoning prevention:
       - Only save review to cache via cache_manager.set(cache_key, response.model_dump()) if response.status == "completed" and no agents failed.
       - NEVER cache reviews that are "degraded" or "failed".

2. cerberus/api/v1/review.py:
   - WebSocket stream authentication in websocket_review_stream(websocket: WebSocket, review_id: str):
     - Authenticate the client before accepting the connection:
       Extract token from query parameters: token = websocket.query_params.get("token") or websocket.headers.get("authorization").
       Validate token against ApiKeyRecord in the database using hash_api_key(token), checking is_active and expiration (with dev fallback in dev mode if token == settings.DEFAULT_DEV_API_KEY).
       If invalid, missing, inactive, or expired, reject the connection:
       await websocket.close(code=1008, reason="Authentication failed") and return immediately.
     - WebSocket connection lifecycle & cleanup:
       - Accept connection and register in ws_connections[review_id].
       - Wrap stream handling in a try ... finally block:
         In finally:
           Remove websocket from ws_connections[review_id] if present.
           If len(ws_connections[review_id]) == 0:
             del ws_connections[review_id]
           (Ensures disconnected sockets are cleaned up and empty review_id keys are removed from ws_connections under clean disconnect, exceptions, or cancellation).
     - Broadcasting in submit_review():
       - When iterating over ws_connections[response.review_id], if ws.send_text() raises an exception, remove that dead socket from ws_connections[response.review_id] immediately. If empty, delete the key.
   - Review history and stored source code security in get_review_status() and get_review_results():
     - Require api_key via Depends(verify_api_key).
     - In _persist_review_record(request, response, api_key): store api_key_hash = hash_api_key(api_key).
     - In get_review_status() and get_review_results(): if record is retrieved from DB and has an api_key_hash, verify that caller's hash matches record.api_key_hash (or scopes contain "admin"), preventing unauthorized cross-tenant retrieval of source code. Also check reviews_store cache for matching caller if stored.

3. cerberus/models/database.py:
   - Add api_key_hash = Column(String(128), nullable=True, index=True) to CodeReviewRecord.

4. Verification:
   - Execute `python -m pytest` to verify all 301 existing tests pass with zero regressions.
   - Author unit/integration tests to verify agent crash scoring degradation, cache poisoning prevention, WebSocket authentication and cleanup, and review history isolation.
   - Keep progress.md updated in your working directory.
   - Write full handoff report to e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m3\handoff.md.
   - Notify orchestrator upon completion.
