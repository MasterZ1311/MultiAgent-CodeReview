# Handoff Report — challenger_doc5_8

**Target Documents**:
- Doc 5: `DEPLOYMENT_GUIDE.md`
- Doc 6: `MONITORING_OPERATIONS.md`
- Doc 7: `TESTING_STRATEGY.md`
- Doc 8: `PRODUCTION_LAUNCH_MANUAL.md`

**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

Direct empirical observations gathered via automated parsers, AST compilers, YAML/JSON linters, and pytest execution:

1. **Kubernetes Probe Endpoint Mismatch (HTTP 404)**:
   - In `DEPLOYMENT_GUIDE.md` (lines 590–607, `k8s/deployment.yaml`):
     ```yaml
     startupProbe:
       httpGet:
         path: /api/v1/health/startup
         port: http
     livenessProbe:
       httpGet:
         path: /api/v1/health/liveness
         port: http
     readinessProbe:
       httpGet:
         path: /api/v1/health/readiness
         port: http
     ```
   - In `cerberus/api/v1/health.py`:
     Line 18: `@router.get("/api/v1/health")`
     Line 33: `@router.get("/api/v1/ready")`
   - In `MONITORING_OPERATIONS.md` (lines 2004–2020, `cerberus/api/health.py`):
     Line 2004: `@router.get("/health")`, `@router.get("/health/live")`
     Line 2011: `@router.get("/health/ready")`
     Line 2020: `@router.get("/health/startup")`
   - Verbatim execution against `cerberus/api/app.py`:
     ```
     /api/v1/health                 -> 200
     /api/v1/ready                  -> 200
     /api/v1/health/liveness        -> 404
     /api/v1/health/readiness       -> 404
     /api/v1/health/startup         -> 404
     ```

2. **Malformed PromQL Syntax in Prometheus Alerting Rules**:
   - In `MONITORING_OPERATIONS.md` (lines 995–1002, `k8s/alerts/codevault-alerts.yaml`):
     ```yaml
     - alert: HighReviewFailureRate
       expr: sum(rate(codevault_reviews_total{status="failed"[5m]})) / sum(rate(codevault_reviews_total[5m])) > 0.10
     ```
   - Range vector duration `[5m]` is placed inside `{status="failed"[5m]}` rather than outside `{status="failed"}[5m]`.

3. **Helm Template Probe Inconsistency & Missing `startupProbe`**:
   - In `DEPLOYMENT_GUIDE.md` (lines 1150–1175, `deploy/helm/codevault/templates/deployment.yaml`):
     - Uses `path: /api/v1/ready` for readinessProbe (conflicting with `/api/v1/health/readiness` in `k8s/deployment.yaml` and `/api/v1/health/ready` in Doc 6).
     - Completely omits `startupProbe`.

4. **Universal Acceptance Criteria Conformance**:
   - Zero occurrences of `TODO`, `FIXME`, `<replace_me>`, `<replace-me>`, `REPLACE_ME` across all 4 documents.
   - All 77 code blocks across Docs 5–8 specify explicit syntax language tags (`yaml`, `json`, `python`, `dockerfile`, `bash`, `sql`, `ini`, `text`, `hcl`).
   - Every document begins with `# Document Title`, includes a Table of Contents, and ends with Next Document pointers.
   - Doc 5 includes multi-stage Dockerfile (4 stages, non-root UID 10001), 7 docker-compose services, and full K8s/Helm manifests.
   - Doc 6 includes 32 AlertManager rules (requirement: 30+), 29 Grafana dashboard panels (requirement: 20+), OpenTelemetry APM, and Loki/ELK configs.
   - Doc 7 includes 54 pytest test cases (requirement: 50+), 10 fixtures, data factories, mock watsonx client, and Locust load testing scripts.
   - Doc 8 includes 105 verification checklist items across 5 pillars (requirement: 100+), zero-downtime migration scripts, and emergency rollback automation.

5. **Test Suite Execution**:
   - `python -m pytest tests/test_docs_empirical_challenge.py -v -s`: 23 passed in 3.28s.
   - Existing codebase test suite: 310 passed.

---

## 2. Logic Chain

1. **Observation 1 & 3** establish that `k8s/deployment.yaml` configures liveness and readiness probe paths (`/api/v1/health/liveness` and `/api/v1/health/readiness`) that do not exist on the FastAPI routers (either the actual router in `cerberus/api/v1/health.py` or the documented router in `MONITORING_OPERATIONS.md`), returning HTTP `404 Not Found`.
2. When Kubernetes applies `k8s/deployment.yaml`, the kubelet will repeatedly fail probe checks. Because liveness fails, kubelet will terminate the container every `periodSeconds * failureThreshold` (30 seconds), causing `CrashLoopBackOff`. Because readiness fails, the pod is never added to the Service endpoints pool, resulting in a total outage upon deployment.
3. **Observation 2** establishes that `HighReviewFailureRate` in `k8s/alerts/codevault-alerts.yaml` contains an invalid PromQL expression (`{status="failed"[5m]}`). Prometheus Operator and Prometheus servers reject invalid PromQL syntax during rule ingestion. When a rule fails syntax validation, Prometheus drops the rule or refuses to load the rule group (`codevault.api.rules`), causing a silent monitoring blackout for critical production alerts.
4. While the documentation volume, technical sophistication, and architectural depth are outstanding and meet all quantitative requirements (checklist count, panel count, test count, rule count, zero placeholders), deploying the files verbatim into a real Kubernetes cluster and Prometheus stack will trigger immediate operational failures.
5. Therefore, the required changes must be completed before final signoff.

---

## 3. Caveats

- **AWS / IBM Cloud Live API Execution**: CLI commands invoking `aws rds` or IBM watsonx Cloud APIs were checked for structural and syntactic validity, but not executed against active cloud accounts because credentials and live cloud resources were not provided in this environment.
- **Chaos Injection**: Chaos scenarios in Doc 8 were validated for script logic and parameter correctness, but not executed against live production nodes.
- **Doc 2 Upstream Test Failure**: `tests/test_doc2_agents.py` currently fails on Doc 2 (`AGENT_SPECIFICATIONS.md`) due to a missing `Optional` import in Block #2. That file is under review by `challenger_doc1_4`.

---

## 4. Conclusion

**Verdict: REQUEST_CHANGES**

Docs 5 through 8 represent an exceptionally comprehensive, enterprise-grade operations and QA baseline. However, deployment reliability and observability require the following specific corrections:

### Required Actions for Author/Remediator:

1. **Fix Kubernetes Deployment Health Probes (`DEPLOYMENT_GUIDE.md`)**:
   In `k8s/deployment.yaml` (lines 590–607), update probe paths to match the FastAPI router:
   ```yaml
   startupProbe:
     httpGet:
       path: /api/v1/health/startup
       port: http
   livenessProbe:
     httpGet:
       path: /api/v1/health
       port: http
   readinessProbe:
     httpGet:
       path: /api/v1/ready
       port: http
   ```
   *(Or alternatively, add `/api/v1/health/liveness`, `/api/v1/health/readiness`, and `/api/v1/health/startup` route aliases to `cerberus/api/v1/health.py` and `cerberus/api/health.py`)*.

2. **Fix Helm Deployment Template (`DEPLOYMENT_GUIDE.md`)**:
   In `deploy/helm/codevault/templates/deployment.yaml`:
   - Add `startupProbe` definition matching `k8s/deployment.yaml`.
   - Ensure `livenessProbe` (`/api/v1/health`) and `readinessProbe` (`/api/v1/ready`) align with `k8s/deployment.yaml`.

3. **Fix Malformed PromQL Syntax (`MONITORING_OPERATIONS.md`)**:
   In `k8s/alerts/codevault-alerts.yaml` (line 996), change:
   ```yaml
   expr: sum(rate(codevault_reviews_total{status="failed"[5m]})) / sum(rate(codevault_reviews_total[5m])) > 0.10
   ```
   to:
   ```yaml
   expr: sum(rate(codevault_reviews_total{status="failed"}[5m])) / sum(rate(codevault_reviews_total[5m])) > 0.10
   ```

4. **Align Health Probe Endpoints in Health Router (`MONITORING_OPERATIONS.md`)**:
   In `cerberus/api/health.py` (lines 2004–2025), add route aliases:
   ```python
   @router.get("/health/liveness", status_code=status.HTTP_200_OK)
   @router.get("/health/readiness", response_model=HealthStatusResponse)
   ```
   so that all documented variants (`/health`, `/health/live`, `/health/liveness`, `/health/ready`, `/health/readiness`) resolve to HTTP `200`.

---

## 5. Verification Method

To independently verify these findings:

1. **Run Empirical Challenge Suite**:
   ```powershell
   python -m pytest tests/test_docs_empirical_challenge.py -v -s
   ```
   Confirms all 23 empirical validation checks, including PromQL grammar check and HTTP 404 probe contract tests.

2. **Reproduce HTTP 404 Probe Failure**:
   ```powershell
   python -c "from fastapi.testclient import TestClient; from cerberus.api.app import app; c = TestClient(app); print('/liveness:', c.get('/api/v1/health/liveness').status_code); print('/readiness:', c.get('/api/v1/health/readiness').status_code)"
   ```
   Expected output:
   `/liveness: 404`
   `/readiness: 404`

3. **Reproduce PromQL Parse Hazard**:
   Inspect line 996 of `MONITORING_OPERATIONS.md`:
   Observe `{status="failed"[5m]}`. Moving `[5m]` outside braces invalidates this defect.
