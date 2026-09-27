# Milestone 1 Handoff Report: Authentication & Security Hardening

## 1. Observation

### 1.1 Baseline Observations
- Baseline pytest run: 23 tests collected in `tests/test_agents.py`, `tests/test_api.py`, `tests/test_cache.py`, `tests/test_cli.py`, `tests/test_compliance_agent.py`, `tests/test_orchestrator.py`. All 23 tests passed in 6.46 seconds.
- The `api_keys` table existed in `cerberus.db` with schema columns `id`, `key_hash`, `name`, `prefix`, `scopes`, `is_active`, `created_at`, `expires_at`, but contained 0 rows.
- Prior code in `cerberus/api/dependencies.py` allowed any token starting with `cvai_` (`not token.startswith(settings.API_KEY_PREFIX)`) without checking cryptographic signatures or database records, and allowed anonymous requests in development mode.
- Prior code in `cerberus/api/app.py` configured CORS with `allow_origins=["*"]` combined with `allow_credentials=True`.
- Prior code in `cerberus/config.py` lacked CORS origin settings and lacked validation rejecting default/insecure secrets when running under production environment.
- Prior code in `cerberus/cli/main.py` generated API keys via `generate_api_key()` but did not insert records into the `api_keys` table.

### 1.2 Implemented Changes & Observations
1. **`cerberus/config.py`**:
   - Added `INSECURE_DEFAULT_SECRETS` set containing known weak and default keys.
   - Added `CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000"`.
   - Added interface contract settings: `CACHE_MAX_ITEMS: int = 1000`, `RATE_LIMIT_MAX_TRACKED: int = 10000`, `MAX_CONCURRENT_BATCH_REVIEWS: int = 5`, `MAX_BATCH_SIZE: int = 100`.
   - Added `cors_origins_list` property returning `[o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]`.
   - Added Pydantic validator `@model_validator(mode="after") def validate_production_security(self)` that raises `ValueError` if `ENVIRONMENT.lower() in ("production", "prod")` and `SECRET_KEY in INSECURE_DEFAULT_SECRETS` or `len(SECRET_KEY) < 32`.
   - Tested: `Settings(ENVIRONMENT="production")` raised `ValueError: Production configuration error: Insecure default SECRET_KEY is not permitted in production.`
   - Tested: `Settings(ENVIRONMENT="production", SECRET_KEY="too_short")` raised `ValueError: Production configuration error: SECRET_KEY must be at least 32 characters long in production.`
   - Tested: `Settings(ENVIRONMENT="production", SECRET_KEY="a"*32)` initialized successfully.

2. **`cerberus/api/app.py`**:
   - Imported `settings` from `cerberus.config`.
   - Replaced wildcard origin in `CORSMiddleware` with `settings.cors_origins_list`.
   - Added explicit safeguard: if `"*"` is present in allowed origins, `allow_credentials` is set to `False`.
   - Tested: Whitelisted origin `http://localhost:3000` returned `access-control-allow-origin: http://localhost:3000` and `access-control-allow-credentials: true`.
   - Tested: Untrusted origin `http://untrusted-attacker.com` did not receive origin reflection or credential permissions.

3. **`cerberus/core/database.py`**:
   - In `init_db()`, added automatic development credential seeding: when `settings.ENVIRONMENT == "development"`, queries `ApiKeyRecord` for `hash_api_key(settings.DEFAULT_DEV_API_KEY)`; if absent, inserts an active `ApiKeyRecord` with scopes `"review:read,review:write,admin"`.
   - Verified in SQLite: `api_keys` table was successfully seeded with key hash `4e304d6d4ca360ebeaccd2bc9665a8e323ba1a333eb4db5a90d3d731606f30b6`, name `"Default Development Key"`, and `is_active=1`.

4. **`cerberus/api/dependencies.py`**:
   - Rewrote `verify_api_key`:
     - Requires non-empty `Authorization` header, raising HTTP 401 with `{"error": "missing_authentication"}` if omitted.
     - Requires strict `Bearer <token>` format, raising HTTP 401 with `{"error": "invalid_token_format"}` if malformed.
     - Computes SHA-256 hash using `hash_api_key(token)`.
     - Queries `ApiKeyRecord` from database via `AsyncSessionLocal`.
     - Rejects inactive keys (`is_active=False`) with HTTP 401.
     - Rejects expired keys (`expires_at < utcnow`) with HTTP 401.
     - For tokens not found in DB: in development mode, permits fallback for `settings.DEFAULT_DEV_API_KEY` (ensuring compatibility across test executions where lifespan isn't triggered), but strictly rejects any unregistered or fabricated tokens (including arbitrary `cvai_` tokens) with HTTP 401.
     - Validates rate limits via `rate_limiter.is_allowed(token)`.
   - Verified:
     - Missing auth: 401 Unauthorized (`missing_authentication`).
     - Malformed auth (`Token foo`): 401 Unauthorized (`invalid_token_format`).
     - Fabricated `cvai_` token (`cvai_malicious_attacker_999`): 401 Unauthorized (`invalid_api_key`).
     - Inactive token in DB: 401 Unauthorized (`invalid_api_key`).
     - Expired token in DB: 401 Unauthorized (`invalid_api_key`).
     - Valid seeded dev key: 200 OK.
     - Valid newly created active key: 200 OK.

5. **`cerberus/cli/main.py`**:
   - In `create_api_key`, implemented database persistence: executes `init_db()` and adds `ApiKeyRecord(key_hash=key_hash, name=name, prefix=prefix, scopes="review:read,review:write", is_active=True)` within `AsyncSessionLocal`.
   - Verified end-to-end: running `create_api_key --name cli-integration-test` generated a key, inserted it into SQLite `api_keys`, and an immediate authenticated request to `/api/v1/agents` using `Bearer <generated_key>` returned HTTP 200 OK.

### 1.3 Final Verification Run
- Command: `python -m pytest`
- Output: `23 passed, 2 warnings in 7.06s`
- Zero test failures, zero regressions.

---

## 2. Logic Chain

1. **Authentication Hardening**:
   - *Premise*: Prior system accepted any token starting with `cvai_` without database or cryptographic verification.
   - *Inference*: Any user could forge credentials (`Bearer cvai_anything`) and gain authenticated access.
   - *Action taken*: Integrated `hash_api_key(token)` with an asynchronous query against `ApiKeyRecord`. Replaced arbitrary prefix acceptance with active status and expiration timestamp validation against genuine database records.
   - *Result*: Tokens starting with `cvai_` that do not correspond to an active, unexpired record in `api_keys` (or the dev key in dev mode) are rejected with HTTP 401.

2. **CORS Hardening**:
   - *Premise*: `CORSMiddleware` with `allow_origins=["*"]` and `allow_credentials=True` permits dynamic origin reflection, allowing any arbitrary website visited by an authenticated user to perform credentialed cross-origin requests.
   - *Inference*: Restricting allowed origins to configured hosts in `settings.CORS_ORIGINS` and explicitly prohibiting `allow_credentials=True` when origins contain `*` closes this cross-origin vector.
   - *Action taken*: Configured `CORSMiddleware` to use `settings.cors_origins_list` and set `allow_credentials = False` if `"*"` is included.
   - *Result*: Only whitelisted origins receive CORS headers with credentials.

3. **Production Configuration Protection**:
   - *Premise*: If default secrets from source code are used in production, attackers can forge or crack tokens using known secrets.
   - *Inference*: Rejecting startup when `ENVIRONMENT` is production and `SECRET_KEY` is weak or default prevents insecure production deployments.
   - *Action taken*: Added a Pydantic `@model_validator(mode="after")` to `Settings` that enforces non-default secrets and minimum 32-character length in production environments.
   - *Result*: Production runs fail fast with clear configuration errors if default secrets remain unchanged.

4. **CLI Key Lifecycle Integration**:
   - *Premise*: `create-api-key` printed a generated key but never stored it, rendering CLI-generated keys non-functional in authenticated API requests.
   - *Inference*: Persisting the generated key hash and metadata to `ApiKeyRecord` closes the loop between key generation and API authentication.
   - *Action taken*: Added asynchronous database persistence to `create_api_key`.
   - *Result*: Keys generated via CLI are immediately usable for authentication against the API.

---

## 3. Caveats

- **Test Environment ASGI Lifespan**: `httpx.ASGITransport(app=app)` used by integration tests in `tests/test_api.py` does not execute FastAPI's ASGI lifespan handler, meaning `init_db()` is not called automatically upon test client startup. To ensure zero test regressions while maintaining strict security, `verify_api_key` includes a fallback check allowing `settings.DEFAULT_DEV_API_KEY` specifically when `settings.ENVIRONMENT == "development"`. In production mode, this fallback is disabled.
- **WebSocket Authentication**: The WebSocket review streaming endpoint (`/{review_id}/ws`) is part of Milestone 3 and does not currently use HTTP `verify_api_key`. That endpoint will be secured in Milestone 3 as specified in `PROJECT.md`.
- **Rate Limiter Storage**: Milestone 2 will address bounding rate limiter memory capacity (`RATE_LIMIT_MAX_TRACKED`). Milestone 1 ensures that only authenticated requests reach the rate limiter, mitigating random token pollution.

---

## 4. Conclusion

Milestone 1: Authentication & Security Hardening has been completely implemented and verified. All requirements have been satisfied with genuine logic:
1. `cerberus/config.py`: CORS configuration, origin list parser, interface contract settings, and production secret validator added.
2. `cerberus/api/app.py`: CORS middleware configured with explicit origins; wildcard origins prohibited with credentials.
3. `cerberus/core/database.py`: Development key seeded into `ApiKeyRecord` in `init_db()`.
4. `cerberus/api/dependencies.py`: Cryptographic token verification against `ApiKeyRecord` with active and expiration checks; prefix bypass eliminated; anonymous dev bypass eliminated; dev fallback maintained for `DEFAULT_DEV_API_KEY`.
5. `cerberus/cli/main.py`: Created API keys are persisted as active `ApiKeyRecord` entries in the database.
6. Verification: All 23 existing pytest tests pass with zero regressions. All negative auth tests, CORS checks, production configuration validations, and end-to-end CLI key authentication checks passed.

---

## 5. Verification Method

To independently reproduce and verify this work:

### 5.1 Run Full Test Suite
```powershell
python -m pytest
```
*Expected result*: 23 passed in ~7s, 0 failures.

### 5.2 Negative Authentication & Cryptographic Verification Check
```powershell
python -c "
import asyncio
from datetime import datetime, timedelta, timezone
from httpx import ASGITransport, AsyncClient
from cerberus.api.app import app
from cerberus.core.database import AsyncSessionLocal, init_db
from cerberus.core.security import generate_api_key
from cerberus.models.database import ApiKeyRecord

async def run_checks():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # 1. Missing Auth -> 401
        res = await client.get('/api/v1/agents')
        assert res.status_code == 401
        # 2. Malformed Auth -> 401
        res = await client.get('/api/v1/agents', headers={'Authorization': 'Token foo'})
        assert res.status_code == 401
        # 3. Arbitrary cvai_ prefix token -> 401
        res = await client.get('/api/v1/agents', headers={'Authorization': 'Bearer cvai_attacker_fake_token'})
        assert res.status_code == 401
        # 4. Inactive key -> 401
        raw_key, key_hash, prefix = generate_api_key('inactive-test')
        async with AsyncSessionLocal() as session:
            session.add(ApiKeyRecord(key_hash=key_hash, name='inactive-test', prefix=prefix, is_active=False))
            await session.commit()
        res = await client.get('/api/v1/agents', headers={'Authorization': f'Bearer {raw_key}'})
        assert res.status_code == 401
        # 5. Expired key -> 401
        raw_key_exp, key_hash_exp, prefix_exp = generate_api_key('expired-test')
        async with AsyncSessionLocal() as session:
            session.add(ApiKeyRecord(key_hash=key_hash_exp, name='expired-test', prefix=prefix_exp, is_active=True, expires_at=datetime.now(timezone.utc) - timedelta(days=1)))
            await session.commit()
        res = await client.get('/api/v1/agents', headers={'Authorization': f'Bearer {raw_key_exp}'})
        assert res.status_code == 401
        # 6. Valid seeded dev key -> 200
        res = await client.get('/api/v1/agents', headers={'Authorization': 'Bearer cvai_dev_key_123'})
        assert res.status_code == 200
        print('All negative authentication and token lifecycle checks PASSED.')

asyncio.run(run_checks())
"
```

### 5.3 CORS Verification Check
```powershell
python -c "
import asyncio
from httpx import ASGITransport, AsyncClient
from cerberus.api.app import app

async def check_cors():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Whitelisted origin
        res = await client.get('/api/v1/health', headers={'Origin': 'http://localhost:3000'})
        assert res.headers.get('access-control-allow-origin') == 'http://localhost:3000'
        assert res.headers.get('access-control-allow-credentials') == 'true'
        # Untrusted origin
        res_evil = await client.get('/api/v1/health', headers={'Origin': 'http://evil-attacker.com'})
        assert res_evil.headers.get('access-control-allow-origin') != 'http://evil-attacker.com'
        print('CORS checks PASSED.')

asyncio.run(check_cors())
"
```

### 5.4 Production Secret Configuration Validation Check
```powershell
python -c "
from cerberus.config import Settings
# Default secret in prod -> raises ValueError
try:
    Settings(ENVIRONMENT='production')
    assert False, 'Should have failed with default secret in production'
except ValueError:
    pass

# Short secret in prod -> raises ValueError
try:
    Settings(ENVIRONMENT='production', SECRET_KEY='too_short')
    assert False, 'Should have failed with short secret in production'
except ValueError:
    pass

# Valid secret in prod -> succeeds
s = Settings(ENVIRONMENT='production', SECRET_KEY='x'*32)
assert s.SECRET_KEY == 'x'*32
print('Production security validation checks PASSED.')
"
```

### 5.5 End-to-End CLI Key Generation & API Authentication Check
```powershell
python -c "
import asyncio, re
from typer.testing import CliRunner
from httpx import ASGITransport, AsyncClient
from cerberus.cli.main import app as cli_app
from cerberus.api.app import app as fastapi_app

runner = CliRunner()
res = runner.invoke(cli_app, ['create-api-key', '--name', 'verify-test'])
assert res.exit_code == 0
match = re.search(r'(cvai_[0-9a-fA-F]+)', res.stdout)
assert match
key = match.group(1)

async def test():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url='http://test') as client:
        r = await client.get('/api/v1/agents', headers={'Authorization': f'Bearer {key}'})
        assert r.status_code == 200
        print('E2E CLI key creation and API authentication PASSED.')

asyncio.run(test())
"
```

### 5.6 Invalidation Conditions
- Any change allowing an unregistered token like `Bearer cvai_random` to access protected endpoints invalidates the authentication fix.
- Any CORS response allowing `*` origins alongside `Access-Control-Allow-Credentials: true` invalidates the CORS fix.
- Instantiating `Settings(ENVIRONMENT="production")` with a default or short `SECRET_KEY` without raising `ValueError` invalidates the configuration fix.
- Creating a key via `cerberus create-api-key` that does not create an active record in the database invalidates the CLI persistence fix.
