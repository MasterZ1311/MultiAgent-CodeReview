# E2E Test Infra: Cerberus / CodeVault Defect Remediation

## Test Philosophy
- Opaque-box, requirement-driven testing based on ORIGINAL_REQUEST.md.
- Methodology: 4-Tier verification framework (Feature Coverage, Boundary/Corner Cases, Cross-Feature Combinations, Real-World Application Scenarios).
- Zero reliance on internal mock shortcuts for core behaviors; end-to-end endpoint and component verification.

## Feature Inventory & Test Mapping
| # | Feature | Source (Requirement) | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Cross-Feature) | Tier 4 (Scenario) |
|---|---------|----------------------|:-----------------:|:-----------------:|:----------------------:|:-----------------:|
| 1 | Cryptographic API Key Verification | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 2 | CORS Origin Restrictions | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 3 | Production Secret Key Enforcement | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 4 | Bounded In-Memory Cache with LRU | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 5 | Bounded Rate Limiter Storage | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 6 | HTTP Client Session Pooling | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 7 | Bounded Batch Review Concurrency | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 8 | Agent Crash Degradation & Score 0.0 | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 9 | WebSocket Authentication & Cleanup | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ | ✓ |
| 10 | Review History Data Security | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ | ✓ |

## Test Architecture
- Test Runner: `python -m pytest` with pytest-asyncio
- Existing test baseline: 23 passed tests in `tests/`
- Test Locations:
  - `tests/test_security_remediation.py`: Negative auth tests, bad tokens, fake `cvai_` prefixes, inactive/expired keys, CORS origins, production secret validation.
  - `tests/test_memory_remediation.py`: Cache max item capacity, LRU eviction order, rate limiter key pruning, 20k random token memory bounds, provider HTTP client session pooling, batch review semaphore throttling.
  - `tests/test_orchestrator_remediation.py`: Agent crash handling (score 0.0, status degraded/failed, non-poisoned cache), review history security.
  - `tests/test_websocket_remediation.py`: WebSocket token authentication, disconnect cleanup, exception cleanup, dead socket pruning.
- Verification Commands:
  - Full suite: `python -m pytest -v` (Must pass 100% with 0 failures)

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Expected Outcome |
|---|----------|--------------------|------------------|
| S1 | Multi-Tenant Review Pipeline | F1, F5, F8, F10 | Tenant A and B use distinct keys; Tenant A cannot access Tenant B review history; all reviews authenticated |
| S2 | High-Load Batch CI/CD Webhook | F4, F5, F7, F8 | 50-file batch submitted concurrently; semaphore limits concurrency; memory cache and rate limiter stay strictly bounded |
| S3 | Faulty Agent Under CI/CD Gate | F8, F4, F1 | Security agent encounters unparseable syntax/crash; review marked degraded with 0.0 score; CI/CD blocks; corrupt score not cached |
| S4 | Hostile Frontend CORS & Token Flood | F1, F2, F5 | Attacker domain blocked by CORS; thousands of fake `cvai_` tokens rejected at 401; rate limiter memory pruned without leak |
| S5 | Live WebSocket Dashboard Stream | F9, F1, F8 | Dashboard connects with token; receives progress/completion events; disconnects cleanly; no leaked socket references |

## Coverage Thresholds
- All 23 original tests MUST pass without regression.
- Every inventoried feature must have ≥5 Tier 1 and Tier 2 test assertions.
- 0 failures, 0 errors across entire suite.
