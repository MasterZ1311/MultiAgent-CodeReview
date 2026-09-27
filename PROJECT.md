# Project: Cerberus / CodeVault Defect Remediation & Verification

## Architecture
Cerberus is a multi-agent automated code review platform built with FastAPI, SQLAlchemy (async SQLite/PostgreSQL), and specialized static/heuristic/LLM evaluation agents.
The system consists of:
1. **API Layer (`cerberus/api/`)**: FastAPI application, CORS middleware, authentication dependencies (`verify_api_key`), routing endpoints (`/review`, `/agents`, `/config`, `/analytics`, `/health`), and WebSocket streaming.
2. **Core Security & Infrastructure (`cerberus/core/`)**: Configuration management (`Settings`), cryptographic helpers (`generate_api_key`, `hash_api_key`), sliding-window `RateLimiter`, and two-tier `CacheManager` (Redis + In-Memory).
3. **Multi-Agent Orchestrator (`cerberus/agents/orchestrator.py`)**: Coordinates parallel agent execution (`SecurityAgent`, `PerformanceAgent`, `QualityAgent`, `ArchitectureAgent`, `ComplianceAgent`), weights scores, detects critical issues, evaluates blocking thresholds, and persists review history.
4. **LLM Providers (`cerberus/providers/`)**: Interfaces with external LLM engines (Ollama, OpenAI, WatsonX) or heuristic fallbacks.
5. **Data Layer (`cerberus/models/database.py`, `cerberus/core/database.py`)**: Async SQLAlchemy ORM models (`CodeReviewRecord`, `ReviewFindingRecord`, `ApiKeyRecord`, `ReviewFeedbackRecord`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Cryptographic API Key Verification | Reject arbitrary, fabricated, or unregistered tokens (including `cvai_` prefix) by validating `token_hash` against active `ApiKeyRecord` in database | M1 | ORIGINAL_REQUEST R1 / Survey 1 |
| 2 | Development Mode Credential Seeding | Ensure default development key is seeded in DB during `init_db()` in development mode, preventing auth failure in local dev | M1 | Survey 1 |
| 3 | CORS Origin Restrictions | Reject wildcard `*` origins when `allow_credentials=True`; enforce explicit origin list via `settings.CORS_ORIGINS` | M1 | ORIGINAL_REQUEST R1 / Survey 1 |
| 4 | Production Secret Key Validation | Reject insecure fallback or default `SECRET_KEY` in production mode via Pydantic model validator (enforcing >= 32 chars and non-default) | M1 | ORIGINAL_REQUEST R1 / Survey 1 |
| 5 | CLI Key Generation Persistence | Persist newly generated API keys to database `api_keys` table in `cerberus create-api-key` CLI command | M1 | Survey 1 |
| 6 | Bounded In-Memory Cache with LRU | Replace unbounded `_memory_cache` dict with `OrderedDict` bounded by `settings.CACHE_MAX_ITEMS` and evict oldest entries on insert | M2 | ORIGINAL_REQUEST R2 / Survey 2 |
| 7 | Bounded In-Memory Review Store | Replace unbounded `reviews_store` dict in `review.py` with bounded structure and database fallback | M2 | Survey 2 |
| 8 | Bounded Rate Limiter Storage | Prune inactive identifiers from `RateLimiter.requests`, delete empty lists, and cap tracking capacity to `RATE_LIMIT_MAX_TRACKED` | M2 | ORIGINAL_REQUEST R2 / Survey 2 |
| 9 | HTTP Client Session Pooling | Maintain persistent `httpx.AsyncClient` instances in LLM providers (`OllamaProvider`, `OpenAIProvider`, `WatsonxProvider`) with connection pooling and lifecycle closure | M2 | ORIGINAL_REQUEST R2 / Survey 2 |
| 10 | Bounded Batch Review Concurrency | Throttle concurrent file processing in `POST /api/v1/review/batch` using `asyncio.Semaphore` and validate maximum batch size | M2 | ORIGINAL_REQUEST R2 / Survey 2 |
| 11 | Agent Crash Degradation & Failing Score | Assign failing score (0.0) to crashed agents, set overall review status to `"degraded"` (or `"failed"` if all crash), and prevent cache poisoning | M3 | ORIGINAL_REQUEST R3 / Survey 3 |
| 12 | WebSocket Stream Authentication | Enforce authentication on `/{review_id}/ws` before accepting connection | M3 | ORIGINAL_REQUEST R3 / Survey 3 |
| 13 | WebSocket Connection Cleanup | Safely remove disconnected sockets, purge empty review ID entries from `ws_connections`, and clean up on exception | M3 | ORIGINAL_REQUEST R3 / Survey 3 |
| 14 | Stored Review History Confidentiality | Protect stored source code snippets against unauthorized cross-tenant retrieval | M3 | ORIGINAL_REQUEST R3 / Survey 3 |
| 15 | Negative & Boundary Auth Tests | Test missing auth, malformed bearer, fake `cvai_` tokens, expired keys, CORS rejection, and production secret validation | M4 | ORIGINAL_REQUEST R4 / Survey 3 |
| 16 | Memory & Resource Management Tests | Test cache capacity eviction (LRU), rate limiter random token bounding, provider session reuse, and batch review concurrency throttle | M4 | ORIGINAL_REQUEST R4 / Survey 3 |
| 17 | Orchestration & WebSocket Tests | Test agent crash scoring (0.0), review status degradation, cache poisoning prevention, WebSocket auth rejection, and socket cleanup | M4 | ORIGINAL_REQUEST R4 / Survey 3 |
| 18 | Full Regression Verification | Verify all existing 23 tests plus all newly added tests pass with 0 failures under `python -m pytest` | M4 | ORIGINAL_REQUEST R4 / Survey 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Authentication & Security Hardening | `cerberus/config.py`, `cerberus/api/app.py`, `cerberus/api/dependencies.py`, `cerberus/cli/main.py`, `cerberus/core/database.py` | none | DONE |
| M2 | Memory Safety & Resource Management | `cerberus/core/cache.py`, `cerberus/core/security.py`, `cerberus/providers/*.py`, `cerberus/api/v1/review.py` | M1 | DONE |
| M3 | Orchestrator Reliability & WebSocket Safety | `cerberus/agents/orchestrator.py`, `cerberus/api/v1/review.py`, `cerberus/models/database.py` | M1, M2 | DONE |
| M4 | Comprehensive Verification & Regression Suite | `tests/`, `TEST_INFRA.md`, E2E test execution | M1, M2, M3 | DONE |

## Interface Contracts

### 1. `cerberus/config.py` Settings
- `CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000"`
- `cors_origins_list: List[str]` (property)
- `CACHE_MAX_ITEMS: int = 1000`
- `RATE_LIMIT_MAX_TRACKED: int = 10000`
- `MAX_CONCURRENT_BATCH_REVIEWS: int = 5`
- `MAX_BATCH_SIZE: int = 100`
- `@model_validator(mode="after") def validate_production_security(self) -> Settings` raises `ValueError` if `ENVIRONMENT in ("production", "prod")` and `SECRET_KEY in INSECURE_DEFAULT_SECRETS` or `len(SECRET_KEY) < 32`.

### 2. `cerberus/api/dependencies.py` Authentication
- `verify_api_key(request: Request, authorization: Optional[str] = Header(None)) -> str`
  - Validates `Authorization: Bearer <token>`
  - Hashes token using `hash_api_key(token)`
  - Looks up `ApiKeyRecord` with `key_hash`, `is_active=True`, and non-expired `expires_at`
  - Rejects missing/malformed header with HTTP 401
  - Rejects unregistered `cvai_` token with HTTP 401
  - Rejects inactive or expired token with HTTP 401
  - Calls `rate_limiter.is_allowed(token)` and raises HTTP 429 if rate limited

### 3. `cerberus/core/cache.py` CacheManager
- `self._memory_cache: OrderedDict[str, Dict[str, Any]]`
- `max_items: int = settings.CACHE_MAX_ITEMS`
- `set(key, value, ttl)`: evicts oldest key via `popitem(last=False)` when `len >= max_items`
- `get(key)`: on hit, calls `move_to_end(key)` and deletes if expired; on miss returns `None`
- `clear()`: clears cache

### 4. `cerberus/core/security.py` RateLimiter
- `self.requests: Dict[str, List[float]]`
- `max_tracked: int = settings.RATE_LIMIT_MAX_TRACKED`
- `is_allowed(identifier: str) -> Tuple[bool, int, int]`:
  - Prunes expired timestamps; if empty list remains, removes `identifier` key from `self.requests`
  - If `len(self.requests) >= max_tracked` and `identifier` is new: purges expired keys across all identifiers, and if still at capacity, evicts oldest entry.

### 5. `cerberus/providers/base.py` & LLM Providers
- `BaseLLMProvider` exposes persistent `self._client: Optional[httpx.AsyncClient]`
- `async def get_client(self) -> httpx.AsyncClient` creates pooled client with `httpx.Limits(max_keepalive_connections=20, max_connections=100)` if not created
- `async def close(self) -> None` closes persistent client

### 6. `cerberus/agents/orchestrator.py`
- On agent exception in `run_agent(agent_name)`:
  - Return `AgentResult(name=agent_name, status="failed", score=0.0, error=str(e), findings=[])`
- In `execute_review`:
  - If any agent failed, set `status = "degraded"` (unless all failed, then `status = "failed"`)
  - Overall score calculation: failed agents contribute 0.0 to weighted average
  - Never cache review results if `status in ("degraded", "failed")`

### 7. `cerberus/api/v1/review.py`
- `/{review_id}/ws`:
  - Enforce token authentication via query param `token: Optional[str] = Query(None)` or header before `await websocket.accept()`. If invalid, close with code 1008 (Policy Violation) or 401.
  - On disconnect or exception, remove socket from `ws_connections[review_id]`. If `ws_connections[review_id]` is empty, delete the key `del ws_connections[review_id]`.
- `/batch`:
  - Semaphore throttle: `sem = asyncio.Semaphore(settings.MAX_CONCURRENT_BATCH_REVIEWS)`
  - Enforce `len(request.files) <= settings.MAX_BATCH_SIZE`
  - Wrap review execution in semaphore: `async with sem: return await orchestrator.execute_review(req)`
- `reviews_store`:
  - Bounded to e.g. 500 entries via `OrderedDict`, evicting oldest.

## Code Layout
- `cerberus/config.py`: Application settings and environment validation
- `cerberus/api/app.py`: FastAPI application entry point, CORS middleware, lifespan
- `cerberus/api/dependencies.py`: Authentication and request verification dependencies
- `cerberus/api/v1/review.py`: Review endpoints (single, batch, status, WebSocket stream)
- `cerberus/core/cache.py`: CacheManager implementation
- `cerberus/core/security.py`: RateLimiter, API key generation and hashing
- `cerberus/core/database.py`: SQLAlchemy database engine, session factory, and `init_db()`
- `cerberus/models/database.py`: SQLAlchemy ORM models (`ApiKeyRecord`, `CodeReviewRecord`, etc.)
- `cerberus/models/schemas.py`: Pydantic request/response schemas
- `cerberus/providers/`: LLM provider client implementations (Ollama, OpenAI, WatsonX, Base)
- `cerberus/agents/orchestrator.py`: Multi-agent review orchestrator
- `cerberus/cli/main.py`: Command-line interface
- `tests/`: Automated test suite
