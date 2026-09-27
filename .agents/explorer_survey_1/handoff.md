# Requirement R1 Survey Report: Authentication & Security Hardening

## 1. Observation

### 1.1 API Key Verification & Credential Storage
- **Location 1**: `cerberus/api/dependencies.py`, lines 11–64.
  ```python
  11: async def verify_api_key(
  12:     request: Request,
  13:     authorization: Optional[str] = Header(None)
  14: ) -> str:
  ...
  21:     # In local development mode, permit unauthenticated or default key requests
  22:     if settings.ENVIRONMENT == "development" and not authorization:
  23:         # Check rate limit on IP
  24:         allowed, remaining, retry_after = rate_limiter.is_allowed(client_ip)
  ...
  31:         return "cvai_dev_anonymous"
  ...
  48:     # Validate token prefix or dev key
  49:     if token != settings.DEFAULT_DEV_API_KEY and not token.startswith(settings.API_KEY_PREFIX):
  50:         raise HTTPException(
  51:             status_code=status.HTTP_401_UNAUTHORIZED,
  52:             detail={"error": "invalid_api_key", "message": "API key is invalid or has expired"}
  53:         )
  ```
  - **Direct Finding**: Line 49 accepts **any** token as long as `token.startswith(settings.API_KEY_PREFIX)` is true (where `settings.API_KEY_PREFIX == "cvai_"` from `cerberus/config.py:26`). No cryptographic signature or hash is checked, and no database query is performed.
  - **Direct Finding**: In development mode (line 22), any request without an `Authorization` header bypasses authentication completely, returning `"cvai_dev_anonymous"`.
  - **Endpoints Affected**: Every endpoint relying on `verify_api_key`:
    - `cerberus/api/v1/review.py`: lines 35, 67, 88, 97, 117 (`POST /api/v1/review`, `GET /api/v1/review/{id}`, `GET /api/v1/review/{id}/findings`, `POST /api/v1/review/{id}/feedback`, `POST /api/v1/review/batch`)
    - `cerberus/api/v1/agents.py`: line 15 (`GET /api/v1/agents`)
    - `cerberus/api/v1/config.py`: lines 21, 38 (`GET /api/v1/config`, `PUT /api/v1/config`)
    - `cerberus/api/v1/analytics.py`: line 18 (`GET /api/v1/analytics/summary`)

- **Location 2**: `cerberus/models/database.py`, lines 89–100.
  ```python
  89: class ApiKeyRecord(Base):
  90:     __tablename__ = "api_keys"
  91: 
  92:     id = Column(String(64), primary_key=True, default=generate_uuid)
  93:     key_hash = Column(String(128), unique=True, index=True, nullable=False)
  94:     name = Column(String(255), nullable=False)
  95:     prefix = Column(String(16), nullable=False)
  96:     scopes = Column(String(255), default="review:read,review:write")
  97:     is_active = Column(Boolean, default=True)
  98:     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  99:     expires_at = Column(DateTime, nullable=True)
  ```
  - **Direct Finding**: The database schema explicitly defines `ApiKeyRecord` with fields for `key_hash`, `prefix`, `scopes`, `is_active`, and `expires_at`. However, a project-wide search (`grep_search ApiKeyRecord`) revealed that `ApiKeyRecord` is never referenced or queried anywhere outside its declaration.
  - **Database Verification**: A direct SQLite query against `cerberus.db` confirmed that the table `api_keys` exists but contains 0 rows (`[]`).

- **Location 3**: `cerberus/core/security.py`, lines 13–27.
  ```python
  13: def generate_api_key(name: str = "default") -> Tuple[str, str, str]:
  18:     token = secrets.token_hex(24)
  19:     prefix = settings.API_KEY_PREFIX
  20:     raw_key = f"{prefix}{token}"
  21:     key_hash = hash_api_key(raw_key)
  22:     return raw_key, key_hash, prefix
  ...
  25: def hash_api_key(key: str) -> str:
  26:     """Computes SHA-256 hash of API key for safe database storage."""
  27:     return hashlib.sha256(f"{settings.SECRET_KEY}:{key}".encode("utf-8")).hexdigest()
  ```
  - **Direct Finding**: The cryptographic hashing function `hash_api_key` is fully implemented using SHA-256 with `settings.SECRET_KEY` as a salt, but it is never called during request authentication in `verify_api_key`.

- **Location 4**: `cerberus/cli/main.py`, lines 113–127.
  ```python
  113: @app.command()
  114: def create_api_key(
  115:     name: str = typer.Option("default", "--name", "-n", help="Name or label for the API key")
  116: ):
  117:     """Generate a cryptographically secure cerberus API key."""
  118:     raw_key, key_hash, prefix = generate_api_key(name=name)
  119:     console.print(Panel(...))
  ```
  - **Direct Finding**: CLI command `create-api-key` generates a key and hash, but does not persist the key to the database.

---

### 1.2 CORS Middleware Misconfiguration
- **Location**: `cerberus/api/app.py`, lines 37–45.
  ```python
  37:     # CORS Configuration
  38:     app.add_middleware(
  39:         CORSMiddleware,
  40:         allow_origins=["*"],
  41:         allow_credentials=True,
  42:         allow_methods=["*"],
  43:         allow_headers=["*"],
  44:     )
  ```
  - **Direct Finding**: `allow_origins=["*"]` is combined with `allow_credentials=True`.
  - **Compliance Agent Contrast**: In `cerberus/agents/compliance/soc2_evaluator.py`, lines 33–35 and 110–120:
    ```python
    33:     # 4. Insecure Permissive CORS / Debug Mode (CC6.6)
    34:     WILDCARD_CORS_PATTERN = re.compile(r"""allow_origins\s*=\\s*\[\s*["']\*["']\s*\]""")
    ...
    115:         title="SOC 2 CC6.6: Permissive Wildcard CORS Origin ('*')",
    116:         message="Cross-Origin Resource Sharing (CORS) configured with wildcard allow_origins=['*'].",
    119:         explanation="Wildcard CORS permits arbitrary untrusted web domains to make credentialed cross-origin requests to internal endpoints."
    ```
    Cerberus's own compliance analyzer flags this exact pattern as a SOC 2 CC6.6 violation.
  - **Documentation Reference**: `docs/04-installation-setup.md`, line 305 specifies:
    `CORS_ORIGINS=http://localhost:3000,http://localhost:8000`. However, `cerberus/config.py` does not define `CORS_ORIGINS`.

---

### 1.3 Configuration Management & Insecure Default Secrets
- **Location**: `cerberus/config.py`, lines 24–29.
  ```python
  24:     # Security Settings
  25:     SECRET_KEY: str = "cerberus_dev_secret_key_change_in_production_32chars"
  26:     API_KEY_PREFIX: str = "cvai_"
  27:     RATE_LIMIT_PER_HOUR: int = 100
  28:     DEFAULT_DEV_API_KEY: str = "cvai_dev_key_123"
  ```
  - **Direct Finding**: `SECRET_KEY` defaults to `"cerberus_dev_secret_key_change_in_production_32chars"`.
  - **Direct Finding**: `Settings` lacks any validation checking whether `ENVIRONMENT == "production"` while `SECRET_KEY` remains the default fallback or is insecure (< 32 characters or matching known weak keys).
  - **Direct Finding**: When running in production, `DEFAULT_DEV_API_KEY` (`"cvai_dev_key_123"`) is neither invalidated nor disabled.
  - **Docker Compose Fallback**: In `docker-compose.yml`, line 23:
    `SECRET_KEY=${SECRET_KEY:-cerberus_production_secret_key_change_me_now_1234}`
    and in `docs/examples/docker-compose.yml`, line 38:
    `SECRET_KEY=${SECRET_KEY:-change_me_in_production}`.

---

## 2. Logic Chain

### 2.1 API Key Verification Authentication Bypass
1. In `cerberus/api/dependencies.py:49`:
   `if token != settings.DEFAULT_DEV_API_KEY and not token.startswith(settings.API_KEY_PREFIX):`
2. If an attacker submits any token starting with `cvai_` (e.g. `Bearer cvai_malicious_attacker_999`), `token.startswith(settings.API_KEY_PREFIX)` evaluates to `True`.
3. Consequently, `not token.startswith(...)` evaluates to `False`, the `if` condition evaluates to `False`, and execution falls through past line 53 without raising an HTTP 401 error.
4. Because lines 22–31 return `"cvai_dev_anonymous"` if `settings.ENVIRONMENT == "development"` and no `Authorization` header is passed, completely unauthenticated callers are granted access.
5. The `ApiKeyRecord` model in `cerberus/models/database.py` and `hash_api_key()` in `cerberus/core/security.py` were designed for cryptographic hash lookups, but were never integrated into `verify_api_key`.
6. Therefore, the authentication check is merely a string-prefix test, constituting a critical authentication bypass vulnerability (CWE-287 / CWE-306).

### 2.2 Wildcard CORS with Credentials Risk
1. In `cerberus/api/app.py:40-41`, `CORSMiddleware` has `allow_origins=["*"]` and `allow_credentials=True`.
2. Under the W3C / WHATWG Fetch specification, browsers reject CORS responses where `Access-Control-Allow-Origin: *` and `Access-Control-Allow-Credentials: true`.
3. To work around browser restrictions, Starlette's `CORSMiddleware` dynamically echoes back the request's `Origin` header as `Access-Control-Allow-Origin: <requesting_origin>` whenever `allow_origins=["*"]` and `allow_credentials=True`.
4. This dynamic reflection permits **any third-party website** visited by an authenticated developer or admin to execute authenticated HTTP requests against the Cerberus API.
5. Malicious web pages can exfiltrate proprietary source code submitted for review, read vulnerability reports, alter system configuration via `PUT /api/v1/config`, or abuse review quotas.

### 2.3 Production Configuration Vulnerability
1. `cerberus/config.py:25` hardcodes `SECRET_KEY = "cerberus_dev_secret_key_change_in_production_32chars"`.
2. `hash_api_key` in `cerberus/core/security.py:27` uses `settings.SECRET_KEY` to compute `hashlib.sha256(f"{settings.SECRET_KEY}:{key}".encode("utf-8")).hexdigest()`.
3. If Cerberus runs in production with default secrets, an attacker possessing the publicly known `SECRET_KEY` can perform offline precomputed dictionary/rainbow table attacks against leaked database hashes.
4. Furthermore, lack of production validation allows `DEFAULT_DEV_API_KEY` (`"cvai_dev_key_123"`) to remain active in production, providing an unauthorized backdoor.

---

## 3. Caveats

1. **Test Environment ASGI Lifespan Quirk**:
   - `httpx.ASGITransport(app=app)` used in `tests/test_api.py` does **NOT** trigger FastAPI's ASGI `lifespan` handler.
   - Verified experimentally: running an endpoint via `ASGITransport` does not execute `init_db()` defined in `app.py:20`.
   - If database seeding of dev credentials occurs *only* in `lifespan`, running `pytest tests/test_api.py` without an explicit DB initialization fixture would fail if `verify_api_key` requires database records.
   - Remediation must either ensure tables and dev seeds exist lazily/on startup, or use a pytest fixture (e.g. in `tests/conftest.py`) that calls `await init_db()`.
2. **WebSocket Authentication Boundary (Requirement R3 Dependency)**:
   - WebSocket streaming in `cerberus/api/v1/review.py:139` does not use `verify_api_key` (FastAPI HTTP `Header` dependencies cannot parse headers on standard WebSocket upgrade handshakes in some clients). While R1 covers API keys and CORS, WebSocket authentication is specified under R3 and should use a query parameter `token` or WebSocket connection headers validated against `hash_api_key`.
3. **Database Concurrency & Async Engine**:
   - `cerberus/core/database.py` uses SQLite with `aiosqlite` in dev and PostgreSQL in production. SQLite requires `check_same_thread: False`, which is currently handled. When querying `ApiKeyRecord` in `verify_api_key`, using `async with AsyncSessionLocal() as session:` must be handled without leaving dangling open sessions.
4. **Rate Limiter Storage (Requirement R2 Dependency)**:
   - `verify_api_key` passes `token` to `rate_limiter.is_allowed(token)`. R2 addresses bounding rate limiter memory; R1 must ensure only valid tokens reach the rate limiter so random tokens cannot pollute memory.

---

## 4. Conclusion & Proposed Remediation Strategies

### Summary Matrix

| Defect | File & Lines | Root Cause | Proposed Fix Strategy | Regression Risk |
|---|---|---|---|---|
| **Arbitrary Prefix Auth Bypass** | `cerberus/api/dependencies.py:48-53` | Prefix-only check `not token.startswith("cvai_")` | Hash token via `hash_api_key()` and query active, unexpired record from `api_keys` table | `tests/test_api.py` uses `cvai_dev_key_123`; dev key must be seeded in DB in dev mode |
| **Anonymous Dev Mode Bypass** | `cerberus/api/dependencies.py:21-31` | Omitting auth header returns `cvai_dev_anonymous` | Require `Authorization` header on all protected endpoints | None; existing tests all pass auth headers |
| **Missing CLI Key Persistence** | `cerberus/cli/main.py:118-126` | Generated key never saved to DB | Use `AsyncSessionLocal` to insert `ApiKeyRecord` | CLI tests in `test_cli.py` pass; new keys will actually work in API |
| **Wildcard CORS with Credentials** | `cerberus/api/app.py:38-44` | `allow_origins=["*"]` with `allow_credentials=True` | Configure explicit origin list from `settings.CORS_ORIGINS`, reject `*` when credentials enabled | Web UI / dashboard or third-party client origins must be included in allowed list |
| **Unvalidated Default Production Secrets** | `cerberus/config.py:25-28` | No Pydantic validator checking production mode | Add `@model_validator(mode="after")` to reject default secrets and enforce min length (32 chars) in production | Ensure dev environment remains smooth while production is strictly secured |

---

### Detailed Code Fix Design (Proposals for Implementer)

#### 1. `cerberus/config.py`
Add `CORS_ORIGINS` setting, helper property `cors_origins_list`, and Pydantic validator for production security:
```python
from pydantic import model_validator

INSECURE_DEFAULT_SECRETS = {
    "cerberus_dev_secret_key_change_in_production_32chars",
    "cerberus_production_secret_key_change_me_now_1234",
    "change_me_in_production",
    "secret",
    "changeme",
    "password",
    "admin",
}

class Settings(BaseSettings):
    ...
    # Security Settings
    SECRET_KEY: str = "cerberus_dev_secret_key_change_in_production_32chars"
    API_KEY_PREFIX: str = "cvai_"
    RATE_LIMIT_PER_HOUR: int = 100
    DEFAULT_DEV_API_KEY: str = "cvai_dev_key_123"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() in ("production", "prod"):
            if not self.SECRET_KEY or self.SECRET_KEY in INSECURE_DEFAULT_SECRETS:
                raise ValueError(
                    "Production configuration error: Insecure default SECRET_KEY is not permitted in production. "
                    "Set a unique, high-entropy SECRET_KEY via environment variable."
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "Production configuration error: SECRET_KEY must be at least 32 characters long in production."
                )
        return self
```

#### 2. `cerberus/api/app.py`
Configure CORS to disallow wildcard `*` with credentials:
```python
    # CORS Configuration
    allowed_origins = settings.cors_origins_list
    allow_creds = True
    if "*" in allowed_origins:
        # Wildcard cannot be combined with credentials
        allow_creds = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_creds,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

#### 3. `cerberus/core/database.py`
Seed development credentials on `init_db()`:
```python
async def init_db() -> None:
    """Initialize database tables and seed development credentials."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")

        # Seed default dev key in development mode
        if settings.ENVIRONMENT == "development" and settings.DEFAULT_DEV_API_KEY:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import select
                from cerberus.core.security import hash_api_key
                dev_hash = hash_api_key(settings.DEFAULT_DEV_API_KEY)
                stmt = select(ApiKeyRecord).where(ApiKeyRecord.key_hash == dev_hash)
                res = await session.execute(stmt)
                if not res.scalars().first():
                    record = ApiKeyRecord(
                        key_hash=dev_hash,
                        name="Default Development Key",
                        prefix=settings.API_KEY_PREFIX,
                        scopes="review:read,review:write,admin",
                        is_active=True,
                    )
                    session.add(record)
                    await session.commit()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
```

#### 4. `cerberus/api/dependencies.py`
Cryptographic verification against active database records:
```python
from datetime import datetime, timezone
from sqlalchemy import select
from cerberus.core.database import AsyncSessionLocal
from cerberus.models.database import ApiKeyRecord
from cerberus.core.security import hash_api_key, rate_limiter

async def verify_api_key(
    request: Request,
    authorization: Optional[str] = Header(None)
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "missing_authentication", "message": "No Authorization header provided"}
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_token_format", "message": "Authorization must be Bearer <token>"}
        )

    token = parts[1]
    token_hash = hash_api_key(token)

    # Validate against stored active credentials
    async with AsyncSessionLocal() as session:
        stmt = select(ApiKeyRecord).where(
            ApiKeyRecord.key_hash == token_hash,
            ApiKeyRecord.is_active.is_(True)
        )
        result = await session.execute(stmt)
        key_record = result.scalars().first()

    if not key_record:
        # Fallback check for dev mode if DB was not pre-seeded
        if settings.ENVIRONMENT == "development" and token == settings.DEFAULT_DEV_API_KEY:
            # Valid dev key
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "invalid_api_key", "message": "API key is invalid or has expired"}
            )
    else:
        if key_record.expires_at:
            exp = key_record.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "invalid_api_key", "message": "API key is invalid or has expired"}
                )

    # Rate Limiting check
    allowed, remaining, retry_after = rate_limiter.is_allowed(token)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limit_exceeded", "message": f"Rate limit exceeded. Retry in {retry_after}s."},
            headers={"Retry-After": str(retry_after)}
        )

    return token
```

#### 5. `cerberus/cli/main.py`
Persist created keys to database in `create_api_key`:
```python
@app.command()
def create_api_key(
    name: str = typer.Option("default", "--name", "-n", help="Name or label for the API key")
):
    """Generate a cryptographically secure cerberus API key."""
    raw_key, key_hash, prefix = generate_api_key(name=name)

    async def _persist():
        from cerberus.core.database import AsyncSessionLocal, init_db
        from cerberus.models.database import ApiKeyRecord
        await init_db()
        async with AsyncSessionLocal() as session:
            rec = ApiKeyRecord(key_hash=key_hash, name=name, prefix=prefix, is_active=True)
            session.add(rec)
            await session.commit()

    asyncio.run(_persist())
    console.print(Panel(...))
```

---

## 5. Verification Method

### 5.1 Existing Regression Suite
Execute existing test suite to ensure no regressions:
```bash
python -m pytest
```
*Current baseline*: 23 passed in 9.92s.

### 5.2 Negative Authentication Verification Tests
Add the following negative and boundary tests to `tests/test_api.py`:
1. **Missing Authorization Header**:
   - Request protected endpoint (`/api/v1/agents`) without `Authorization` header.
   - Expected status: `401 Unauthorized`. Detail: `{"error": "missing_authentication", ...}`.
2. **Malformed Authorization Header**:
   - Header: `Authorization: Token cvai_dev_key_123` or `Authorization: Bearer`.
   - Expected status: `401 Unauthorized`. Detail: `{"error": "invalid_token_format", ...}`.
3. **Fabricated / Unregistered Token with Valid Prefix**:
   - Header: `Authorization: Bearer cvai_fake_token_not_in_database`.
   - Expected status: `401 Unauthorized`. Detail: `{"error": "invalid_api_key", ...}`.
4. **Inactive or Revoked Token**:
   - Insert key with `is_active=False`. Submit header.
   - Expected status: `401 Unauthorized`.
5. **Expired Token**:
   - Insert key with `expires_at = datetime.now(timezone.utc) - timedelta(days=1)`. Submit header.
   - Expected status: `401 Unauthorized`.
6. **Valid Active Token**:
   - Header: `Authorization: Bearer cvai_dev_key_123` (seeded dev key) or newly created key.
   - Expected status: `200 OK`.

### 5.3 CORS Verification Tests
1. **Wildcard Origin with Credentials**:
   - Test preflight `OPTIONS` and cross-origin `GET` with `Origin: http://untrusted-attacker.com`.
   - Assert `Access-Control-Allow-Origin` is NOT reflected as `http://untrusted-attacker.com` if not in `settings.cors_origins_list`.
   - Assert `Access-Control-Allow-Credentials: true` is never returned alongside wildcard `*`.
2. **Whitelisted Origin**:
   - Request with `Origin: http://localhost:3000`.
   - Assert `Access-Control-Allow-Origin: http://localhost:3000` and `Access-Control-Allow-Credentials: true`.

### 5.4 Production Secret Enforcement Tests
1. **Insecure Fallback in Production**:
   - Execute `Settings(ENVIRONMENT="production")` with default `SECRET_KEY`.
   - Assert `pydantic.ValidationError` or `ValueError` is raised with message indicating insecure secret rejection.
2. **Short Secret in Production**:
   - Execute `Settings(ENVIRONMENT="production", SECRET_KEY="too-short")`.
   - Assert validation error is raised.
3. **Valid Secret in Production**:
   - Execute `Settings(ENVIRONMENT="production", SECRET_KEY="a"*32)`.
   - Assert instance successfully initializes.

### 5.5 Invalidation Conditions
- Any change that allows `Authorization: Bearer cvai_anything` to succeed invalidates the security fix.
- Any CORS response with both `Access-Control-Allow-Origin: *` and `Access-Control-Allow-Credentials: true` invalidates the CORS fix.
- Booting the application with `ENVIRONMENT=production` and default `SECRET_KEY` without an error invalidates the configuration fix.
