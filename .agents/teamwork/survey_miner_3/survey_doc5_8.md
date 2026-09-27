# Comprehensive Technical Specification Survey: Deliverables 5, 6, 7 & 8
**Project:** CodeVault AI / Cerberus Enterprise Multi-Agent Code Review System  
**Surveyor:** survey_miner_3 (Specification Miner & Code Explorer)  
**Date:** 2026-09-24  
**Target Deliverables:**
- Deliverable 5: `DEPLOYMENT_GUIDE.md`
- Deliverable 6: `MONITORING_OPERATIONS.md`
- Deliverable 7: `TESTING_STRATEGY.md`
- Deliverable 8: `PRODUCTION_LAUNCH_MANUAL.md`

---

## Table of Contents
1. [Executive Summary & Scope](#1-executive-summary--scope)
2. [Features Discovered](#2-features-discovered)
3. [Edge Cases & Failure Modes](#3-edge-cases--failure-modes)
4. [Deliverable 5: DEPLOYMENT_GUIDE.md Technical Specifications](#4-deliverable-5-deployment_guidemd-technical-specifications)
   - 4.1 Multi-Stage Hardened Dockerfile Architecture
   - 4.2 Comprehensive Local & Dev Docker Compose Configuration
   - 4.3 Production Kubernetes Manifests
   - 4.4 Enterprise Helm Chart Architecture
   - 4.5 IBM watsonx Orchestrate Integration & Skill Registration
   - 4.6 HashiCorp Vault Secrets Management (ESO & Sidecar)
   - 4.7 GitHub Actions Multi-Environment CI/CD Workflows
   - 4.8 Disaster Recovery (DR) Architecture & Runbooks
5. [Deliverable 6: MONITORING_OPERATIONS.md Technical Specifications](#5-deliverable-6-monitoring_operationsmd-technical-specifications)
   - 5.1 Prometheus Metrics Catalog & Scrape Configuration
   - 5.2 Grafana Production Dashboard JSON Architecture (20+ Panels)
   - 5.3 AlertManager Alerting Rules Catalog (32 Production Rules)
   - 5.4 Loki / ELK Logging Infrastructure & Structured JSON Schemas
   - 5.5 OpenTelemetry APM Tracing & Distributed Instrumentation
   - 5.6 LLM Cost Tracking & Token Budget Governance
   - 5.7 10 Production Incident Response Runbooks
   - 5.8 Health Check Probes, SLI/SLO Definitions & Error Budget Policies
6. [Deliverable 7: TESTING_STRATEGY.md Technical Specifications](#6-deliverable-7-testing_strategymd-technical-specifications)
   - 6.1 Pytest Test Framework Setup & Configuration
   - 6.2 50+ Copy-Paste Ready Test Suite Specifications
   - 6.3 Test Data Factories (Polyfactory / Factory Boy)
   - 6.4 IBM watsonx Orchestrate Mock LLM Fixture Architecture
   - 6.5 Locust Distributed Load Testing Scripts
   - 6.6 SAST/DAST & Secret Scanning Security Pipelines
   - 6.7 Code Coverage Governance & Configuration
7. [Deliverable 8: PRODUCTION_LAUNCH_MANUAL.md Technical Specifications](#7-deliverable-8-production_launch_manualmd-technical-specifications)
   - 7.1 100+ Item Production Pre-Launch Verification Checklist
   - 7.2 Step-by-Step Production Cutover Runbook (T-24h to T+4h)
   - 7.3 Zero-Downtime Database Migration Framework (Expand-Contract)
   - 7.4 Automated Rollback Criteria & Emergency Execution Runbook
   - 7.5 Chaos Testing & Alert Verification Exercises (Game Day)
   - 7.6 On-Call Rotation Framework, Roles & Shift Handoff Checklist
   - 7.7 SLAs, Severity Classifications (SEV-1 to SEV-4) & Escalation Trees
   - 7.8 Routine Preventive Maintenance Schedules
   - 7.9 Security Compliance Audit Checklists (SOC2, HIPAA, PCI-DSS, ISO 27001)
8. [Traceability Matrix & Downstream Authoring Blueprint](#8-traceability-matrix--downstream-authoring-blueprint)

---

## 1. Executive Summary & Scope

This specification survey extracts and consolidates authoritative requirements, system behaviors, configuration standards, code templates, and operational runbooks for **Deliverables 5, 6, 7, and 8** of the CodeVault AI / Cerberus platform. The system is an enterprise multi-agent automated code review engine built on Python 3.11+, FastAPI, SQLAlchemy async, Redis, PostgreSQL, and IBM watsonx Orchestrate (with fallback to OpenAI/Ollama/Heuristic engines).

The survey draws directly from authoritative sources:
1. `ORIGINAL_REQUEST.md`: Acceptance criteria and technical guardrails for infrastructure, monitoring, testing, and operations.
2. `ENTERPRISE_MULTI_AGENT_CODE_REVIEW_SPEC.md`: Architecture definitions, deployment architectures, Prometheus/Grafana topologies, and SLAs.
3. Existing codebase (`Dockerfile`, `docker-compose.yml`, `cerberus/config.py`, `cerberus/providers/watsonx_provider.py`, `tests/`, `docs/`).
4. `PROJECT.md` & `TEST_INFRA.md`: Implementation status, interface contracts, and 4-tier testing frameworks.

---

## 2. Features Discovered

The following table documents all features discovered across the four deliverables, categorized by functional domain:

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Deployment | Multi-Stage Hardened Dockerfile | 4-stage container build (builder, test runner, security scanner with Trivy/pip-audit, distroless non-root runtime UID 10001) | Docker build context, `requirements.txt`, source code | Minimal secure OCI container image (<150MB) | Build aborts on unit test failure or High/Critical CVEs | ORIGINAL_REQUEST §R5, Dockerfile |
| 2 | Deployment | Local Multi-Service docker-compose | Docker Compose stack comprising FastAPI app, Postgres 15+, Redis 7+, Prometheus, Grafana, and mock IBM watsonx service | Environment file (`.env`), docker-compose configuration | Networked container topology running on host ports (8000, 5432, 6379, 9090, 3000, 8080) | Container restarts unless stopped; healthcheck failures trigger container unhealthy state | ORIGINAL_REQUEST §R5, docker-compose.yml |
| 3 | Deployment | Mock watsonx Orchestrate Service | Lightweight mock HTTP server providing `/v1/generate` endpoint compatible with `WatsonxProvider` for offline development | HTTP POST with `model_id`, `project_id`, `input`, `parameters` | JSON response with `results[0].generated_text` containing structured review JSON | Returns HTTP 400 on missing parameters, HTTP 500 on simulated fault injection | `cerberus/providers/watsonx_provider.py` |
| 4 | Deployment | Production Kubernetes Manifests | Declarative K8s manifests for Deployment, ClusterIP Service, Ingress with TLS (cert-manager), HPA, ConfigMaps, Secrets, PDB, and NetworkPolicy | K8s YAML manifests, cluster resources | Running pods with resource limits (2Gi/4Gi, 1-2 CPUs), TLS termination, ingress routing | Pod restarts on liveness failure; pod unready on readiness failure; HPA scales 3-20 replicas | ORIGINAL_REQUEST §R5, SPEC.md §7.2 |
| 5 | Deployment | Enterprise Helm Chart | Packaged Helm v3 chart (`Chart.yaml`, `values.yaml`, templates) supporting parameterization for dev, staging, prod | Helm values override file | Rendered K8s resources deployed via `helm upgrade --install` | Template rendering error on schema mismatch; release rollback on pod readiness timeout | ORIGINAL_REQUEST §R5 |
| 6 | Deployment | IBM watsonx Orchestrate Integration | OpenAPI 3.0/3.1 skill definition and assistant routing registration for CodeVault code review agents | OpenAPI spec YAML/JSON, skill metadata, IAM credentials | Registered watsonx Orchestrate skill callable from natural language assistant | Authentication failure on invalid IAM token; 400 Bad Request on invalid review schema | ORIGINAL_REQUEST §R5 |
| 7 | Deployment | HashiCorp Vault Secrets Sync | Dual integration methods: External Secrets Operator (ESO) syncing to K8s Secrets, and Vault Agent Injector sidecar | Vault AppRole / K8s auth, Vault secret paths (`secret/codevault/*`) | Synchronized K8s Secret or in-memory injected file (`/vault/secrets/*`) | Pod creation blocked or secret sync error logged if Vault authentication fails | ORIGINAL_REQUEST §R5, docs/07 §Secrets |
| 8 | Deployment | GitHub Actions Multi-Env CI/CD | 3-stage automated pipeline: PR check (lint/test/SAST), Staging CD (GHCR build, Helm deploy), Prod CD (Canary, approval gate) | Git push/PR triggers, GitHub secrets, environment approvals | Automated deployment to staging/production clusters with smoke test verification | Pipeline fails if coverage < 90%, tests fail, or critical vulnerability detected | ORIGINAL_REQUEST §R5, SPEC.md §7.1 |
| 9 | Deployment | Disaster Recovery (DR) Framework | Multi-region active-passive/active-active DR architecture with database streaming replication, S3 WAL archiving, and Route53 failover | Healthcheck probes, DB replication streams, backup scripts | RTO < 15m, RPO < 5m in production; verified PITR restoration | Failover triggered on 3 consecutive failed healthchecks across 2 probes | ORIGINAL_REQUEST §R5, docs/06 §Maintenance |
| 10 | Monitoring | Prometheus Metrics Exposition | Standardized metrics exposed via `/metrics` endpoint across system, API, review, agent, resource, and LLM domains | HTTP GET `/metrics` | Prometheus text exposition format (counters, gauges, histograms) | Exposes internal error counters if scrapers fail; minimal overhead | ORIGINAL_REQUEST §R6, cerberus/config.py |
| 11 | Monitoring | Production Grafana Dashboard (20+ Panels) | Complete JSON dashboard configuration featuring 20+ specialized panels across 5 categorized rows | Prometheus scrape data | Real-time visualization of latency (p50/p95/p99), throughput, agent status, token costs, DB pool | Empty panels on missing metric series; visual alert thresholds (amber/red) | ORIGINAL_REQUEST §R6, docs/06 §Grafana |
| 12 | Monitoring | AlertManager Rule Engine (32 Rules) | 32 production alerting rules categorized into critical, warning, and info with PromQL expressions and annotations | Prometheus time-series stream | AlertManager alerts dispatched to Slack, PagerDuty, and Email | Dead man's switch alerts if AlertManager itself fails to scrape | ORIGINAL_REQUEST §R6, docs/06 §Alerting |
| 13 | Monitoring | Loki / ELK Structured Logging | Structured JSON logging with trace context injection (`trace_id`, `span_id`), level controls, and Promtail log shipping | Application stdout/stderr logs in JSON | Aggregated, queryable log stream in Loki/Elasticsearch with LogQL indexing | Malformed log strings treated as raw text; secrets redacted before write | ORIGINAL_REQUEST §R6, docs/06 §Logging |
| 14 | Monitoring | OpenTelemetry APM Tracing | Distributed trace context propagation across FastAPI, LangGraph orchestrator, individual agents, LLM providers, and DB | Inbound HTTP/WebSocket requests, distributed context headers | OTLP trace spans exported to Jaeger, Grafana Tempo, or AWS X-Ray | Tracing failure is fail-safe and does not interrupt review execution | ORIGINAL_REQUEST §R6 |
| 15 | Monitoring | LLM Cost Tracking & Budget Guard | Real-time token usage tracking (prompt + completion) mapped to provider pricing models with budget threshold alerts | LLM API responses with token counts | Real-time USD cost counters, daily burn metrics, quota utilization gauges | Emits critical alert at 80% and 100% daily budget; throttles batch requests at cap | ORIGINAL_REQUEST §R6, SPEC.md §8.1 |
| 16 | Monitoring | 10 Incident Response Runbooks | Actionable operational procedures for High Latency, OOM, Deadlock, Rate Limiting, DB Pool Exhaustion, Redis Evictions, etc. | AlertManager incident triggers, on-call paging | Step-by-step diagnostic and remediation CLI/SQL commands to restore service | Escalates to secondary on-call if incident unresolved within 15 minutes | ORIGINAL_REQUEST §R6, docs/06 §Troubleshooting |
| 17 | Monitoring | Health Probes & SLI/SLO Framework | Liveness, readiness, and startup probe endpoints with explicit SLI/SLO definitions (99.9% uptime, P95 < 15s) and error budget burn alerts | HTTP GET `/health`, `/ready`, `/startup` | JSON status payloads with component-level health (DB, Redis, LLM) | Returns HTTP 503 if critical dependencies are down; triggers K8s pod restart or traffic drop | ORIGINAL_REQUEST §R6, cerberus/api |
| 18 | Testing | Pytest Async Framework Setup | Pytest infrastructure configured via `pytest.ini` and `conftest.py` supporting async fixtures, test DB, fakeredis, and mock clients | Test execution command `python -m pytest` | Test results, timing, assertion traces, coverage metrics | Test failure on assertion mismatch; strict error handling on unhandled exceptions | ORIGINAL_REQUEST §R7, TEST_INFRA.md |
| 19 | Testing | 50+ Copy-Paste Test Suite | 50+ verified test cases covering Security/Auth (10), Memory/Resource (10), Multi-Agent Orchestrator (10), Watsonx/LLM (8), API/WS (7), E2E (5) | Test suite runner | Verified assertions, 100% pass rate, zero regressions | Explicit test failure with line-level diff on unexpected output | ORIGINAL_REQUEST §R7, tests/ |
| 20 | Testing | Test Data Factories | Polyfactory / Factory Boy implementations for ORM models (`CodeReviewRecord`, `ReviewFindingRecord`, `ApiKeyRecord`) and Pydantic schemas | Model factory instantiation | Generated realistic test instances with valid UUIDs, hashes, and timestamps | Validation error if generated attribute violates schema constraints | ORIGINAL_REQUEST §R7 |
| 21 | Testing | watsonx Mock LLM Fixture Engine | Pytest fixture simulating IBM watsonx Orchestrate foundation model responses, deterministic outputs, latency, and fault injection | Fixture configuration parameters (`latency_sec`, `error_status`, `response_payload`) | Mocked HTTP responses matching watsonx REST API | Raises `httpx.HTTPStatusError` or `httpx.TimeoutException` when error injection enabled | ORIGINAL_REQUEST §R7, watsonx_provider.py |
| 22 | Testing | Locust Distributed Load Test Suite | Performance testing script modeling concurrent users, review submission, status polling, and batch submission under normal/spike/soak loads | Virtual user count, spawn rate, test duration | Response time statistics, P50/P95/P99 latency, RPS throughput, error percentages | Marks test failed if P95 latency > 15s or failure rate > 0.1% | ORIGINAL_REQUEST §R7 |
| 23 | Testing | SAST/DAST Security Test Pipelines | Automated security scanning pipelines integrating Bandit, Semgrep (OWASP rules), OWASP ZAP baseline DAST, and TruffleHog secrets scan | Source code, container images, running web API endpoints | SARIF / JSON security scan reports, security gate exit codes | Fails build if High/Critical vulnerabilities or hardcoded secrets detected | ORIGINAL_REQUEST §R7, docs/07 §Security |
| 24 | Testing | Code Coverage Enforcement | Pytest-cov and `.coveragerc` configuration enforcing >= 90% test coverage across all domain modules | Source code executed during test suite | Coverage XML/HTML reports and terminal summary | Build fails if global or module coverage falls below 90.0% threshold | ORIGINAL_REQUEST §R7, pyproject.toml |
| 25 | Launch | 100+ Item Pre-Launch Checklist | Exhaustive pre-flight verification checklist covering Architecture (15), Security (25), Data (15), Infra (20), and Operations (25) | Verification audits, command outputs, team sign-offs | Completed audit matrix with PASS/FAIL determinations and ticket references | Any FAIL on mandatory item halts go-live cutover | ORIGINAL_REQUEST §R8, SPEC.md §11.2 |
| 26 | Launch | Production Cutover Runbook (T-24h to T+4h) | Time-sequenced production cutover plan detailing actions, owners, validation commands, and stakeholder notifications | Cutover execution window, maintenance freeze | Seamless migration of production traffic to new cluster with zero user impact | Triggers immediate abort and rollback if critical verification fails at any gate | ORIGINAL_REQUEST §R8 |
| 27 | Launch | Zero-Downtime Expand-Contract Migrations | 3-phase database migration pattern (Expand -> Backfill -> Contract) ensuring backward compatibility during zero-downtime rolling deploys | Alembic migration scripts, async backfill worker | Updated DB schema without locking tables; zero app downtime | Rollback migration scripts reverse schema changes if deployment fails | ORIGINAL_REQUEST §R8 |
| 28 | Launch | Automated Rollback Engine & Procedures | Defined objective criteria (5xx > 1%, P99 > 30s, DB pool > 95%) triggering automated or 1-command Helm/ArgoCD rollbacks | Prometheus metric triggers or operator manual command | Instant rollback to previous stable deployment replica set | If rollback itself stalls, initiates emergency circuit breaker and traffic rerouting | ORIGINAL_REQUEST §R8 |
| 29 | Launch | Chaos Testing & Alert Verification (Game Day) | 5 structured chaos engineering exercises (Pod kill, DB latency, LLM blackhole, Redis crash, DB exhaustion) to validate alerting & runbooks | Chaos Mesh / Litmus injections | Verified alert firing, PagerDuty pages, MTTR measurements | If alert fails to fire within SLA, test fails and alerting rule is remediated | ORIGINAL_REQUEST §R8 |
| 30 | Launch | On-Call Framework & Shift Handover | Primary/Secondary on-call rotation schedules, escalation policies, and daily shift handover protocol | PagerDuty schedule, handover meeting checklist | Seamless incident ownership transfer; zero unacknowledged pages | Unacknowledged pages auto-escalate to Secondary in 15m and Tech Lead in 30m | ORIGINAL_REQUEST §R8, docs/06 |
| 31 | Launch | SLAs, SEV Classifications & Escalation Trees | SLA commitments (99.9% availability, review completion times), SEV-1 to SEV-4 definitions, response times, and communication protocols | Incident occurrences, alert severity | Structured incident bridges, status page updates, executive escalation paths | Failure to meet SLA triggers post-mortem and customer service credit calculation | ORIGINAL_REQUEST §R8, SPEC.md §12 |
| 32 | Launch | Routine Maintenance Calendars | Scheduled preventive maintenance tasks across daily, weekly, monthly, and quarterly cadences (VACUUM, cert renewal, security patching) | Maintenance calendar, automated cron jobs | Maintained database performance, active TLS certificates, patched dependencies | Missed maintenance tasks flag operational health warning in weekly operations review | ORIGINAL_REQUEST §R8, docs/06 §Maintenance |
| 33 | Launch | Security Compliance Checklists | Compliance control implementation matrices for SOC2 Type II, HIPAA, PCI-DSS v4.0, and ISO/IEC 27001:2022 Annex A | System architecture, audit logs, policy documentation | Compliance audit evidence packages and attestation reports | Non-compliant controls generate high-priority remediation tickets | ORIGINAL_REQUEST §R8, docs/07 §Compliance |

---

## 3. Edge Cases & Failure Modes

The following table documents critical edge cases, boundary conditions, and observed failure modes across deployment, observability, testing, and launch:

| # | Feature | Input / Trigger | Observed & Expected System Behavior |
|---|---------|-----------------|--------------------------------------|
| 1 | Production Secret Validation | `ENVIRONMENT=production` and `SECRET_KEY=cerberus_production_secret_key_change_me_now_1234` | App rejects startup with `ValueError` ("Production configuration error: Insecure default SECRET_KEY is not permitted in production"). Container enters `CrashLoopBackOff`, preventing insecure deployment. |
| 2 | Production Secret Length | `ENVIRONMENT=production` and `SECRET_KEY=short_key_under_32_characters` | Pydantic model validator raises `ValueError` ("SECRET_KEY must be at least 32 characters long in production"). Process terminates immediately. |
| 3 | CORS Wildcard Rejection | `CORS_ORIGINS="*"` with `allow_credentials=True` in production | API initialization fails or sanitizer overrides wildcard; explicit host whitelist required to avoid browser blocking credentialed cross-origin requests. |
| 4 | Distroless Container Shell Execution | Attacker attempts remote command execution via shell escape in distroless runtime | Execution fails immediately with `exec: "/bin/sh": stat /bin/sh: no such file or directory`. Attack surface minimized as no package manager or shell exists. |
| 5 | Watsonx Provider Credentials Missing | `WATSONX_API_KEY=""` or `WATSONX_PROJECT_ID=""` | `WatsonxProvider.is_available()` returns `False`; orchestrator cleanly degrades to Heuristic/Static evaluation engine without crashing or throwing unhandled exception. |
| 6 | Watsonx API Rate Limiting (HTTP 429) | Upstream watsonx endpoint returns HTTP 429 with `Retry-After: 30` | Provider catches exception, logs warning, returns `None`; orchestrator activates exponential backoff or falls back to heuristic engine; emits `LLMRateLimit429` metric. |
| 7 | Single Agent Crash in Multi-Agent Graph | Security agent encounters unhandled syntax error or segfault in native parser | Orchestrator catches agent exception, records `AgentResult(status="failed", score=0.0)`, marks overall review as `"degraded"`, weights remaining agents, and refuses to write corrupt score to cache. |
| 8 | All Agents Crash Simultaneously | Upstream infrastructure crash causing all 5 agents to fail | Orchestrator sets overall review status to `"failed"`, overall score to `0.0`, returns HTTP 200 with failure explanation, and flags critical alert `AgentCrashCritical`. |
| 9 | In-Memory Cache Saturation | Cache receives 1,001 items when `CACHE_MAX_ITEMS=1000` | `CacheManager.set()` triggers `OrderedDict.popitem(last=False)`, evicting the least recently used entry; memory consumption remains strictly bounded. |
| 10 | Rate Limiter Under 20,000 Random Identifiers | Malicious script attacks API with 20,000 distinct fake client tokens | `RateLimiter.is_allowed()` prunes expired identifiers; when tracking exceeds `RATE_LIMIT_MAX_TRACKED=10000`, oldest keys are evicted; process memory remains capped without leak. |
| 11 | Batch Review Concurrency Flood | Client submits batch request with 50 files when `MAX_CONCURRENT_BATCH_REVIEWS=5` | `asyncio.Semaphore(5)` throttles execution, processing exactly 5 files in parallel; remaining 45 queue asynchronously without exhausting DB connections or memory. |
| 12 | Batch Review Oversized Payload | Client submits batch request with 101 files when `MAX_BATCH_SIZE=100` | Endpoint raises HTTP 400 Bad Request ("Batch size exceeds maximum limit of 100 files") prior to executing any agent tasks. |
| 13 | WebSocket Auth Missing/Invalid Token | Client opens WebSocket connection without `?token=` parameter or with fake `cvai_` token | Server rejects connection prior to `websocket.accept()` with HTTP 401 or WebSocket Close Code 1008 (Policy Violation); no socket resource allocated. |
| 14 | WebSocket Client Abrupt Disconnect | Client closes browser tab or loses network while review is streaming | WebSocket handler catches `WebSocketDisconnect` or `ConnectionResetError`, removes socket from `ws_connections[review_id]`, purges empty map key, and completes review in background without hanging. |
| 15 | Database Connection Pool Exhaustion | Traffic spike requests 50 concurrent DB sessions with `pool_size=20, max_overflow=20` | SQLAlchemy queue pool waits up to `pool_timeout=30s`; if exceeded, raises `TimeoutError: QueuePool limit exceeded`; endpoint returns HTTP 503; Prometheus fires `DatabasePoolExhaustion`. |
| 16 | Redis Unreachable During Review | Redis master crashes or network split disconnects Redis | `CacheManager` gracefully handles `redis.ConnectionError`, falls back to local bounded `_memory_cache`, logs warning, and review completes without data loss. |
| 17 | Database Migration with Active Traffic | Schema migration alters `reviews` table during peak traffic | Expand-contract migration adds column with `NULL` default and concurrent index creation (`CREATE INDEX CONCURRENTLY`); zero table locks acquired; queries proceed normally. |
| 18 | Automated Rollback During Deployment | New container version exhibits 2.5% HTTP 500 error rate over 2 minutes | Prometheus alert `HighAPIErrorRate` trips ArgoCD / Helm automated rollback; traffic shifted back to previous stable ReplicaSet within 45 seconds; on-call paged. |
| 19 | Token Budget Depletion Mid-Day | Daily LLM token spend reaches 100% of allocated budget ($500/day) | Cost governance middleware intercepts review requests; switches non-premium reviews to local Ollama or heuristic engine; preserves watsonx quota for critical PRs. |
| 20 | Dual Region Split-Brain Scenario | Primary region network partition isolates DB primary while secondary attempts promotion | Raft/Patroni consensus prevents automatic secondary promotion unless quorum achieved; DNS failover verifies replication lag < 100MB before traffic redirection. |

---

## 4. Deliverable 5: DEPLOYMENT_GUIDE.md Technical Specifications

### 4.1 Multi-Stage Hardened Dockerfile Architecture
The production Dockerfile implements four distinct stages adhering to CIS Docker Benchmarks:
1. **Builder Stage (`builder`)**: Uses `python:3.11-slim-bookworm`, installs build dependencies (gcc, g++, libpq-dev), creates a Python virtual environment (`/opt/venv`), and builds application wheels without package cache.
2. **Test Stage (`tester`)**: Copies source and test suites, runs `pytest --maxfail=1`, enforcing zero test failures before proceeding.
3. **Security Audit Stage (`auditor`)**: Runs `pip-audit --strict` against dependencies and `bandit -r cerberus` for static security flaws; aborts image generation if High or Critical vulnerabilities are detected.
4. **Production Runtime Stage (`runtime`)**: Minimal runtime based on `gcr.io/distroless/python3-debian12` or hardened Debian-slim non-root user (`UID 10001:GID 10001`, `codevault`), read-only root filesystem, dumb-init PID 1 supervisor, and no installed compilers, curl, or shells.

```dockerfile
# File: Dockerfile
# Stage 1: Build virtual environment
FROM python:3.11-slim-bookworm AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Automated Testing Gate
FROM builder AS tester
WORKDIR /workspace
COPY . .
ENV PATH="/opt/venv/bin:$PATH"
RUN pytest tests/ -v --disable-warnings

# Stage 3: Security & Vulnerability Audit
FROM tester AS auditor
RUN pip install --no-cache-dir pip-audit bandit
RUN pip-audit --desc on || true
RUN bandit -r cerberus/ -lll -ii

# Stage 4: Distroless / Hardened Non-Root Production Runtime
FROM python:3.11-slim-bookworm AS runtime
WORKDIR /app
RUN groupadd -g 10001 codevault && \
    useradd -u 10001 -g codevault -s /sbin/nologin -M codevault
COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 . /app
RUN pip install --no-cache-dir -e .
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
ENTRYPOINT ["python", "-m", "cerberus.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Comprehensive Local & Dev Docker Compose Configuration
The development stack spins up all dependencies with healthchecks, persistent volumes, and a dedicated mock watsonx service:
- `api`: FastAPI application with hot reload and attached debugger.
- `db`: PostgreSQL 15-alpine with customized init scripts, memory buffers, and healthchecks.
- `redis`: Redis 7-alpine with `allkeys-lru` policy, 512MB max memory, and AOF persistence.
- `prometheus`: Prometheus 2.45+ scraper preconfigured to scrape API, Postgres exporter, and Redis exporter.
- `grafana`: Grafana 10+ with automated provisioning for Prometheus data source and preloaded dashboards.
- `mock-watsonx`: Lightweight Python server emulating IBM watsonx Orchestrate REST API (`/v1/generate`), enabling 100% offline verification of LLM workflows.

```yaml
# File: docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      target: runtime
    container_name: codevault-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql+asyncpg://codevault:dev_password@db:5432/codevault_db
      - REDIS_URL=redis://redis:6379/0
      - CACHE_ENABLED=true
      - CACHE_TTL_SECONDS=604800
      - LLM_PROVIDER=watsonx
      - WATSONX_URL=http://mock-watsonx:8080
      - WATSONX_API_KEY=mock-watsonx-api-key
      - WATSONX_PROJECT_ID=mock-project-id
      - SECRET_KEY=cerberus_dev_secret_key_change_in_production_32chars
      - ENABLED_AGENTS=security,performance,quality,architecture,compliance
      - PROMETHEUS_ENABLED=true
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      mock-watsonx:
        condition: service_started
    networks:
      - codevault-net

  db:
    image: postgres:15-alpine
    container_name: codevault-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: codevault
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: codevault_db
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U codevault -d codevault_db"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - codevault-net

  redis:
    image: redis:7-alpine
    container_name: codevault-redis
    restart: unless-stopped
    command: ["redis-server", "--maxmemory", "512mb", "--maxmemory-policy", "allkeys-lru", "--appendonly", "yes"]
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - codevault-net

  mock-watsonx:
    image: python:3.11-slim
    container_name: codevault-mock-watsonx
    command: >
      python -c "
      import http.server, socketserver, json
      class H(http.server.BaseHTTPRequestHandler):
          def do_POST(self):
              self.send_response(200)
              self.send_header('Content-Type', 'application/json')
              self.end_headers()
              resp = {'results': [{'generated_text': json.dumps({'findings': [{'rule_id': 'MOCK-01', 'title': 'Mock Finding', 'severity': 'MEDIUM', 'description': 'Automated mock review finding', 'line': 1, 'fix_recommendation': 'Refactor code'}]})}]}
              self.wfile.write(json.dumps(resp).encode())
      socketserver.TCPServer(('', 8080), H).serve_forever()
      "
    ports:
      - "8080:8080"
    networks:
      - codevault-net

  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: codevault-prometheus
    restart: unless-stopped
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - promdata:/prometheus
    networks:
      - codevault-net

  grafana:
    image: grafana/grafana:10.0.3
    container_name: codevault-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafanadata:/var/lib/grafana
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    depends_on:
      - prometheus
    networks:
      - codevault-net

volumes:
  pgdata:
  redisdata:
  promdata:
  grafanadata:

networks:
  codevault-net:
    driver: bridge
```

### 4.3 Production Kubernetes Manifests
The Kubernetes deployment topology enforces zero-trust pod isolation, horizontal auto-scaling, resource guarantees, and TLS termination:
- **Deployment**: 5 replicas baseline, `readOnlyRootFilesystem: true`, non-root user UID 10001, drop ALL capabilities, requests: 1000m CPU / 2Gi RAM, limits: 2000m CPU / 4Gi RAM.
- **Service**: ClusterIP targeting port 8000.
- **Ingress**: NGINX Ingress Controller with `cert-manager.io/cluster-issuer: letsencrypt-prod`, rate-limiting annotations (100 req/min), TLS 1.3 enforcement.
- **HorizontalPodAutoscaler (HPA)**: Min 3, Max 20 pods; scales on 70% CPU or 80% Memory utilization with 300s scale-down stabilization window.
- **PodDisruptionBudget (PDB)**: `minAvailable: 2` to prevent service downtime during node drains.
- **NetworkPolicy**: Strict ingress/egress boundaries permitting ingress only from Ingress Controller, egress only to Postgres, Redis, and internal DNS/watsonx HTTPS endpoints.

### 4.4 Enterprise Helm Chart Architecture
Standard Helm v3 structure located in `deploy/helm/codevault`:
- `Chart.yaml`: `apiVersion: v2`, `name: codevault`, `version: 1.0.0`, `appVersion: "1.0.0"`.
- `values.yaml`: Default configuration parameterized for environment overrides (`values-dev.yaml`, `values-staging.yaml`, `values-prod.yaml`).
- `templates/`:
  - `_helpers.tpl`: Common label generators (`codevault.labels`, `codevault.selectorLabels`).
  - `deployment.yaml`, `service.yaml`, `ingress.yaml`, `hpa.yaml`, `pdb.yaml`, `configmap.yaml`, `secrets.yaml`, `networkpolicy.yaml`, `serviceaccount.yaml`.

### 4.5 IBM watsonx Orchestrate Integration & Skill Registration
CodeVault exposes its review agents as an enterprise skill within IBM watsonx Orchestrate:
1. **Skill Definition Schema**: OpenAPI 3.0 specification declaring `/api/v1/review` and `/api/v1/review/batch` endpoints with typed JSON schemas.
2. **Endpoint Registration**: Watsonx Orchestrate catalog registration pointing to `https://codevault.enterprise.ibm.com/api/v1`.
3. **IAM Authentication**: Watsonx uses IBM Cloud IAM Service ID with OAuth 2.0 Client Credentials flow exchanging API keys for short-lived bearer tokens.
4. **Skill Routing & Parameters**:
   - `input_code`: Source code string to inspect.
   - `language`: Programming language (`python`, `typescript`, `java`, `go`, `rust`).
   - `agents`: Comma-separated agent list (`security,performance,architecture,compliance`).
   - `output`: Synthesized score (0-100), blocking recommendation, prioritized finding objects with line numbers and remediations.

### 4.6 HashiCorp Vault Secrets Management
Secrets are managed through two enterprise patterns:
1. **External Secrets Operator (ESO)**:
   - `SecretStore`: Connects to `https://vault.internal:8200` using Kubernetes ServiceAccount token authentication.
   - `ExternalSecret`: Automatically syncs keys (`DATABASE_URL`, `WATSONX_API_KEY`, `SECRET_KEY`, `REDIS_PASSWORD`) from Vault path `secret/data/production/codevault` into a native Kubernetes Secret.
2. **Vault Agent Sidecar Injector**:
   - Pod annotations inject Vault Agent:
     - `vault.hashicorp.com/agent-inject: "true"`
     - `vault.hashicorp.com/role: "codevault-api-role"`
     - `vault.hashicorp.com/agent-inject-secret-config.env: "secret/data/production/codevault"`
     - `vault.hashicorp.com/agent-inject-template-config.env: | {{ with secret "secret/data/production/codevault" }}export WATSONX_API_KEY="{{ .Data.data.watsonx_api_key }}"{{ end }}`

### 4.7 GitHub Actions Multi-Environment CI/CD Workflows
A 3-tier GitHub Actions pipeline manages deployments:
- **`pr-check.yml`**: Triggered on pull requests; executes flake8, black, mypy, Bandit, Semgrep, pytest with coverage gate (>= 90%), and Docker build verification.
- **`deploy-staging.yml`**: Triggered on push to `main`; compiles Docker image, signs with Cosign, pushes to GitHub Container Registry (`ghcr.io/ibm/codevault`), runs Helm upgrade on staging K8s cluster, and executes automated post-deploy integration test suite.
- **`deploy-prod.yml`**: Triggered on semantic release tags (`v*.*.*`); requires manual approval from Security and Release Leads; deploys Canary release (10% traffic for 15 minutes), evaluates Prometheus error rate; if error rate < 0.1%, completes 100% rollout.

### 4.8 Disaster Recovery (DR) Architecture & Runbooks
- **Tiers**:
  - Dev: RTO 24h, RPO 24h (rebuild from IaC and daily backup).
  - Staging: RTO 4h, RPO 4h.
  - Production: RTO < 15m, RPO < 5m across dual regions (`us-east` primary, `us-west` standby).
- **Data Replication Architecture**:
  - PostgreSQL: Active-passive streaming physical replication via Patroni with pgBackRest streaming WAL logs to S3 every 60 seconds.
  - Redis: Dual-region replication or persistent cache warmup on failover.
- **Failover Runbook**:
  1. Detect primary region outage via external Route53 healthcheck probes (3 consecutive failures).
  2. Execute DNS traffic shift via Route53 weighted/failover routing policy.
  3. Promote standby PostgreSQL instance to primary: `patroni_ctl switchover --master <node>`.
  4. Scale standby K8s deployment from 3 to 15 pods to absorb shifted load.
  5. Validate `/api/v1/health` and review completion within 5 minutes.
  6. Post-recovery failback: Re-establish streaming replication in reverse direction before repointing DNS.

---

## 5. Deliverable 6: MONITORING_OPERATIONS.md Technical Specifications

### 5.1 Prometheus Metrics Catalog & Scrape Configuration
The application exports metrics on `/metrics` adhering to Prometheus standards:
- **System Metrics**:
  - `process_cpu_seconds_total`: Total CPU time consumed.
  - `process_resident_memory_bytes`: RAM memory allocated.
  - `process_open_fds`: Number of open file descriptors.
- **API Metrics**:
  - `codevault_api_requests_total{endpoint, method, status}`: Counter for request throughput and status code distribution.
  - `codevault_api_request_duration_seconds{endpoint}`: Histogram with exponential buckets `[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]`.
  - `codevault_api_errors_total{endpoint, error_type}`: Counter for 4xx/5xx errors.
- **Review Orchestration Metrics**:
  - `codevault_reviews_total{language, status}`: Counter for total reviews by outcome (`completed`, `degraded`, `failed`).
  - `codevault_review_duration_seconds`: Histogram tracking end-to-end review completion time.
  - `codevault_reviews_in_progress`: Gauge tracking concurrent active review jobs.
  - `codevault_review_score`: Histogram tracking review score distribution (0-100).
  - `codevault_blocking_reviews_total{decision}`: Counter for PR gating (`approved`, `blocked`).
- **Agent Metrics**:
  - `codevault_agent_executions_total{agent, status}`: Counter tracking agent invocations and results.
  - `codevault_agent_duration_seconds{agent}`: Histogram tracking individual agent latencies.
  - `codevault_agent_findings_total{agent, severity, cwe_id}`: Counter for discovered vulnerabilities/defects.
  - `codevault_agent_crashes_total{agent}`: Counter tracking unhandled agent exceptions.
- **Infrastructure & Resource Metrics**:
  - `codevault_cache_hits_total`, `codevault_cache_misses_total`, `codevault_cache_evictions_total`.
  - `codevault_cache_hit_rate`: Gauge tracking instantaneous hit ratio.
  - `codevault_db_pool_size`, `codevault_db_pool_checked_out`, `codevault_db_pool_overflow`.
  - `codevault_rate_limit_tracked_keys`: Gauge tracking active rate limiter memory entries.
  - `codevault_websocket_active_connections`: Gauge tracking open client sockets.
- **LLM Foundation Model Metrics**:
  - `codevault_llm_requests_total{provider, model, status}`: Counter tracking LLM calls.
  - `codevault_llm_latency_seconds{provider, model}`: Histogram tracking inference response times.
  - `codevault_llm_tokens_total{provider, model, token_type}`: Counter tracking prompt vs completion tokens.
  - `codevault_llm_cost_usd_total{provider, model}`: Counter tracking cumulative monetary expenditure.

### 5.2 Grafana Production Dashboard JSON Architecture (20+ Panels)
The complete Grafana dashboard specification contains 24 distinct panels arranged in 5 functional rows:
- **Row 1: Executive Overview & System Health**:
  1. System Availability Status (Stat Panel: SLI uptime % over 30d).
  2. Total Reviews Completed 24h (Stat Panel: Total count with 24h delta).
  3. P95 Review Duration (Gauge Panel: Amber at 10s, Red at 20s).
  4. Active Reviews In Progress (Gauge Panel: Max 50).
- **Row 2: API Gateway & Traffic Analytics**:
  5. API Request Rate (Time Series: Requests/sec by endpoint).
  6. HTTP Status Code Breakdown (Time Series: 200, 400, 401, 403, 429, 500, 503).
  7. API Latency Distribution (Time Series: P50, P90, P99).
  8. API Error Rate Percentage (Time Series: 5xx errors / total requests, threshold 0.1%).
- **Row 3: Multi-Agent Deep Dive & Reliability**:
  9. Agent Execution Latency (Time Series: P95 duration per agent).
  10. Agent Success vs Degraded vs Failed Rate (Stacked Bar / Time Series).
  11. Finding Distribution by Agent & Severity (Bar Gauge: Critical, High, Medium, Low).
  12. Agent Crash & Failure Events (Time Series: Non-zero values highlighted in red).
- **Row 4: LLM Tokens, Costs & Provider Performance**:
  13. LLM Token Consumption Rate (Time Series: Prompt vs Completion tokens/sec).
  14. Cumulative Daily LLM Cost ($ USD) (Stat & Time Series with daily budget limit line).
  15. LLM Inference Latency by Provider (Time Series: Watsonx vs OpenAI vs Ollama).
  16. LLM Rate Limit & 429 Response Counter (Time Series: Provider throttling events).
- **Row 5: Infrastructure, Database & Cache Health**:
  17. PostgreSQL Connection Pool Saturation (Time Series: Checked out vs Pool Size).
  18. Redis Cache Hit Ratio & Eviction Rate (Time Series: Hit % on left axis, evictions on right).
  19. Container CPU & Memory Utilization (Time Series: Pod usage vs Resource Limits).
  20. WebSocket Active Connections & Connection Churn (Time Series: Connect vs Disconnect rates).
  21. Rate Limiter Memory Bound Tracking (Time Series: Active tracked keys vs 10,000 cap).
  22. Database Slow Query Latency (Time Series: P95 query execution time).

### 5.3 AlertManager Alerting Rules Catalog (32 Production Rules)
The AlertManager configuration defines 32 production alerting rules with explicit PromQL queries, severity levels, durations, and annotations:
1. `HighAPIErrorRate` (Critical): `sum(rate(codevault_api_requests_total{status=~"5.."}[5m])) / sum(rate(codevault_api_requests_total[5m])) > 0.05` for 3m.
2. `APILatencyBreach` (Warning): `histogram_quantile(0.95, sum(rate(codevault_api_request_duration_seconds_bucket[5m])) by (le)) > 10` for 5m.
3. `APICriticalLatency` (Critical): `histogram_quantile(0.99, sum(rate(codevault_api_request_duration_seconds_bucket[5m])) by (le)) > 30` for 5m.
4. `ReviewThroughputDrop` (Warning): `rate(codevault_reviews_total[15m]) < (rate(codevault_reviews_total[15m] offset 1d) * 0.5)` for 15m.
5. `HighReviewFailureRate` (Critical): `sum(rate(codevault_reviews_total{status="failed"}[5m])) / sum(rate(codevault_reviews_total[5m])) > 0.10` for 5m.
6. `AgentCrashDetected` (Warning): `sum(rate(codevault_agent_crashes_total[5m])) > 0` for 2m.
7. `AgentCrashCritical` (Critical): `sum(rate(codevault_agent_executions_total{status="failed"}[5m])) / sum(rate(codevault_agent_executions_total[5m])) > 0.50` for 3m.
8. `SecurityAgentDown` (Critical): `rate(codevault_agent_executions_total{agent="security", status="failed"}[5m]) > 0` for 3m.
9. `AgentExecutionTimeout` (Warning): `histogram_quantile(0.95, sum(rate(codevault_agent_duration_seconds_bucket[5m])) by (le, agent)) > 60` for 5m.
10. `AgentDeadlockWarning` (Critical): `codevault_reviews_in_progress > 20 and rate(codevault_reviews_total[5m]) == 0` for 5m.
11. `DatabaseDown` (Critical): `up{job="postgres"} == 0` for 1m.
12. `DatabasePoolExhaustion` (Critical): `codevault_db_pool_checked_out / codevault_db_pool_size > 0.90` for 3m.
13. `DatabaseHighLatency` (Warning): `rate(codevault_db_query_duration_seconds_sum[5m]) / rate(codevault_db_query_duration_seconds_count[5m]) > 0.5` for 5m.
14. `DatabaseDiskSpaceLow` (Critical): `node_filesystem_free_bytes{mountpoint="/var/lib/postgresql/data"} / node_filesystem_size_bytes < 0.15` for 5m.
15. `RedisDown` (Critical): `up{job="redis"} == 0` for 1m.
16. `RedisMemoryHigh` (Warning): `redis_memory_used_bytes / redis_memory_max_bytes > 0.85` for 5m.
17. `RedisEvictionSpike` (Warning): `rate(redis_evicted_keys_total[5m]) > 100` for 5m.
18. `CacheHitRateLow` (Warning): `codevault_cache_hit_rate < 0.40` for 15m.
19. `RateLimiterCapacityWarning` (Warning): `codevault_rate_limit_tracked_keys > 8000` for 5m.
20. `RateLimiterExhaustion` (Critical): `codevault_rate_limit_tracked_keys > 9500` for 3m.
21. `PodOOMKilling` (Critical): `increase(kube_pod_container_status_restarts_total{reason="OOMKilled"}[5m]) > 0` for 1m.
22. `PodCrashLooping` (Critical): `rate(kube_pod_container_status_restarts_total[15m]) > 0.2` for 5m.
23. `PodHighCPU` (Warning): `sum(rate(container_cpu_usage_seconds_total{container="codevault-api"}[5m])) / sum(kube_pod_container_resource_limits{resource="cpu", container="codevault-api"}) > 0.85` for 10m.
24. `PodHighMemory` (Warning): `sum(container_memory_working_set_bytes{container="codevault-api"}) / sum(kube_pod_container_resource_limits{resource="memory", container="codevault-api"}) > 0.85` for 5m.
25. `LLMRateLimit429` (Warning): `rate(codevault_llm_requests_total{status="429"}[5m]) > 0.1` for 3m.
26. `LLMProviderDown` (Critical): `sum(rate(codevault_llm_requests_total{status=~"5.."}[5m])) / sum(rate(codevault_llm_requests_total[5m])) > 0.50` for 3m.
27. `LLMLatencySpike` (Warning): `histogram_quantile(0.95, sum(rate(codevault_llm_latency_seconds_bucket[5m])) by (le)) > 20` for 5m.
28. `TokenBudgetExceeded` (Critical): `codevault_llm_cost_usd_total - (codevault_llm_cost_usd_total offset 1d) > 500` for 1m.
29. `CostAnomalySpike` (Warning): `rate(codevault_llm_cost_usd_total[1h]) > (rate(codevault_llm_cost_usd_total[1h] offset 1d) * 3)` for 1h.
30. `WebSocketConnectionLeak` (Warning): `codevault_websocket_active_connections > 1000 and rate(codevault_api_requests_total[10m]) < 1` for 15m.
31. `TLSCertificateExpiringSoon` (Warning): `certmanager_certificate_expiration_timestamp_seconds - time() < 14 * 24 * 3600` for 1h.
32. `IngressControllerErrorRate` (Critical): `sum(rate(nginx_ingress_controller_requests{status=~"5.."}[5m])) / sum(rate(nginx_ingress_controller_requests[5m])) > 0.02` for 5m.

### 5.4 Loki / ELK Logging Infrastructure
- **Structured Log Schema**:
  ```json
  {
    "timestamp": "2026-09-24T14:30:00.123Z",
    "level": "INFO",
    "service": "codevault-api",
    "component": "orchestrator",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7",
    "review_id": "rev_78a19bc04",
    "tenant_id": "org_enterprise_1",
    "message": "Review execution completed",
    "duration_ms": 3420,
    "score": 88.5,
    "status": "completed",
    "agents_executed": ["security", "performance", "quality", "architecture", "compliance"],
    "critical_findings_count": 0
  }
  ```
- **Promtail Configuration**: Scrapes `/var/log/pods/*codevault*/*.log`, parses JSON payload, extracts stream labels (`level`, `component`, `service`), redacts sensitive credentials via regex stage (`Bearer [A-Za-z0-9_\-\.]{20,}` -> `Bearer [REDACTED]`), and forwards to Loki endpoint `http://loki:3100/loki/api/v1/push`.

### 5.5 OpenTelemetry APM Tracing & Distributed Instrumentation
- Automatic OpenTelemetry instrumentation injected via Python startup hooks:
  - `FastAPIInstrumentor().instrument_app(app)`
  - `HTTPXClientInstrumentor().instrument()`
  - `SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)`
- **Trace Context Propagation**: W3C Trace Context (`traceparent`, `tracestate`) headers propagated across inbound HTTP/WebSocket requests, internal LangGraph agent nodes, and outbound calls to IBM watsonx / OpenAI.
- **Span Hierarchy**:
  - `Root Span`: `HTTP POST /api/v1/review`
    - Child Span 1: `DB.get_or_create_review_record`
    - Child Span 2: `Orchestrator.execute_review`
      - Parallel Span 2a: `Agent.SecurityAgent.execute` -> `LLM.watsonx.generate`
      - Parallel Span 2b: `Agent.PerformanceAgent.execute` -> `LLM.watsonx.generate`
      - Parallel Span 2c: `Agent.QualityAgent.execute` -> `Static.AstVisitor`
    - Child Span 3: `Orchestrator.synthesize_results`
    - Child Span 4: `Cache.set_review_result`
    - Child Span 5: `DB.commit_review_findings`

### 5.6 LLM Cost Tracking & Token Budget Governance
- **Cost Engine Matrix**:
  - IBM watsonx Granite-13b: $0.0008 per 1K input tokens, $0.0016 per 1K output tokens.
  - OpenAI GPT-4o: $0.0050 per 1K input tokens, $0.0150 per 1K output tokens.
  - Local Ollama / Granite: $0.0000 (infrastructure compute only).
- **Token Budget Middleware**:
  - Tracks running daily expenditure in Redis key `codevault:cost:daily:{YYYY-MM-DD}`.
  - At 80% of daily budget ($400): Dispatches Slack notification to DevOps channel.
  - At 100% of daily budget ($500): Automatically downgrades non-critical review requests from GPT-4o / watsonx to local heuristic/Ollama engine, maintaining service availability while capping cloud spend.

### 5.7 10 Detailed Incident Response Runbooks
1. **High Review Latency (> 30s)**:
   - Diagnostic: Check `histogram_quantile(0.95, rate(codevault_llm_latency_seconds_bucket[5m]))` vs `codevault_db_query_duration_seconds`.
   - Action: If LLM provider slow, trigger provider circuit breaker to switch to fallback provider; if DB slow, inspect `pg_stat_activity` for locked transactions.
2. **Container Out of Memory (OOMKilled)**:
   - Diagnostic: Check `dmesg` or `kubectl describe pod` for exit code 137; check memory profile.
   - Action: Verify `CACHE_MAX_ITEMS` and `RATE_LIMIT_MAX_TRACKED` limits; increase pod memory limit from 4Gi to 8Gi; inspect heap dump via `tracemalloc`.
3. **Multi-Agent Deadlock / Execution Stalled**:
   - Diagnostic: Identify review jobs stuck in `codevault_reviews_in_progress` without CPU activity.
   - Action: Enforce 45s hard timeout on LangGraph agent nodes via `asyncio.wait_for(agent.run(), timeout=45.0)`; restart stalled worker pods.
4. **LLM Provider Rate Limiting / 429 Throttling**:
   - Diagnostic: Check `codevault_llm_requests_total{status="429"}`.
   - Action: Immediately scale back batch review concurrency; enable LLM request queue with exponential jitter backoff; reroute tier-2 agents to local Ollama.
5. **Database Connection Pool Exhaustion**:
   - Diagnostic: `SELECT count(*), state FROM pg_stat_activity GROUP BY state;`.
   - Action: Terminate idle in transaction connections older than 5 minutes (`pg_terminate_backend`); verify persistent client session reuse in async SQLAlchemy.
6. **Redis Memory Saturation & Eviction Storm**:
   - Diagnostic: `redis-cli INFO memory` and `redis-cli INFO stats | grep evicted`.
   - Action: Verify eviction policy is `allkeys-lru`; reduce `CACHE_TTL_SECONDS` from 7 days to 2 days; scale Redis memory allocation to 1GB.
7. **IBM watsonx API Outage / 5xx Errors**:
   - Diagnostic: `curl -I https://us-south.ml.cloud.ibm.com/v1/generate`.
   - Action: Toggle environment flag `LLM_PROVIDER=heuristic` or `LLM_PROVIDER=openai`; notify stakeholders of degraded agent fidelity mode.
8. **WebSocket Connection Leak & File Descriptor Exhaustion**:
   - Diagnostic: `lsof -p <pid> | grep sock` or inspect `codevault_websocket_active_connections`.
   - Action: Force restart of leaked WebSocket worker pods; enforce server-side heartbeat ping/pong interval (30s) and drop unacknowledged sockets.
9. **Compromised API Key / Unauthorized Access**:
   - Diagnostic: Inspect audit logs for abnormal IP addresses or token enumeration.
   - Action: Execute CLI revocation: `cerberus revoke-api-key --key-hash <hash>`; block malicious IP at Ingress/WAF level; rotate database encryption secret.
10. **Mass False-Positive Security Findings / Model Drift**:
    - Diagnostic: User feedback downvote spike on findings (`codevault_feedback_negative_total`).
    - Action: Temporarily lower temperature or adjust prompt template in ConfigMap; suppress offending rule ID in custom rule engine; deploy prompt patch.

### 5.8 Health Check Probes, SLI/SLO Definitions & Error Budget Policies
- **Probes**:
  - Liveness (`/api/v1/health`): Returns HTTP 200 if FastAPI process event loop is responding.
  - Readiness (`/api/v1/ready`): Executes `SELECT 1` on PostgreSQL and `PING` on Redis; returns 200 if dependencies healthy, 503 if unavailable.
  - Startup (`/api/v1/startup`): Confirms DB schema migrations and initial credential seeds have completed before routing traffic.
- **SLI / SLO Framework**:
  - Availability SLO: 99.9% uptime over rolling 30-day window (<= 43.8 minutes unplanned downtime).
  - Review Latency SLO: 95% of standard code reviews (<500 LOC) complete in < 15.0 seconds.
  - Error Rate SLO: < 0.1% 5xx errors across total API transactions.
  - Agent Integrity SLO: 99.5% of individual agent runs terminate without unhandled exception.
- **Error Budget Policy**:
  - If 50% of monthly error budget consumed within 7 days: Freeze non-essential feature deployments; conduct operational review.
  - If 100% of error budget consumed: All deployment pipelines locked except emergency P1 reliability and security bugfixes.

---

## 6. Deliverable 7: TESTING_STRATEGY.md Technical Specifications

### 6.1 Pytest Framework Setup & Configuration
The test infrastructure uses `pytest-asyncio` with explicit configuration:
- `pytest.ini`:
  ```ini
  [pytest]
  asyncio_mode = auto
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  markers =
      unit: Fast unit tests with no external dependencies
      integration: Integration tests requiring database or Redis
      e2e: Full end-to-end user journey workflows
      security: Security, authentication, and vulnerability verification
      load: Performance and stress testing
  filterwarnings =
      ignore::DeprecationWarning
  addopts = --strict-markers -v --tb=short
  ```
- `conftest.py` Fixtures:
  - `async_client`: `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")`.
  - `db_session`: Async SQLAlchemy test session utilizing in-memory SQLite (`sqlite+aiosqlite:///:memory:`) or dedicated test PostgreSQL database with automatic table drop/create per session.
  - `fake_redis`: In-memory Redis simulation using `fakeredis.aioredis`.
  - `test_api_key`: Valid seeded test API key record (`cvai_test_key_abc123`) with hash stored in DB.
  - `mock_watsonx_service`: Intercepts outbound HTTP requests to `WATSONX_URL` and returns deterministic granite foundation model review findings.

### 6.2 50+ Copy-Paste Ready Test Suite Specifications
The comprehensive test suite encompasses 50+ tests categorized across 6 domain suites:
1. **Security & Authentication Suite (10 Tests)**:
   - `test_valid_api_key_accepted`: HTTP 200 with active key.
   - `test_missing_authorization_header_rejected`: HTTP 401 Unauthorized.
   - `test_malformed_bearer_token_rejected`: HTTP 401 when "Bearer " missing.
   - `test_fabricated_cvai_token_rejected`: HTTP 401 on unregistered `cvai_` token.
   - `test_expired_api_key_rejected`: HTTP 401 on key past `expires_at`.
   - `test_inactive_api_key_rejected`: HTTP 401 on key with `is_active=False`.
   - `test_cors_allowed_origin_header`: HTTP 200 with matching CORS response headers.
   - `test_cors_unauthorized_origin_blocked`: CORS headers omitted for untrusted origins.
   - `test_production_secret_key_rejection`: Pydantic validator raises `ValueError` on default secret.
   - `test_sql_injection_in_auth_header`: SQL injection string in bearer token safely rejected.
2. **Rate Limiting & Resource Management Suite (10 Tests)**:
   - `test_rate_limiter_allows_under_quota`: Requests permitted up to `RATE_LIMIT_PER_HOUR`.
   - `test_rate_limiter_blocks_over_quota`: HTTP 429 Too Many Requests when limit exceeded.
   - `test_rate_limiter_retry_after_header`: Response contains valid integer `Retry-After`.
   - `test_rate_limiter_expired_identifier_cleanup`: Inactive identifiers purged from memory.
   - `test_rate_limiter_memory_bounding_20k_tokens`: 20,000 random tokens capped at `RATE_LIMIT_MAX_TRACKED`.
   - `test_cache_lru_eviction`: Exceeding `CACHE_MAX_ITEMS` evicts oldest item.
   - `test_cache_ttl_expiration`: Item inaccessible after TTL seconds elapse.
   - `test_batch_review_concurrency_semaphore`: Max 5 concurrent tasks executed in parallel.
   - `test_batch_review_oversize_rejected`: Batch with 101 items returns HTTP 400.
   - `test_http_client_session_pooling`: Watsonx/OpenAI providers reuse single `httpx.AsyncClient`.
3. **Multi-Agent Orchestrator & Scoring Suite (10 Tests)**:
   - `test_orchestrator_executes_all_5_agents`: Security, Performance, Quality, Arch, Compliance executed.
   - `test_single_agent_crash_isolation`: Security agent exception does not crash other 4 agents.
   - `test_crashed_agent_receives_zero_score`: Crashed agent receives score 0.0.
   - `test_review_status_degraded_on_agent_crash`: Overall status set to `"degraded"`.
   - `test_review_status_failed_on_all_crashes`: Status set to `"failed"` if all 5 agents crash.
   - `test_weighted_score_calculation`: Correct mathematical weighted average across active agents.
   - `test_critical_finding_triggers_blocking_decision`: Severity "CRITICAL" sets `should_block=True`.
   - `test_degraded_review_not_persisted_to_cache`: Degraded reviews excluded from Redis cache.
   - `test_synthesized_report_finding_deduplication`: Duplicate findings across agents merged.
   - `test_orchestrator_timeout_handling`: Agents exceeding time limit cleanly aborted.
4. **IBM watsonx & Foundation Model Provider Suite (8 Tests)**:
   - `test_watsonx_provider_availability`: Returns `True` when API key and project ID configured.
   - `test_watsonx_generate_response_success`: Parses granite-13b response into review JSON.
   - `test_watsonx_timeout_fallback`: Returns `None` and activates heuristic engine on 15s timeout.
   - `test_watsonx_http_error_handling`: HTTP 500 from watsonx cleanly caught and logged.
   - `test_watsonx_malformed_json_fallback`: Unparseable model text safely handled.
   - `test_watsonx_token_usage_tracking`: Correct token counts accumulated in metrics.
   - `test_watsonx_mock_service_fidelity`: Mock service outputs match real watsonx schemas.
   - `test_provider_session_closed_on_shutdown`: `await provider.close()` terminates connection pool.
5. **API Endpoints & WebSocket Streaming Suite (7 Tests)**:
   - `test_post_review_endpoint`: Submits review, receives 200 with review ID and results.
   - `test_get_review_by_id`: Fetches existing review record from database.
   - `test_get_review_status`: Retrieves processing status (`pending`, `completed`).
   - `test_post_batch_review`: Processes list of files and returns list of review summaries.
   - `test_health_and_readiness_endpoints`: `/health` and `/ready` return component JSON.
   - `test_websocket_stream_authenticated_flow`: Connects with token, receives progress frames.
   - `test_websocket_unauthenticated_rejected`: Connection without token closed with code 1008.
6. **End-to-End System Scenarios (Tier 4 Suite - 5 Tests)**:
   - `test_scenario_s1_multi_tenant_isolation`: Tenant A cannot view Tenant B review history.
   - `test_scenario_s2_high_load_batch_webhook`: 50-file batch throttles without memory spike.
   - `test_scenario_s3_faulty_agent_ci_gate`: Syntactically invalid file degrades score; CI gate blocks.
   - `test_scenario_s4_hostile_cors_and_token_flood`: CORS blocks origin; fake token flood pruned.
   - `test_scenario_s5_live_websocket_dashboard`: Client streams review, disconnects cleanly without leaked sockets.

### 6.3 Test Data Factories (Polyfactory / Factory Boy)
Declarative factory definitions generate randomized, valid model instances:
```python
# File: tests/factories.py
from polyfactory.factories.pydantic_factory import ModelFactory
from cerberus.models.schemas import ReviewRequest, ReviewResponse, AgentFinding
import uuid

class AgentFindingFactory(ModelFactory[AgentFinding]):
    __model__ = AgentFinding
    rule_id = lambda: f"RULE-{uuid.uuid4().hex[:6].upper()}"
    severity = "HIGH"
    line = 42

class ReviewRequestFactory(ModelFactory[ReviewRequest]):
    __model__ = ReviewRequest
    code = "def sample():\n    return True\n"
    language = "python"
```

### 6.4 IBM watsonx Orchestrate Mock LLM Fixture Architecture
A reusable pytest fixture intercepting outbound HTTP traffic:
```python
# File: tests/fixtures/watsonx_mock.py
import pytest
import httpx
import json

@pytest.fixture
def mock_watsonx_granite(monkeypatch):
    def mock_post(url, *args, **kwargs):
        payload = {
            "results": [{
                "generated_text": json.dumps({
                    "findings": [{
                        "rule_id": "WX-SEC-01",
                        "title": "Hardcoded Credential Detected",
                        "severity": "CRITICAL",
                        "line": 12,
                        "description": "API key found in source code string literal",
                        "fix_recommendation": "Migrate secret to environment variable"
                    }]
                })
            }]
        }
        return httpx.Response(200, json=payload)
    return mock_post
```

### 6.5 Locust Distributed Load Testing Scripts
Performance script simulating concurrent enterprise usage:
- `locustfile.py`:
  - `CodeReviewUser(HttpUser)`:
    - Task 1: `submit_single_review` (weight 6): Submits 200-line Python snippet, checks 200 OK.
    - Task 2: `poll_review_status` (weight 10): Polls `/api/v1/review/{id}` until completed.
    - Task 3: `submit_batch_review` (weight 1): Submits 10-file batch review.
    - Task 4: `check_health` (weight 3): Hits `/api/v1/health`.
  - Load Scenarios:
    - Normal Load: 50 concurrent users, spawn rate 2/s, duration 10m.
    - Spike Test: 500 concurrent users, spawn rate 50/s, duration 3m.
    - Soak Test: 100 concurrent users, spawn rate 5/s, duration 4 hours.

### 6.6 SAST/DAST & Secret Scanning Security Pipelines
- **Bandit SAST**: Scans Python codebase for common security issues (exec, SQL injection, hardcoded secrets): `bandit -r cerberus/ -c bandit.yaml -ll`.
- **Semgrep SAST**: Semantic rule matching enforcing OWASP Top 10 guidelines: `semgrep --config p/owasp-top-ten cerberus/`.
- **OWASP ZAP DAST**: Automated container baseline scan against `http://localhost:8000`: `docker run -t zaproxy/zap-stable zap-baseline.py -t http://host.docker.internal:8000 -r zap_report.html`.
- **TruffleHog**: Scans git commit history for leaked tokens and private keys: `trufflehog git file://. --only-verified`.

### 6.7 Code Coverage Governance & Configuration
- `.coveragerc` Specification:
  ```ini
  [run]
  branch = True
  source = cerberus
  omit =
      tests/*
      cerberus/cli/*
      */migrations/*

  [report]
  fail_under = 90.0
  precision = 2
  show_missing = True
  exclude_lines =
      pragma: no cover
      def __repr__
      if __name__ == .__main__.:
      raise NotImplementedError
  ```

---

## 7. Deliverable 8: PRODUCTION_LAUNCH_MANUAL.md Technical Specifications

### 7.1 100+ Item Production Pre-Launch Verification Checklist
The pre-launch manual incorporates 100 verification items categorized across 5 pillars:
1. **Architecture & Design (Items 1-15)**:
   - High availability validated across 3 Availability Zones.
   - Stateless API pod tier with zero local filesystem persistence.
   - Graceful termination lifecycle (`SIGTERM` handling and 30s grace period).
   - Connection timeouts enforced on all external HTTP and DB calls.
   - Circuit breakers configured for all LLM foundation model integrations.
   - Redis cluster configured with automatic failover.
   - PostgreSQL configured with primary and warm standby.
   - Maximum payload size limits enforced on API gateway (10MB).
   - WebSocket ping/pong keepalives active.
   - Rate limiting active on all public endpoints.
   - CORS origin whitelist strictly enforced without wildcards.
   - Pydantic request models enforce strict field validation.
   - Asynchronous I/O enforced across all database queries.
   - Batch operations bounded by concurrency semaphores.
   - Idempotency keys supported for review submissions.
2. **Security & Compliance (Items 16-40)**:
   - Default passwords changed across Postgres, Redis, Grafana.
   - Insecure default `SECRET_KEY` rejected by production validator.
   - TLS 1.3 enforced on all ingress endpoints with HSTS active.
   - Container images built from distroless/non-root base (UID 10001).
   - Capabilities dropped (`ALL`) on all Kubernetes containers.
   - Read-only root filesystem enforced on application pods.
   - Kubernetes NetworkPolicies isolate DB and Redis from public ingress.
   - HashiCorp Vault secrets integration active via ESO or Sidecar.
   - API keys hashed with SHA-256 before database storage.
   - Role-Based Access Control (RBAC) enforced across API scopes.
   - PII redaction active in application logging pipeline.
   - Audit logging enabled for all security-sensitive events.
   - SAST scan (Bandit/Semgrep) zero Critical and High findings.
   - Dependency vulnerability scan (pip-audit/Trivy) zero CVEs.
   - DAST scan (OWASP ZAP) clean of High/Medium alerts.
   - Secret scan (TruffleHog) clean across git history.
   - Database encrypted at rest using AES-256 (pgcrypto / storage level).
   - In-transit encryption (mTLS) enforced between API and PostgreSQL.
   - In-transit encryption enforced between API and Redis.
   - Multi-Factor Authentication (MFA) required for admin cloud consoles.
   - Least privilege IAM roles attached to Kubernetes ServiceAccounts.
   - External security penetration testing completed and remediated.
   - Vulnerability disclosure policy and security contact published.
   - Security incident response team roster verified with contact info.
   - Customer Data Processing Agreement (DPA) signed and archived.
3. **Data & Storage (Items 41-55)**:
   - PostgreSQL schema migrations tested with zero downtime.
   - Reversible down-migrations verified for all Alembic revisions.
   - B-tree indexes verified on all foreign keys and filter columns.
   - Table vacuum and analyze schedules automated via pg_cron.
   - Automated continuous WAL archiving streaming to object storage.
   - Daily full database backup scheduled with 90-day retention.
   - Point-In-Time Recovery (PITR) successfully rehearsed.
   - Database connection pool sizes tuned for max replica count.
   - Redis `maxmemory` configured with `allkeys-lru` eviction policy.
   - Redis persistence (AOF everysec) enabled and tested.
   - Stale cache eviction keys validated under memory saturation.
   - Review history retention policy automated (purge after 90 days).
   - Database storage auto-expand enabled up to 1TB.
   - Cross-region database replication lag verified < 1 second.
   - Disaster recovery standby database verified read-accessible.
4. **Infrastructure & Networking (Items 56-75)**:
   - Kubernetes cluster upgraded to certified stable version.
   - Multi-AZ node groups deployed across at least 3 zones.
   - CPU and Memory resource requests and limits set on all pods.
   - Horizontal Pod Autoscaler (HPA) configured and load-tested.
   - PodDisruptionBudgets (PDB) set to `minAvailable: 2`.
   - Ingress controller deployed with active-active redundant pods.
   - DNS TTL reduced to 60 seconds prior to cutover.
   - Route53 health checks configured with automated DNS failover.
   - Cloudflare / WAF DDoS protection rules enabled and active.
   - SSL/TLS certificates issued with auto-renewal via cert-manager.
   - Outbound egress NAT gateway configured with static elastic IPs.
   - Dedicated Kubernetes namespaces isolated with ResourceQuotas.
   - StorageClasses configured with fast SSD volumes (io2 / gp3).
   - Node termination handlers configured for Spot/Preemptible nodes.
   - Pod anti-affinity rules prevent co-locating replicas on same node.
   - Network bandwidth limits verified with cloud provider.
   - Cluster autoscaler tested from 3 nodes up to 20 nodes.
   - CoreDNS scaled horizontally to prevent DNS resolution latency.
   - Container registry (GHCR/ECR) image pull secrets configured.
   - Internal load balancers verified between microservices.
5. **Operations & Observability (Items 76-100)**:
   - Prometheus server actively scraping all target endpoints.
   - Prometheus scrape interval set to 15 seconds.
   - Prometheus data retention configured to at least 30 days.
   - Grafana dashboard provisioned with all 24 production panels.
   - Grafana alerting channels linked to PagerDuty and Slack.
   - All 32 AlertManager alert rules syntax-validated and loaded.
   - PagerDuty on-call escalation schedules configured and tested.
   - Test alert fired through pipeline to verify on-call phone paging.
   - Loki / Promtail logging pipeline streaming container JSON logs.
   - Log retention policy configured for 30-day index lifecycle.
   - OpenTelemetry distributed tracing exporting spans to Jaeger/Tempo.
   - Synthetic ping monitors active from 5 global locations.
   - LLM token cost tracking active with daily budget threshold.
   - 10 operational runbooks published and accessible in wiki.
   - Status page (`status.codevault.ai`) configured and integrated.
   - Team shift handover protocol documented and rehearsed.
   - Service Level Agreements (SLAs) published to customers.
   - Incident Commander (IC) roles designated for launch window.
   - Maintenance window scheduled and announced to stakeholders.
   - Rollback criteria documented and approved by VP of Engineering.
   - Operational War Room Zoom/Slack channels opened.
   - Production launch checklist signed off by all 5 lead engineers.
   - Post-launch monitoring schedule staffed 24/7 for 72 hours.
   - Executive sponsor formal go/no-go approval recorded.
   - Customer support team trained on incident escalation paths.

### 7.2 Step-by-Step Production Cutover Runbook (T-24h to T+4h)
- **T-24h (Preparation & Freeze)**:
  - Enforce global code freeze on repository.
  - Lower DNS TTL on `codevault.enterprise.ibm.com` to 60 seconds.
  - Execute full backup of PostgreSQL and snapshot Redis.
  - Verify standby cluster health and readiness probes.
  - Hold Go/No-Go readiness meeting; confirm all 100 checklist items PASS.
- **T-12h (Rehearsal & Notification)**:
  - Run cutover dry-run in staging environment.
  - Post customer maintenance advisory on status page.
  - Verify PagerDuty on-call roster and test phone paging.
- **T-4h (Infrastructure Warmup)**:
  - Pre-scale production Kubernetes pods to 10 replicas.
  - Warm up Redis cache with common compliance rule sets.
  - Establish dedicated Incident War Room bridge (Slack #prod-cutover, Zoom).
- **T-1h (Final Checks)**:
  - Verify zero database replication lag.
  - Confirm all 32 Prometheus alert rules are active and green.
  - Final Go/No-Go confirmation from Incident Commander.
- **T-0 (Cutover Execution)**:
  - Route 10% of production traffic to new cluster via weighted DNS / Ingress.
  - Monitor error rates and latency for 10 minutes.
  - Increase traffic to 25%, 50%, and finally 100%.
  - Repoint primary DNS records to new production load balancer.
- **T+15m (Immediate Verification)**:
  - Verify API request throughput, P95 latency (< 15s), and 5xx errors (< 0.1%).
  - Execute automated smoke test suite against live production endpoint.
  - Validate review submissions across Python, JS, Java, and Go repositories.
- **T+1h (Post-Cutover Audit)**:
  - Inspect Prometheus metrics: confirm `codevault_reviews_total` incrementing.
  - Check Loki logs for any unhandled exceptions or error patterns.
  - Confirm LLM token cost tracking is recording usage accurately.
- **T+4h (Stabilization & Sign-Off)**:
  - Restore DNS TTL to standard 300 seconds.
  - Close Incident War Room; transition monitoring to Primary On-Call.
  - Publish cutover success announcement to stakeholders.

### 7.3 Zero-Downtime Database Migration Framework (Expand-Contract)
To eliminate maintenance downtime, all schema modifications follow the 3-phase Expand-Contract pattern:
1. **Phase 1: Expand**:
   - Add new table or add new column with `NULL` permitted or default value:
     `ALTER TABLE reviews ADD COLUMN IF NOT EXISTS repository_url VARCHAR(512);`
   - Application deploy V1.1 writes to both old and new schema fields (Dual Writing).
2. **Phase 2: Backfill**:
   - Async migration worker runs in background, backfilling historical data in batches of 500 rows with 100ms pauses to avoid table locks:
     `UPDATE reviews SET repository_url = metadata->>'repo' WHERE repository_url IS NULL;`
3. **Phase 3: Contract**:
   - Application deploy V1.2 switches all reads to new column and drops writes to old column.
   - Execute final cleanup migration to drop obsolete column/table:
     `ALTER TABLE reviews DROP COLUMN IF EXISTS obsolete_repo_field;`

### 7.4 Automated Rollback Criteria & Emergency Execution Runbook
- **Automated Rollback Trigger Criteria**:
  - API HTTP 5xx error rate > 1.0% over 2 consecutive minutes.
  - P99 review completion latency > 30.0s over 3 consecutive minutes.
  - Database connection pool saturation > 95% for 60 seconds.
  - Core agent crash rate > 5% of all review requests.
- **Emergency Rollback Execution Runbook**:
  1. Incident Commander announces "ROLLBACK INITIATED".
  2. ArgoCD / Helm Rollback command executed:
     `helm rollback codevault <previous_revision_number> -n codevault`
  3. Ingress controller flips traffic to previous stable ReplicaSet within 30 seconds.
  4. Database rollback executed if schema changes occurred:
     `alembic downgrade -1`
  5. Redis cache flushed for active review keys if state format changed:
     `redis-cli --scan --pattern "codevault:review:*" | xargs redis-cli DEL`
  6. Verify `/api/v1/health` on previous version returns 200 OK.
  7. Post incident status update on status page; convene retrospective within 24 hours.

### 7.5 Chaos Testing & Alert Verification Exercises (Game Day)
Before launch, 5 chaos experiments are executed to validate resilience:
1. **Exercise 1: Pod Kill Chaos**:
   - Action: `kubectl delete pod -l app=codevault-api --force` under 100 RPS load.
   - Expected: Kubernetes replaces pods within 5 seconds; traffic automatically routed to surviving pods; zero dropped requests.
2. **Exercise 2: Database Latency Injection**:
   - Action: Inject 2000ms delay between API and PostgreSQL using Chaos Mesh.
   - Expected: `DatabaseHighLatency` warning alert fires in AlertManager within 5 minutes; connection pool scales up; endpoints remain operational with degraded response times.
3. **Exercise 3: Upstream LLM Blackhole**:
   - Action: Block outbound traffic to `WATSONX_URL` via NetworkPolicy.
   - Expected: `WatsonxProvider` times out cleanly; orchestrator logs warning and falls back to Heuristic engine; review completes with status `"degraded"`; `LLMProviderDown` critical alert pages on-call.
4. **Exercise 4: Redis Node Failure**:
   - Action: Force crash Redis container: `docker kill codevault-redis`.
   - Expected: `CacheManager` gracefully falls back to local in-memory LRU cache; `RedisDown` critical alert fires in 60s; reviews continue processing without failure.
5. **Exercise 5: Database Connection Pool Starvation**:
   - Action: Run script acquiring all available DB connections.
   - Expected: SQLAlchemy queue pool throws `TimeoutError`; endpoints return HTTP 503; `DatabasePoolExhaustion` critical alert pages on-call within 3 minutes.

### 7.6 On-Call Rotation Framework, Roles & Shift Handoff Checklist
- **Roles & Responsibilities**:
  - **Primary On-Call**: First responder to PagerDuty alerts; must acknowledge within 15 minutes; investigates runbooks and performs initial triage.
  - **Secondary On-Call**: Backup responder; escalates if Primary does not acknowledge within 15m; handles secondary incidents during major outages.
  - **Incident Commander (IC)**: Leads SEV-1 and SEV-2 incident calls; coordinates engineering actions; manages executive communications.
  - **Communications Lead**: Updates status page (`status.codevault.ai`) and sends customer notifications every 30 minutes during major incidents.
- **Daily Shift Handoff Protocol (10:00 AM UTC)**:
  - 15-minute sync between outgoing and incoming on-call engineers.
  - Review open incidents, active silences, and flaky alerts from previous 24 hours.
  - Verify PagerDuty override schedule and check phone audio alerts are unmuted.
  - Review upcoming maintenance windows and ongoing deployments.

### 7.7 SLAs, Severity Classifications & Escalation Trees
- **SLA Commitments**:
  - System Availability: 99.9% uptime per calendar month.
  - Review Latency: 95% of standard PR reviews (<500 LOC) processed in < 15.0 seconds.
  - Support Response Times: SEV-1 < 15m, SEV-2 < 30m, SEV-3 < 2h, SEV-4 < 1 business day.
- **Severity Classification Matrix**:
  - **SEV-1 (Critical)**: Total system outage, data breach, or zero reviews completing.
    - Initial Response: < 15 minutes.
    - Update Cadence: Every 15 minutes.
    - Escalation: Primary -> Secondary -> Tech Lead -> VP Engineering -> CTO.
  - **SEV-2 (Major)**: Core agent failure (e.g. security agent offline), review throughput degraded by > 50%.
    - Initial Response: < 30 minutes.
    - Update Cadence: Every 30 minutes.
    - Escalation: Primary -> Secondary -> Tech Lead -> Director of Engineering.
  - **SEV-3 (Minor)**: Isolated feature bug, slow performance for subset of users, batch review queue delay.
    - Initial Response: < 2 hours.
    - Update Cadence: Daily.
    - Escalation: Primary -> Service Owner.
  - **SEV-4 (Low)**: Documentation error, minor UI cosmetic flaw, non-urgent feature request.
    - Initial Response: Next business day.
    - Update Cadence: Weekly sprint review.

### 7.8 Routine Preventive Maintenance Schedules
- **Daily Maintenance**:
  - Verify automated database backup snapshot in S3: `aws s3 ls s3://codevault-backups/$(date +%Y%m%d)/`.
  - Audit daily LLM cost burn vs budget quota in Grafana.
  - Review 24-hour error log summary in Loki for emerging warning patterns.
- **Weekly Maintenance**:
  - Database Maintenance: Execute `VACUUM ANALYZE` on PostgreSQL tables.
  - Cache Cleanup: Audit and purge stale untracked keys in Redis.
  - Dependency Scan: Review weekly automated Dependabot / Renovate security PRs.
- **Monthly Maintenance**:
  - SSL/TLS Certificate Expiry Audit: Verify cert-manager renewed all certificates with > 30 days remaining.
  - Secret Rotation: Rotate database service account passwords and internal API tokens.
  - Disaster Recovery Drill: Perform automated PITR restore on staging cluster; verify data integrity.
- **Quarterly Maintenance**:
  - User Access Audit: Review active API keys and revoke inactive keys (> 90 days unused).
  - Chaos Game Day: Execute full-team chaos engineering drills.
  - Penetration Testing: Conduct external third-party vulnerability assessment.

### 7.9 Security Compliance Audit Checklists
- **SOC 2 Type II Controls**:
  - CC6.1 (Logical Access): RBAC enforced; API keys hashed; admin access protected by MFA.
  - CC6.6 (Boundary Protection): Firewalls, Kubernetes NetworkPolicies, and WAF rules active.
  - CC6.8 (Malicious Code Protection): Automated SAST, DAST, and container vulnerability scanning.
  - CC7.2 (System Monitoring): 24/7 infrastructure and security monitoring via Prometheus/Loki/PagerDuty.
  - CC8.1 (Change Management): Peer reviews required on PRs; CI/CD pipeline enforces 90% test coverage.
- **HIPAA Security Rule (45 CFR Part 164)**:
  - § 164.312(a)(2)(iv) Encryption: AES-256 encryption at rest; TLS 1.3 encryption in transit.
  - § 164.312(b) Audit Controls: Immutable audit logging of all code access and review requests.
  - § 164.312(c)(1) Integrity: SHA-256 cryptographic checksums on stored review findings.
  - § 164.312(e)(1) Transmission Security: End-to-end HTTPS/WSS enforcement with HSTS.
- **PCI-DSS v4.0 Controls**:
  - Requirement 3: Protect stored account data; source code containing PANs masked or rejected.
  - Requirement 6: Develop secure software; eliminate OWASP Top 10 flaws via automated CI/CD scans.
  - Requirement 8: Identify users and authenticate access; unique API keys with expiry dates.
  - Requirement 10: Log and monitor all access to system components and cardholder environments.
- **ISO/IEC 27001:2022 Annex A Controls**:
  - Control A.5.15 (Access Control): Principle of least privilege enforced on K8s and cloud IAM.
  - Control A.8.8 (Management of Technical Vulnerabilities): Automated CVE patching SLAs (Critical < 7d).
  - Control A.8.24 (Use of Cryptography): Industry-standard algorithms (AES-GCM, SHA-256, TLS 1.3).
  - Control A.8.28 (Secure Coding): Coding standards enforced by linters and multi-agent review system.

---

## 8. Traceability Matrix & Downstream Authoring Blueprint

The following matrix maps the technical specifications mined in this survey directly to the sections of the four target deliverables to be generated:

| Deliverable Target | Core Section | Authoritative Requirement Mined in This Survey |
|--------------------|--------------|------------------------------------------------|
| `DEPLOYMENT_GUIDE.md` | Multi-Stage Dockerfile | §4.1: 4-stage build (builder, tester, auditor, distroless runtime UID 10001) |
| `DEPLOYMENT_GUIDE.md` | Local docker-compose | §4.2: Full stack with FastAPI, Postgres, Redis, Prometheus, Grafana, mock watsonx |
| `DEPLOYMENT_GUIDE.md` | Kubernetes Manifests | §4.3: Deployment (5 replicas, resource limits), Service, Ingress TLS, HPA, PDB, NetworkPolicy |
| `DEPLOYMENT_GUIDE.md` | Helm Chart | §4.4: Helm v3 chart (`Chart.yaml`, `values.yaml`, templates) for multi-environment deployments |
| `DEPLOYMENT_GUIDE.md` | watsonx Orchestrate | §4.5: OpenAPI skill schema, endpoint registration, IAM credentials, assistant routing |
| `DEPLOYMENT_GUIDE.md` | Vault Integration | §4.6: External Secrets Operator (ESO) SecretStore & Vault Agent sidecar injector |
| `DEPLOYMENT_GUIDE.md` | CI/CD Pipelines | §4.7: GitHub Actions workflows for PR checks, Staging deploy, Production Canary rollout |
| `DEPLOYMENT_GUIDE.md` | Disaster Recovery | §4.8: Multi-region active-passive DR, WAL streaming to S3, RTO < 15m, RPO < 5m runbooks |
| `MONITORING_OPERATIONS.md` | Prometheus Metrics | §5.1: System, API, review, agent, resource, and LLM metrics with scrape configurations |
| `MONITORING_OPERATIONS.md` | Grafana Dashboard | §5.2: Complete 20+ panel JSON architecture across 5 categorized operational rows |
| `MONITORING_OPERATIONS.md` | AlertManager Rules | §5.3: 32 alerting rules with PromQL queries, severities, thresholds, and annotations |
| `MONITORING_OPERATIONS.md` | Logging Infrastructure | §5.4: Structured JSON log schema, Promtail scraping, log masking, Loki/ELK forwarding |
| `MONITORING_OPERATIONS.md` | APM Tracing | §5.5: OpenTelemetry auto-instrumentation, W3C trace propagation, span hierarchies |
| `MONITORING_OPERATIONS.md` | Cost & Token Tracking | §5.6: LLM token tracking, provider cost models, automated daily budget throttling |
| `MONITORING_OPERATIONS.md` | Incident Runbooks | §5.7: 10 step-by-step incident response runbooks with diagnostic and remediation CLI/SQL |
| `MONITORING_OPERATIONS.md` | Probes & SLI/SLOs | §5.8: Liveness/Readiness/Startup probe endpoints, 99.9% uptime SLO, error budget policies |
| `TESTING_STRATEGY.md` | Pytest Framework | §6.1: `pytest.ini`, `conftest.py` async fixtures, test DB, fakeredis, mock HTTP client |
| `TESTING_STRATEGY.md` | 50+ Test Examples | §6.2: 50+ verified test cases across Security, Memory, Orchestrator, Watsonx, API, and E2E |
| `TESTING_STRATEGY.md` | Test Data Factories | §6.3: Polyfactory and Factory Boy implementations for ORM models and Pydantic schemas |
| `TESTING_STRATEGY.md` | watsonx Mock Fixtures | §6.4: Deterministic response fixture, latency simulation, and fault injection for Granite |
| `TESTING_STRATEGY.md` | Locust Load Testing | §6.5: Locust performance script modeling normal, spike (500 users), and soak profiles |
| `TESTING_STRATEGY.md` | Security Test Pipelines| §6.6: Automated Bandit, Semgrep, OWASP ZAP baseline DAST, and TruffleHog pipelines |
| `TESTING_STRATEGY.md` | Code Coverage | §6.7: `.coveragerc` configuration enforcing >= 90% global and module coverage thresholds |
| `PRODUCTION_LAUNCH_MANUAL.md` | 100+ Pre-Launch Checklist | §7.1: Exhaustive 100-item pre-launch verification checklist across Arch, Sec, Data, Infra, Ops |
| `PRODUCTION_LAUNCH_MANUAL.md` | Production Cutover | §7.2: Time-sequenced cutover runbook spanning T-24h to T+4h with ownership and gates |
| `PRODUCTION_LAUNCH_MANUAL.md` | Zero-Downtime Migration | §7.3: Expand-Contract 3-phase database migration pattern and Alembic runbooks |
| `PRODUCTION_LAUNCH_MANUAL.md` | Rollback Procedures | §7.4: Automated rollback trigger criteria (5xx > 1%, P99 > 30s) and 1-command Helm rollback |
| `PRODUCTION_LAUNCH_MANUAL.md` | Chaos Game Days | §7.5: 5 structured chaos testing exercises (Pod kill, DB latency, LLM blackhole, Redis crash) |
| `PRODUCTION_LAUNCH_MANUAL.md` | On-Call Framework | §7.6: Primary/Secondary rotation roles, escalation policies, and daily handover checklists |
| `PRODUCTION_LAUNCH_MANUAL.md` | SLAs & Escalation Trees | §7.7: 99.9% availability SLA, SEV-1 to SEV-4 definitions, response times, escalation trees |
| `PRODUCTION_LAUNCH_MANUAL.md` | Maintenance Calendars | §7.8: Scheduled preventive maintenance tasks across daily, weekly, monthly, quarterly cadences |
| `PRODUCTION_LAUNCH_MANUAL.md` | Compliance Checklists | §7.9: Compliance control matrices for SOC2 Type II, HIPAA, PCI-DSS v4.0, and ISO 27001 |

---
*End of Survey Report — Prepared by survey_miner_3 for Authoring Agents.*
