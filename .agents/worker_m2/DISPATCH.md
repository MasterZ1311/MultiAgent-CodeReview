## 2026-09-22T06:38:25Z

You are the implementation worker for Milestone 2: Memory Safety & Resource Management.
Your archetype is teamwork_preview_worker.
Your working directory is e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m2.

You MUST read ORIGINAL_REQUEST.md at:
e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\ORIGINAL_REQUEST.md

You MUST also read:
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\PROJECT.md
- e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\explorer_survey_2\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

File Ownership (you have exclusive write ownership for Milestone 2):
- cerberus/core/cache.py
- cerberus/core/security.py
- cerberus/providers/base.py
- cerberus/providers/ollama_provider.py
- cerberus/providers/openai_provider.py
- cerberus/providers/watsonx_provider.py
- cerberus/api/v1/review.py

Implementation Tasks:
1. cerberus/core/cache.py:
   - Replace unbounded self._memory_cache dict with collections.OrderedDict.
   - Use settings.CACHE_MAX_ITEMS (default 1000).
   - In set(key, value, ttl_seconds): if len(self._memory_cache) >= self.max_items and key not in self._memory_cache, evict the oldest entry: self._memory_cache.popitem(last=False).
   - In get(key): if key in self._memory_cache, check expiration. If valid, call self._memory_cache.move_to_end(key) for LRU ordering and return data. If expired, del self._memory_cache[key] and return None.
   - Add prune_expired() method and clear() method.

2. cerberus/core/security.py:
   - Update RateLimiter:
     - Enforce bounded memory. Read settings.RATE_LIMIT_MAX_TRACKED (default 10000).
     - When pruning expired timestamps: if len(self.requests[identifier]) == 0, delete the key: del self.requests[identifier].
     - If len(self.requests) >= self.max_tracked and identifier not in self.requests:
       - Run a sweep: purge all identifiers that have no timestamps or whose timestamps are all older than one_hour_ago.
       - If still at or above capacity, evict the oldest tracking key.
     - Add purge_expired() method.

3. cerberus/providers/ (base.py, ollama_provider.py, openai_provider.py, watsonx_provider.py):
   - In BaseLLMProvider (base.py):
     - Add persistent self._client: Optional[httpx.AsyncClient] = None.
     - Add async def get_client(self) -> httpx.AsyncClient: lazily instantiate persistent client with httpx.Limits(max_keepalive_connections=20, max_connections=100) and keep it stored in self._client.
     - Add async def close(self) -> None: if self._client and not self._client.is_closed, await self._client.aclose().
   - In ollama_provider.py, openai_provider.py, watsonx_provider.py:
     - Reuse await self.get_client() across calls instead of `async with httpx.AsyncClient(...)` per request.
     - Pass specific timeout to the client method (e.g. client.get(..., timeout=1.0) or client.post(..., timeout=30.0)).
     - Ensure close() closes self._client.

4. cerberus/api/v1/review.py:
   - Replace unbounded reviews_store dict with a bounded OrderedDict (e.g. max 500 or settings.CACHE_MAX_ITEMS entries, evicting oldest on insert).
   - In get_review_status() and get_review_results(): if review_id not in reviews_store, fall back to checking the database (CodeReviewRecord), so evicted entries can still be retrieved if saved in DB.
   - In batch_review():
     - Enforce maximum batch size limit: if len(request.files) > settings.MAX_BATCH_SIZE (default 100), raise HTTPException(status_code=400, detail=f"Batch size {len(request.files)} exceeds maximum allowed of {settings.MAX_BATCH_SIZE}").
     - Bound concurrency using asyncio.Semaphore(settings.MAX_CONCURRENT_BATCH_REVIEWS). Wrap orchestrator.execute_review in semaphore:
       async def _throttled_review(req):
           async with semaphore:
               return await orchestrator.execute_review(req)
       results = await asyncio.gather(*[_throttled_review(req) for req in request.files])

5. Verification:
   - Execute `python -m pytest` to verify all 251 existing tests pass with 0 failures and 0 regressions.
   - Keep progress.md updated in your working directory.
   - Write full handoff report to e:\My Development\IBM Agentic AI - PT1\MultiAgentCodeReview\.agents\worker_m2\handoff.md detailing files modified, diff summary, and verification results.
   - Notify orchestrator upon completion.
