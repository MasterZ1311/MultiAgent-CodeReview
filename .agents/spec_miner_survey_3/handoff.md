# Specification Mining Report & Handoff

**Author**: `spec_miner_survey_3` (teamwork_preview_spec_miner)  
**Target Milestone / Requirements**: Requirement R3 (Orchestrator Reliability & WebSocket Safety) & Requirement R4 (Test Suite Baseline & Testing Gaps)  
**Date**: 2026-09-22  
**Working Directory**: `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\spec_miner_survey_3`  

---

## 1. Observation

### 1.1 Orchestrator Calculation & Crash Scoring Flaw
- **File**: `cerberus/agents/orchestrator.py`
- **Lines 101–123**:
  ```python
  async def run_agent(agent_name: str) -> AgentResult:
      agent = self.registry[agent_name]
      a_start = time.perf_counter()
      try:
          res = await agent.analyze(
              code=request.code,
              language=request.language or "python",
              context=request.context.model_dump() if request.context else None,
          )
          AGENT_EXECUTION_SECONDS.labels(agent_name=agent_name).observe(time.perf_counter() - a_start)
          for f in res.findings:
              FINDINGS_DETECTED_TOTAL.labels(agent_name=agent_name, severity=f.severity.value).inc()
          return res
      except Exception as e:
          logger.error(f"Agent '{agent_name}' failed during review: {e}")
          return AgentResult(
              name=agent_name,
              status="failed",
              score=100.0,
              execution_time_ms=int((time.perf_counter() - a_start) * 1000),
              error=str(e),
          )
  ```
- **Lines 129–156**:
  ```python
  scores: Dict[str, float] = {}
  for res in agent_results:
      scores[res.name] = res.score
      all_findings.extend(res.findings)
      agents_payload.append(res.model_dump())

  # Calculate weighted overall score
  weights = {
      "security": 0.40,
      "performance": 0.25,
      "quality": 0.25,
      "architecture": 0.05,
      "compliance": 0.05,
  }
  total_weight = sum(weights.get(name, 0.2) for name in scores)
  if total_weight > 0:
      overall_score = sum(scores[name] * weights.get(name, 0.2) for name in scores) / total_weight
  else:
      overall_score = 100.0
  overall_score = round(max(0.0, min(100.0, overall_score)), 1)
  ```
- **Lines 188–193 & Line 212**:
  ```python
  response = CodeReviewResponse(
      review_id=review_id,
      status="completed",
      ...
  )
  await cache_manager.set(cache_key, response.model_dump())
  ```
- **Empirical Execution Probe 1 (Security Agent Crash)**:
  - Command:
    ```bash
    python -c "import asyncio; from unittest.mock import AsyncMock; from cerberus.agents.orchestrator import ReviewOrchestrator; from cerberus.models.schemas import CodeReviewRequest; o = ReviewOrchestrator(); o.registry['security'].analyze = AsyncMock(side_effect=RuntimeError('LLM engine segfault')); res = asyncio.run(o.execute_review(CodeReviewRequest(code='x = 1', language='python', agents=['security', 'performance', 'quality']))); print('STATUS:', res.status, 'SCORE:', res.overall_score, 'SECURITY_AGENT_RESULT:', [a for a in res.results['agents'] if a['name'] == 'security'])"
    ```
  - Verbatim Output:
    ```
    2026-09-22 11:17:50,333 [ERROR] [cerberus.orchestrator]: Agent 'security' failed during review: LLM engine segfault
    STATUS: completed SCORE: 100.0 SECURITY_AGENT_RESULT: [{'name': 'security', 'status': 'failed', 'score': 100.0, 'execution_time_ms': 1, 'findings': [], 'error': 'LLM engine segfault'}]
    ```
- **Empirical Execution Probe 2 (All Agents Crash)**:
  - Command:
    ```bash
    python -c "import asyncio; from unittest.mock import AsyncMock; from cerberus.agents.orchestrator import ReviewOrchestrator; from cerberus.models.schemas import CodeReviewRequest; o = ReviewOrchestrator(); o.registry['security'].analyze = AsyncMock(side_effect=RuntimeError('Crash 1')); o.registry['performance'].analyze = AsyncMock(side_effect=RuntimeError('Crash 2')); o.registry['quality'].analyze = AsyncMock(side_effect=RuntimeError('Crash 3')); res = asyncio.run(o.execute_review(CodeReviewRequest(code='x = 1', language='python', agents=['security', 'performance', 'quality']))); print('ALL_FAIL_STATUS:', res.status, 'ALL_FAIL_SCORE:', res.overall_score)"
    ```
  - Verbatim Output:
    ```
    2026-09-22 11:18:06,844 [ERROR] [cerberus.orchestrator]: Agent 'security' failed during review: Crash 1
    2026-09-22 11:18:06,844 [ERROR] [cerberus.orchestrator]: Agent 'performance' failed during review: Crash 2
    2026-09-22 11:18:06,845 [ERROR] [cerberus.orchestrator]: Agent 'quality' failed during review: Crash 3
    ALL_FAIL_STATUS: completed ALL_FAIL_SCORE: 100.0
    ```

### 1.2 WebSocket Endpoint Safety & Connection Lifecycle
- **File**: `cerberus/api/v1/review.py`
- **Lines 28–30 & Lines 139–160**:
  ```python
  reviews_store: Dict[str, CodeReviewResponse] = {}
  ws_connections: Dict[str, List[WebSocket]] = {}

  @router.websocket("/{review_id}/ws")
  async def websocket_review_stream(websocket: WebSocket, review_id: str):
      """Live WebSocket stream broadcasting agent lifecycle events and progress."""
      await websocket.accept()
      if review_id not in ws_connections:
          ws_connections[review_id] = []
      ws_connections[review_id].append(websocket)

      try:
          await websocket.send_text(json.dumps({
              "event": "connected",
              "review_id": review_id,
              "message": "Subscribed to live agent updates."
          }))
          while True:
              # Keep connection alive
              await websocket.receive_text()
      except WebSocketDisconnect:
          if review_id in ws_connections and websocket in ws_connections[review_id]:
              ws_connections[review_id].remove(websocket)
  ```
- **Lines 50–60**:
  ```python
  if response.review_id in ws_connections:
      for ws in ws_connections[response.review_id]:
          try:
              await ws.send_text(json.dumps({
                  "event": "review_completed",
                  "review_id": response.review_id,
                  "overall_score": response.overall_score
              }))
          except Exception:
              pass
  ```
- **Empirical Execution Probe 3 (WebSocket Auth & Disconnect Probe)**:
  - Command:
    ```bash
    python -c "from fastapi.testclient import TestClient; from cerberus.api.app import app; from cerberus.api.v1.review import ws_connections; client = TestClient(app); print('Initial ws_connections:', ws_connections); ws = client.websocket_connect('/api/v1/review/test_rev_123/ws'); msg = ws.receive_json(); print('Received msg:', msg); print('ws_connections after connect:', list(ws_connections.keys()), len(ws_connections['test_rev_123'])); ws.close(); print('After exit ws_connections:', ws_connections)"
    ```
  - Verbatim Output:
    ```
    Initial ws_connections: {}
    Received msg: {'event': 'connected', 'review_id': 'test_rev_123', 'message': 'Subscribed to live agent updates.'}
    ws_connections after connect: ['test_rev_123'] 1
    After exit ws_connections: {'test_rev_123': []}
    ```

### 1.3 Stored Review History & Source Code Security
- **File**: `cerberus/models/database.py` (lines 28–46):
  ```python
  class CodeReviewRecord(Base):
      __tablename__ = "code_reviews"

      id = Column(String(64), primary_key=True, default=generate_uuid)
      github_pr_url = Column(String(500), nullable=True)
      github_repo_owner = Column(String(255), nullable=True)
      github_repo_name = Column(String(255), nullable=True)
      commit_hash = Column(String(64), nullable=True)
      code_snippet = Column(Text, nullable=False)
      language = Column(String(50), default="python")
      status = Column(String(20), default="processing")
      overall_score = Column(Float, nullable=True)
      processing_time_ms = Column(Integer, nullable=True)
      results_json = Column(JSON, nullable=True)
      created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
      completed_at = Column(DateTime, nullable=True)
  ```
- **File**: `cerberus/api/v1/review.py` (lines 64–83):
  ```python
  @router.get("/{review_id}", response_model=CodeReviewResponse)
  async def get_review_status(
      review_id: str,
      api_key: str = Depends(verify_api_key)
  ):
      """Get the current processing status and summary of a review."""
      if review_id in reviews_store:
          return reviews_store[review_id]

      # Check database
      try:
          async with AsyncSessionLocal() as session:
              record = await session.get(CodeReviewRecord, review_id)
              if record and record.results_json:
                  return CodeReviewResponse(**record.results_json)
      except Exception as e:
          logger.warning(f"DB lookup failed for {review_id}: {e}")

      raise HTTPException(status_code=404, detail=f"Review with ID '{review_id}' was not found.")
  ```

### 1.4 Existing Test Suite Baseline Execution
- **Command**: `python -m pytest -v` executed in `e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview`
- **Verbatim Pytest Output**:
  ```
  ============================= test session starts =============================
  platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Python313\python.exe
  cachedir: .pytest_cache
  rootdir: E:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview
  configfile: pyproject.toml
  plugins: anyio-4.12.1, langsmith-0.11.1, asyncio-1.4.0
  asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
  collecting ... collected 23 items

  tests/test_agents.py::test_security_agent_detects_sqli_and_secrets PASSED [  4%]
  tests/test_agents.py::test_security_agent_clean_code PASSED              [  8%]
  tests/test_agents.py::test_performance_agent_detects_quadratic_complexity PASSED [ 13%]
  tests/test_agents.py::test_quality_agent_detects_bare_except_and_missing_docs PASSED [ 17%]
  tests/test_agents.py::test_compliance_agent_detects_sensitive_logging PASSED [ 21%]
  tests/test_api.py::test_health_endpoint PASSED                           [ 26%]
  tests/test_api.py::test_list_agents_endpoint PASSED                      [ 30%]
  tests/test_api.py::test_submit_review_endpoint PASSED                    [ 34%]
  tests/test_cache.py::test_cache_hashing_and_lifecycle PASSED             [ 39%]
  tests/test_cli.py::test_cli_health PASSED                                [ 43%]
  tests/test_cli.py::test_cli_list_agents PASSED                           [ 47%]
  tests/test_cli.py::test_cli_create_api_key PASSED                        [ 52%]
  tests/test_cli.py::test_cli_review_snippet PASSED                        [ 56%]
  tests/test_compliance_agent.py::test_luhn_algorithm_validation PASSED    [ 60%]
  tests/test_compliance_agent.py::test_hipaa_phi_and_cleartext_http PASSED [ 65%]
  tests/test_compliance_agent.py::test_gdpr_data_minimization_and_url_pii PASSED [ 69%]
  tests/test_compliance_agent.py::test_soc2_credentials_and_logging PASSED [ 73%]
  tests/test_compliance_agent.py::test_pcidss_pan_and_cvv_storage PASSED   [ 78%]
  tests/test_compliance_agent.py::test_ccpa_opt_out_enforcement PASSED     [ 82%]
  tests/test_compliance_agent.py::test_clean_code_full_compliance PASSED   [ 86%]
  tests/test_compliance_agent.py::test_orchestrator_integration_with_compliance PASSED [ 91%]
  tests/test_orchestrator.py::test_orchestrator_parallel_execution PASSED  [ 95%]
  tests/test_orchestrator.py::test_orchestrator_blocking_mode PASSED       [100%]

  ======================= 23 passed, 2 warnings in 8.27s ========================
  ```

---

## 2. Logic Chain

### 2.1 The Agent Crash 100.0 Score Inflation Mechanism
1. **Observation Ref 1.1**: Line 116 in `cerberus/agents/orchestrator.py` catches `Exception as e` during agent execution and returns `AgentResult(name=agent_name, status="failed", score=100.0, error=str(e))`.
2. **Observation Ref 1.1**: In lines 129–134, `scores[res.name] = res.score` extracts `res.score` (which is `100.0`) without inspecting `res.status`.
3. **Observation Ref 1.1**: In lines 143–155, the weighted score is computed via `overall_score = sum(scores[name] * weights[name]) / total_weight`. Because `scores[res.name] == 100.0`, the crashed agent's score is counted as 100% perfect.
   - Example with `security` (weight 0.40): If `security` crashes, it contributes `100.0 * 0.40 = 40.0` points out of 40 available. If all agents crash, `overall_score` is `100.0`.
4. **Observation Ref 1.1**: Because `res.findings` is `[]`, no findings are appended to `critical_issues` or `warnings`.
5. **Observation Ref 1.1**: In lines 174–177, `should_block` checks `summary["critical"] > 0 or summary["high"] > 0`. Because findings are empty, `should_block` evaluates to `False`.
6. **Observation Ref 1.1**: Line 190 unconditionally hardcodes `status="completed"` in `CodeReviewResponse`. It never marks the review as `"degraded"` or `"failed"`.
7. **Observation Ref 1.1**: Line 212 calls `await cache_manager.set(cache_key, response.model_dump())`, caching the corrupted review (score 100.0, status "completed", 0 findings) for 7 days.
8. **Conclusion**: An agent crash (such as an unhandled AST syntax or LLM timeout) causes severe silent failure: the system masks the crash, assigns 100.0, ignores any actual vulnerabilities in the code, bypasses blocking CI/CD gates, reports "completed", and poisons the cache.

### 2.2 WebSocket Endpoint Vulnerabilities
1. **Observation Ref 1.2**: In line 140 of `cerberus/api/v1/review.py`, `websocket_review_stream` accepts `(websocket: WebSocket, review_id: str)`. There is no `api_key: str = Depends(...)`, no query parameter `token: str`, and no token authentication check prior to `await websocket.accept()`.
2. **Observation Ref 1.2**: Any client can initiate a WebSocket handshake without credentials and receive live updates and review scores for any `review_id`.
3. **Observation Ref 1.2**: Line 156 only catches `WebSocketDisconnect`. If an exception occurs (e.g., `ConnectionResetError`, `RuntimeError`, `asyncio.CancelledError`, network drop), execution bypasses the cleanup handler, leaving the disconnected `WebSocket` object in `ws_connections[review_id]`.
4. **Observation Ref 1.2**: Line 58 in `submit_review` catches `Exception` during `ws.send_text()` and executes `pass` without removing the dead socket.
5. **Observation Ref 1.2**: In Probe 3, when a socket disconnects cleanly, `ws_connections[review_id].remove(websocket)` leaves `ws_connections = {'test_rev_123': []}`. The dictionary key is never deleted, leading to continuous memory leaks across review IDs.

### 2.3 Stored Review History & Code Confidentiality Flaws
1. **Observation Ref 1.3**: `CodeReviewRecord` in `cerberus/models/database.py` stores `code_snippet` in plaintext `Text` and `results_json` in plaintext `JSON`.
2. **Observation Ref 1.3**: `CodeReviewRecord` has no `user_id`, `tenant_id`, or `api_key_id` column.
3. **Observation Ref 1.3**: `GET /api/v1/review/{review_id}` in `cerberus/api/v1/review.py` verifies only that the caller has a valid API key (or uses dev bypass), but performs zero ownership verification before returning the full review data and code snippet.
4. **Conclusion**: Any authenticated caller can access any other caller's proprietary source code snippets and vulnerability findings by guessing or knowing the `review_id` (Insecure Direct Object Reference / IDOR).

### 2.4 Existing Test Baseline & Defect Coverage
1. **Observation Ref 1.4**: Exactly 23 tests exist in `tests/`, and all 23 pass.
2. **Observation Ref 1.4**: None of the existing 23 tests cover:
   - Orchestrator behavior when an agent crashes.
   - WebSocket endpoint connectivity, authentication, or cleanup.
   - Unauthorized review history retrieval across tenants.
   - Negative authentication tests (invalid tokens, fake `cvai_` tokens, production mode enforcement).
   - Cache bounds, LRU eviction, or rate limiter memory bounding.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Orchestrator | Multi-Agent Parallel Execution | Dispatches parallel analysis to Security, Performance, Quality, Architecture, and Compliance agents | `CodeReviewRequest` (code, language, agents) | `CodeReviewResponse` with aggregated findings & scores | Catches agent crashes, returns `status='failed'`, but incorrectly sets `score=100.0` | `cerberus/agents/orchestrator.py:101-125` |
| 2 | Orchestrator | Failure Handling & Crash Scoring | Handles exceptions raised by agents during `agent.analyze()` | Agent exception | `AgentResult(status='failed', score=100.0, error=...)` | Masking bug: awards 100.0 instead of 0.0 or marking review degraded | `cerberus/agents/orchestrator.py:114-122` |
| 3 | Orchestrator | Weighted Score Aggregation | Computes normalized weighted average: Security (0.40), Performance (0.25), Quality (0.25), Architecture (0.05), Compliance (0.05) | `scores: Dict[str, float]` | `overall_score: float` rounded to 1 decimal place | Defaults to 100.0 if total weight is 0 | `cerberus/agents/orchestrator.py:143-156` |
| 4 | Orchestrator | Blocking Mode Evaluation | Checks whether review findings exceed critical or high thresholds | `config.blocking_mode`, `all_findings` | `should_block: bool`, `block_reason: str` | Bypassed when agents crash because findings list is empty | `cerberus/agents/orchestrator.py:167-178` |
| 5 | Orchestrator | Two-Tier Caching Integration | Checks Redis/memory cache via SHA-256 fingerprint before running agents, stores result after execution | `request.code`, `language`, `active_agents` | Cached `CodeReviewResponse` | Caches false 100.0 scores when agents crash | `cerberus/agents/orchestrator.py:79-96, 212` |
| 6 | WebSocket | Live Review Stream | WebSocket endpoint broadcasting live review events to subscribers | `review_id: str` path parameter | JSON event stream (`connected`, `review_completed`) | Completely unauthenticated; leaks empty list keys upon disconnect | `cerberus/api/v1/review.py:139-160` |
| 7 | WebSocket | Broadcast Notification | Broadcasts `review_completed` event to all open websockets for a review | `review_id`, `response` | Outgoing WebSocket message frame | Catches `Exception` and calls `pass`; fails to prune dead socket objects | `cerberus/api/v1/review.py:50-60` |
| 8 | Review History | In-Memory Review Storage | Stores completed reviews in memory dictionary for rapid status lookup | `response.review_id`, `response` | Stored `CodeReviewResponse` | Unbounded dictionary (`reviews_store`); causes process memory leak | `cerberus/api/v1/review.py:28, 44, 104` |
| 9 | Review History | Database Review Persistence | Asynchronously persists review records and findings in SQLite/PostgreSQL | `request`, `response` | Database records in `code_reviews` and `review_findings` | Stores code in cleartext; lacks user/tenant ownership fields | `cerberus/api/v1/review.py:161-196` |
| 10 | Review History | Review Status & Results Retrieval | Endpoints `GET /api/v1/review/{review_id}` and `/{review_id}/results` | `review_id`, `api_key` | `CodeReviewResponse` | IDOR vulnerability: allows any authenticated caller to read any review's code | `cerberus/api/v1/review.py:64-92` |
| 11 | Review API | Batch Code Review | Concurrently executes reviews for multiple files via `asyncio.gather` | `BatchReviewRequest` (list of `CodeReviewRequest`) | `BatchReviewResponse` (list of `CodeReviewResponse`) | Unbounded concurrency: executes all files simultaneously without semaphore | `cerberus/api/v1/review.py:94-111` |
| 12 | Review API | Developer Feedback Submission | Persists user feedback and ratings for completed reviews | `review_id`, `FeedbackRequest` | `FeedbackResponse` | Sets `user_id = api_key` in `review_feedback` table | `cerberus/api/v1/review.py:113-137` |
| 13 | Security | API Key Verification | Dependency verifying Bearer token in `Authorization` header | `request: Request`, `authorization: Header` | Validated token string | Accepts any string starting with `cvai_` without checking database | `cerberus/api/dependencies.py:11-65` |
| 14 | Security | Sliding-Window Rate Limiter | In-memory sliding-window limiter enforcing per-hour limits | `identifier: str` | `(allowed, remaining, retry_after)` | Unbounded memory growth: dictionary never purges inactive identifiers | `cerberus/core/security.py:30-60` |
| 15 | Test Suite | Pytest Baseline Suite | Pytest test suite containing 23 unit and integration tests | Test commands | 23 passed tests | Missing negative tests, agent crash tests, and WebSocket tests | `tests/` directory |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Orchestrator Failure Handling | `SecurityAgent.analyze` raises `RuntimeError("LLM engine segfault")` | Returns `status="completed"`, `overall_score=100.0`. The crashed agent is assigned `score=100.0` and `findings=[]`. Blocking threshold is not triggered. |
| 2 | Orchestrator Failure Handling | All 3 requested agents raise `RuntimeError` | Returns `status="completed"`, `overall_score=100.0`. Zero findings are reported. Complete masking of catastrophic system failure. |
| 3 | Orchestrator Caching | Review request where an agent crashes | Orchestrator saves the 100.0 score result to Redis/memory cache (`cache_manager.set`). Subsequent calls immediately return 100.0 from cache without running agents. |
| 4 | WebSocket Authentication | Client connects to `/api/v1/review/{review_id}/ws` without `Authorization` header or query token | Connection accepted unconditionally (`await websocket.accept()`), returns `{"event": "connected"}`. Unauthenticated access permitted. |
| 5 | WebSocket Disconnection Cleanup | Client connects to WebSocket and closes connection cleanly | Socket removed from `ws_connections[review_id]`, but dictionary retains `{review_id: []}`. Empty list keys leak permanently in memory. |
| 6 | WebSocket Exception Cleanup | Client connection drops or raises `ConnectionResetError` during receive/send | Exception bypasses `except WebSocketDisconnect`. Dead `WebSocket` object is never removed from `ws_connections[review_id]`. |
| 7 | WebSocket Broadcast on Dead Socket | Review finishes and attempts to broadcast to a dead/disconnected socket in `ws_connections` | `ws.send_text()` raises exception, caught by `except Exception: pass`. Socket remains in `ws_connections` forever. |
| 8 | Review History Authorization | User with API Key B queries `GET /api/v1/review/{review_id}` where review was submitted by User A | Endpoint returns full review data including User A's `code_snippet` and findings. Zero tenant isolation or authorization check. |
| 9 | In-Memory Review Storage Bound | Client submits 10,000 code reviews over time | `reviews_store` in `cerberus/api/v1/review.py` retains all 10,000 `CodeReviewResponse` objects indefinitely in memory without eviction or size limit. |
| 10 | Batch Review Concurrency | Client submits a batch request with 500 files | `asyncio.gather(*[orchestrator.execute_review(req) for req in request.files])` spawns 500 concurrent review tasks simultaneously, exhausting system CPU/memory. |

---

## 5. Existing Test Suite Baseline & Testing Gaps Analysis

### 5.1 Existing 23 Tests Inventory
All 23 existing tests pass with 0 failures under `python -m pytest`:

| File | Test Name | Target Tested |
|------|-----------|---------------|
| `tests/test_agents.py` | `test_security_agent_detects_sqli_and_secrets` | SecurityAgent finds SQLi (CWE-89) & hardcoded secrets |
| `tests/test_agents.py` | `test_security_agent_clean_code` | SecurityAgent gives clean code 100.0 score |
| `tests/test_agents.py` | `test_performance_agent_detects_quadratic_complexity` | PerformanceAgent detects O(N^2) loops |
| `tests/test_agents.py` | `test_quality_agent_detects_bare_except_and_missing_docs` | QualityAgent detects bare except |
| `tests/test_agents.py` | `test_compliance_agent_detects_sensitive_logging` | ComplianceAgent detects password logging |
| `tests/test_api.py` | `test_health_endpoint` | `GET /api/v1/health` returns healthy status |
| `tests/test_api.py` | `test_list_agents_endpoint` | `GET /api/v1/agents` returns active agents list |
| `tests/test_api.py` | `test_submit_review_endpoint` | `POST /api/v1/review` submits code & retrieves it |
| `tests/test_cache.py` | `test_cache_hashing_and_lifecycle` | Cache SHA-256 fingerprinting, get, set, and miss |
| `tests/test_cli.py` | `test_cli_health` | CLI `health` command |
| `tests/test_cli.py` | `test_cli_list_agents` | CLI `list-agents` command |
| `tests/test_cli.py` | `test_cli_create_api_key` | CLI `create-api-key` command |
| `tests/test_cli.py` | `test_cli_review_snippet` | CLI `review` command |
| `tests/test_compliance_agent.py` | `test_luhn_algorithm_validation` | Luhn checksum algorithm & PAN masking |
| `tests/test_compliance_agent.py` | `test_hipaa_phi_and_cleartext_http` | HIPAA ePHI cleartext transmission detection |
| `tests/test_compliance_agent.py` | `test_gdpr_data_minimization_and_url_pii` | GDPR data minimization and URL PII detection |
| `tests/test_compliance_agent.py` | `test_soc2_credentials_and_logging` | SOC 2 credentials & logging detection |
| `tests/test_compliance_agent.py` | `test_pcidss_pan_and_cvv_storage` | PCI-DSS PAN & CVV storage detection |
| `tests/test_compliance_agent.py` | `test_ccpa_opt_out_enforcement` | CCPA opt-out / do not sell enforcement |
| `tests/test_compliance_agent.py` | `test_clean_code_full_compliance` | ComplianceAgent passes clean code |
| `tests/test_compliance_agent.py` | `test_orchestrator_integration_with_compliance` | Orchestrator runs compliance agent |
| `tests/test_orchestrator.py` | `test_orchestrator_parallel_execution` | Orchestrator runs security, performance, quality |
| `tests/test_orchestrator.py` | `test_orchestrator_blocking_mode` | Orchestrator blocks when threshold exceeded |

### 5.2 Testing Gaps Mapped by Requirement

#### Requirement R1: Authentication & Security Hardening
1. **Negative API Key Validation**: No tests verify that tokens prefixed with `cvai_` but not registered in the database (e.g. `cvai_fake_123`) are rejected with HTTP 401.
2. **Database Key Hash Validation**: No tests verify that API keys are validated against the database table `api_keys` using `hash_api_key`.
3. **Key Expiration & Deactivation**: No tests verify rejection of expired or deactivated (`is_active=False`) API keys.
4. **Production Mode Enforcement**: No tests verify that when `settings.ENVIRONMENT == "production"`, unauthenticated requests are rejected (no dev anonymous fallback).
5. **CORS Configuration Validation**: No tests verify that CORS middleware rejects or disallows wildcard `*` origins when `allow_credentials=True`.
6. **Insecure Default Secret Key**: No tests verify that the application rejects running in production mode if `settings.SECRET_KEY` remains the default development secret.

#### Requirement R2: Memory Safety & Resource Management
1. **Cache Maximum Capacity**: No tests verify that `CacheManager` enforces a maximum entry limit (e.g., bounded LRU).
2. **Cache Eviction**: No tests verify that the oldest or least recently used entries are evicted when cache capacity is reached.
3. **Rate Limiter Expiration Purge**: No tests verify that stale request timestamps and inactive identifiers are pruned to prevent memory bloat.
4. **Rate Limiter Identifier Bounding**: No tests verify memory stability under a flood of requests with randomly generated IP addresses or identifiers.
5. **HTTP Client Session Pooling**: No tests verify that external LLM providers (`OpenAIProvider`, `WatsonxProvider`) maintain and reuse persistent HTTP client sessions instead of opening new clients per request.
6. **Batch Review Concurrency Bounds**: No tests verify that `/api/v1/review/batch` restricts concurrency (e.g. via `asyncio.Semaphore`) to avoid resource exhaustion under large file batches.

#### Requirement R3: Orchestrator Reliability & WebSocket Safety
1. **Orchestrator Agent Crash Degradation**: No tests verify that an individual agent crash marks `CodeReviewResponse.status` as `"degraded"` and assigns a failing score (`0.0`) to that agent.
2. **Score Non-Inflation on Crash**: No tests verify that overall review scores are appropriately dragged down when an agent crashes rather than scoring 100.0.
3. **Catastrophic Crash Handling**: No tests verify that when all agents crash, review status is marked `"failed"` and overall score is `0.0`.
4. **Cache Poisoning Prevention on Crash**: No tests verify that failed or degraded reviews are not cached as clean 100.0 reviews.
5. **WebSocket Authentication Enforcement**: No tests verify that connecting to `/api/v1/review/{review_id}/ws` without a valid token is rejected with HTTP 401 or WebSocket policy violation (code 1008).
6. **WebSocket Connection Cleanup**: No tests verify that disconnected sockets are pruned from `ws_connections`, empty review ID keys are removed from `ws_connections`, and dead sockets are cleaned up on exception.
7. **Review History Tenant Isolation**: No tests verify that `GET /api/v1/review/{review_id}` rejects cross-tenant retrieval of stored review history and code snippets.

---

## 6. Caveats
- **Read-Only Scope**: In accordance with the dispatch instructions, no code or test modifications were applied during this survey.
- **Provider API Keys**: LLM provider tests (`OpenAIProvider`, `WatsonxProvider`) were not executed against live remote APIs as credentials were not configured; heuristic fallbacks were active.
- **Database Engine**: Development database runs on SQLite (`sqlite+aiosqlite:///./cerberus.db`). Production deployments using PostgreSQL may require identical schema migration when adding `user_id` / ownership columns.

---

## 7. Conclusion
1. **Orchestrator Reliability (R3)**: The review orchestrator suffers from a critical defect where agent crashes are caught and explicitly assigned `score=100.0` with `status="completed"`. This inflates overall scores, bypasses blocking CI/CD thresholds, and poisons the cache. To fix this, crashed agents must be assigned `score=0.0`, the response status must be marked as `"degraded"` (or `"failed"` if all agents crash), and degraded results must not poison the cache.
2. **WebSocket Safety (R3)**: The WebSocket stream endpoint `/{review_id}/ws` is completely unauthenticated and leaks connection state: it only handles `WebSocketDisconnect` (ignoring general exceptions), retains empty review ID keys in `ws_connections` forever, and swallows broadcast failures without removing dead sockets.
3. **Review History Security (R3)**: Code snippets and review results are stored in cleartext in database records (`code_reviews`) and in-memory dictionaries (`reviews_store`) with zero tenant/user ownership binding, enabling trivial cross-tenant IDOR access.
4. **Test Suite Baseline & Testing Gaps (R4)**: The existing test suite has 23 tests that all pass, but completely lacks negative tests, crash tests, concurrency tests, memory bounding tests, and WebSocket tests across R1–R4.

---

## 8. Verification Method
To independently verify the observations and findings in this report:

1. **Verify Baseline Test Suite**:
   ```bash
   cd "e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview"
   python -m pytest -v
   ```
   *Expected outcome*: 23 passed, 2 warnings in ~8s.

2. **Verify Orchestrator Crash 100.0 Inflation Bug**:
   ```bash
   python -c "import asyncio; from unittest.mock import AsyncMock; from cerberus.agents.orchestrator import ReviewOrchestrator; from cerberus.models.schemas import CodeReviewRequest; o = ReviewOrchestrator(); o.registry['security'].analyze = AsyncMock(side_effect=RuntimeError('LLM engine segfault')); res = asyncio.run(o.execute_review(CodeReviewRequest(code='x = 1', language='python', agents=['security', 'performance', 'quality']))); print('STATUS:', res.status, 'SCORE:', res.overall_score)"
   ```
   *Expected outcome*: `STATUS: completed SCORE: 100.0`.

3. **Verify WebSocket Unauthenticated Access & Memory Key Leak**:
   ```bash
   python -c "from fastapi.testclient import TestClient; from cerberus.api.app import app; from cerberus.api.v1.review import ws_connections; client = TestClient(app); ws = client.websocket_connect('/api/v1/review/test_rev_123/ws'); msg = ws.receive_json(); print('Connected without auth:', msg); ws.close(); print('Leaked keys in ws_connections:', ws_connections)"
   ```
   *Expected outcome*: Successfully connects without auth, and prints `Leaked keys in ws_connections: {'test_rev_123': []}`.
