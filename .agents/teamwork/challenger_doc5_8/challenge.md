# Empirical Adversarial Challenge Report: Docs 5–8

**Target Documents**:
- Doc 5: `DEPLOYMENT_GUIDE.md`
- Doc 6: `MONITORING_OPERATIONS.md`
- Doc 7: `TESTING_STRATEGY.md`
- Doc 8: `PRODUCTION_LAUNCH_MANUAL.md`

**Verifier**: `challenger_doc5_8` (Empirical Challenger)  
**Date**: 2026-09-24  
**Test Suite**: `tests/test_docs_empirical_challenge.py` (23 passed)

---

## Challenge Summary

**Overall risk assessment**: **HIGH**

While the four documents provide exceptionally deep, production-grade technical content (comprising over 290 KB of specifications, multi-stage Dockerfiles, full Kubernetes manifests, Helm v3 charts, 32 AlertManager rules, 29 Grafana dashboard panels, 54 pytest test cases, and 105 verification checklist items with zero forbidden placeholder tokens), adversarial testing and AST/YAML/PromQL parsing exposed **critical runtime contract mismatches** and **syntax bugs** that would halt Kubernetes rollouts and disable alert evaluations in production.

---

## Challenges

### [Critical] Challenge 1: Kubernetes Deployment Health Probe Endpoint Mismatch (HTTP 404 CrashLoopBackOff)

- **Target File**: `DEPLOYMENT_GUIDE.md` (lines 590–607, `k8s/deployment.yaml`) vs. `cerberus/api/v1/health.py` and `MONITORING_OPERATIONS.md` (lines 1994–2020)
- **Assumption Challenged**: Assumed that the probe paths specified in `k8s/deployment.yaml` (`/api/v1/health/startup`, `/api/v1/health/liveness`, `/api/v1/health/readiness`) correspond to implemented endpoints in the FastAPI router.
- **Attack Scenario**:
  A DevOps/SRE engineer deploys the application using `kubectl apply -f k8s/deployment.yaml`.
  The kubelet periodically sends HTTP GET requests to:
  - Startup probe: `/api/v1/health/startup`
  - Liveness probe: `/api/v1/health/liveness`
  - Readiness probe: `/api/v1/health/readiness`
  
  **Empirical Verification**:
  Direct execution of HTTP client against the codebase (`cerberus/api/app.py`):
  - `GET /api/v1/health` -> HTTP `200 OK`
  - `GET /api/v1/ready` -> HTTP `200 OK`
  - `GET /api/v1/health/liveness` -> HTTP `404 Not Found` (FAILED)
  - `GET /api/v1/health/readiness` -> HTTP `404 Not Found` (FAILED)
  - `GET /api/v1/health/startup` -> HTTP `404 Not Found` (FAILED)

  Furthermore, testing against the router documented in `MONITORING_OPERATIONS.md` (Block 14):
  - `@router.get("/health/live")` exists, but `/health/liveness` returns HTTP `404`!
  - `@router.get("/health/ready")` exists, but `/health/readiness` returns HTTP `404`!
- **Blast Radius**:
  100% of pods fail startup and liveness probes. Kubelet repeatedly terminates and restarts containers, sending the deployment into an unrecoverable `CrashLoopBackOff`. The Kubernetes Service endpoints controller marks all pods unready, completely blocking ingress traffic and causing total service outage upon initial cluster launch.
- **Mitigation**:
  Align all probe paths consistently across `k8s/deployment.yaml`, Helm chart `deploy/helm/codevault/templates/deployment.yaml`, and `cerberus/api/v1/health.py`:
  - Liveness: `/api/v1/health` (or add `/api/v1/health/liveness` alias to `cerberus/api/v1/health.py`)
  - Readiness: `/api/v1/ready` (or add `/api/v1/health/readiness` alias to `cerberus/api/v1/health.py`)
  - Startup: `/api/v1/health/startup` (implement endpoint in `cerberus/api/v1/health.py`)

---

### [High] Challenge 2: Malformed PromQL Syntax in Prometheus Alerting Rules

- **Target File**: `MONITORING_OPERATIONS.md` (lines 995–1002, `k8s/alerts/codevault-alerts.yaml`)
- **Assumption Challenged**: Assumed all PromQL expressions in `codevault-alerts.yaml` are syntactically valid and parseable by the Prometheus PromQL parser.
- **Attack Scenario**:
  The alerting manifest is applied to a Prometheus Operator cluster.
  In rule `HighReviewFailureRate`:
  ```yaml
  - alert: HighReviewFailureRate
    expr: sum(rate(codevault_reviews_total{status="failed"[5m]})) / sum(rate(codevault_reviews_total[5m])) > 0.10
  ```
  The range vector duration `[5m]` is placed inside the label matcher curly braces `{status="failed"[5m]}` rather than attached to the vector selector `{status="failed"}[5m]`.
- **Empirical Verification**:
  Extracted rule expression and evaluated via regex/PromQL grammar parser in `tests/test_docs_empirical_challenge.py::test_empirical_promql_syntax_error_in_doc6`:
  Prometheus grammar requires `metric_name{label=value}[range]`. Placing `[5m]` inside `{...}` triggers a fatal Prometheus parse error:
  `parse error: unexpected "[" in label matching, expected "," or "}"`.
- **Blast Radius**:
  The Prometheus PrometheusRule CRD evaluation fails. Depending on the Prometheus Operator version, the entire rule group `codevault.api.rules` (which includes `HighAPIErrorRate`, `APICriticalLatency`, and `SecurityAgentDown`) is rejected from the Prometheus active rule registry, silently blinding SREs to critical API failures and agent crashes.
- **Mitigation**:
  Correct the PromQL expression in `MONITORING_OPERATIONS.md`:
  ```yaml
  expr: sum(rate(codevault_reviews_total{status="failed"}[5m])) / sum(rate(codevault_reviews_total[5m])) > 0.10
  ```

---

### [Medium] Challenge 3: Probe Contract Drift & Missing `startupProbe` in Helm Chart Templates

- **Target File**: `DEPLOYMENT_GUIDE.md` (lines 1150–1175, `deploy/helm/codevault/templates/deployment.yaml`)
- **Assumption Challenged**: Assumed that the Helm chart provides identical reliability protections and compatible probe contracts to the standalone Kubernetes manifests.
- **Attack Scenario**:
  1. Helm `templates/deployment.yaml` specifies `readinessProbe: path: /api/v1/ready`. While this matches the repo's existing `cerberus/api/v1/health.py`, it conflicts with the standalone `k8s/deployment.yaml` (`/api/v1/health/readiness`) and `MONITORING_OPERATIONS.md` (`/api/v1/health/ready`).
  2. Helm `templates/deployment.yaml` omits `startupProbe`.
- **Empirical Verification**:
  Parsed `deploy/helm/codevault/templates/deployment.yaml`:
  Contains `livenessProbe` and `readinessProbe`, but no `startupProbe`.
  In Python FastAPI containers loading LangGraph orchestrators, DB connection pools, and watsonx client wrappers, initialization under resource-constrained nodes can exceed 15 seconds. Without `startupProbe`, `livenessProbe` (with `periodSeconds: 15, timeoutSeconds: 5`) will kill the container before warmup completes.
- **Blast Radius**:
  Helm deployments on busy Kubernetes clusters risk startup reboot loops during cold starts or HPA scaling events.
- **Mitigation**:
  Add `startupProbe` to `deploy/helm/codevault/templates/deployment.yaml` mirroring `k8s/deployment.yaml` and standardize the path contract.

---

### [Low] Challenge 4: Rollback Script Health Verification Relies on Legacy Path

- **Target File**: `PRODUCTION_LAUNCH_MANUAL.md` (`scripts/emergency_rollback.sh`, line 533)
- **Assumption Challenged**: Rollback health validation assumes `/api/v1/health` guarantees readiness of all sub-dependencies (DB, Redis, watsonx).
- **Attack Scenario**:
  In `cerberus/api/v1/health.py`, `/api/v1/health` checks process uptime and basic cache pointer, but does not perform an active `SELECT 1` ping on Postgres or a Redis ping. In contrast, `/api/v1/ready` (or `/health/ready` in Doc 6) explicitly asserts DB connection and Redis ping.
  During a rollback, `scripts/emergency_rollback.sh` checks `/api/v1/health` which returns `200` even if the database is in recovery mode or locks are held.
- **Blast Radius**:
  Emergency rollback script may declare success prematurely before database connection pools are operational.
- **Mitigation**:
  Update `scripts/emergency_rollback.sh` to check `/api/v1/ready` instead of `/api/v1/health`.

---

## Stress Test Results

| Test Scenario | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|
| **Placeholder Scan**: Scan Docs 5–8 for `TODO`, `FIXME`, `<replace_me>` | Zero matches across all documents | 0 matches found in all 4 documents | **PASS** |
| **Code Block Language Tag Audit**: Verify language specified on all fences | 100% of code blocks have explicit language tag | 77 blocks checked across Docs 5–8; 0 missing language | **PASS** |
| **Doc 5 Dockerfile Audit**: Multi-stage build targets & UID 10001 | 4 distinct stages (`builder`, `tester`, `security-scan`, `runtime`), UID 10001 | Builder, tester, scan, and non-root runtime verified | **PASS** |
| **Doc 5 docker-compose.yml YAML Syntax**: Parse all services | Valid YAML, services `api`, `db`, `redis`, `mock-watsonx`, `prometheus`, `grafana`, `jaeger` | Valid YAML, all 7 services configured with volumes & healthchecks | **PASS** |
| **Doc 5 Kubernetes Manifests Spec Audit**: Deployment, Service, Ingress, HPA, PDB, ConfigMap, Secret, NetworkPolicy | Valid YAML, proper resource requests/limits, probes, security context | Valid YAML, resources & securityContext strictly defined | **PASS** |
| **Doc 5 K8s Deployment Probe Endpoints**: Hit `/api/v1/health/liveness`, `/readiness`, `/startup` | HTTP 200 OK | HTTP 404 Not Found (CrashLoopBackOff failure) | **FAIL** (Defect 1) |
| **Doc 5 Helm Chart & Values YAML**: Parse Chart.yaml and values.yaml | Valid YAML v2 chart, complete values structure | Valid YAML, replicaCount, resources, autoscaling present | **PASS** |
| **Doc 5 Helm Deployment Probe Audit**: Verify startupProbe presence | startupProbe present in template | startupProbe missing from Helm template | **FAIL** (Defect 3) |
| **Doc 5 Python IAM Token AST**: Syntax parse `cerberus/providers/watsonx_iam_auth.py` | Valid Python AST | Valid AST, 9 top-level nodes, proper type annotations | **PASS** |
| **Doc 6 AlertManager Config YAML**: Parse `config/alertmanager.yml` | Valid YAML, routes to slack and pagerduty | Valid YAML, 4 receiver routes verified | **PASS** |
| **Doc 6 PrometheusRule CRD YAML**: Parse `k8s/alerts/codevault-alerts.yaml` | Valid YAML, 30+ rules | Valid YAML, 32 rules across 3 groups | **PASS** |
| **Doc 6 PromQL Syntax Audit**: Validate all 32 PromQL alerting expressions | Balanced parens, braces, valid range vectors | 31 valid; 1 invalid expression with `[5m]` inside `{}` (`HighReviewFailureRate`) | **FAIL** (Defect 2) |
| **Doc 6 Grafana Dashboard JSON**: Parse `config/grafana/dashboards/codevault-overview.json` | Valid JSON, 20+ panels across domains | Valid JSON, 29 panels (5 rows + 24 panels) | **PASS** |
| **Doc 6 Python Telemetry & Cost AST**: Parse logging, telemetry, cost governance | Valid Python AST | Valid AST across all 6 python blocks | **PASS** |
| **Doc 7 Pytest Framework & Test Count**: AST parse test suites A–F | 50+ test cases, fixtures, mock watsonx client | 54 test functions, 10 fixtures, mock client verified | **PASS** |
| **Doc 7 Locust Load Test Script AST**: Verify Locust User class | FastHttpUser / User class defined with tasks | Valid AST, HttpUser with review task weightings | **PASS** |
| **Doc 7 Pytest INI & Coverage Config**: Parse pytest.ini and .coveragerc | Valid INI/YAML | Valid configuration | **PASS** |
| **Doc 8 Checklist Count Audit**: Count numbered verification items in tables | 100+ checklist items | 105 verification items across 5 pillars | **PASS** |
| **Doc 8 Runbooks & SQL Migrations**: Parse Python backfill and SQL migrations | Valid Python AST and SQL syntax | Valid AST and Expand/Contract SQL migration scripts | **PASS** |
| **Doc 8 Emergency Rollback Script**: Validate bash syntax with shlex | Valid shell script tokens, exit traps, curl health check | Valid shell script syntax | **PASS** |

---

## Unchallenged Areas

- **Live Cloud Provider Provisioning (AWS RDS / Route53 / IBM Cloud)**: Cloud provider API calls (e.g., `aws rds describe-db-snapshots`, IBM watsonx SaaS live provisioning) were validated structurally against CLI syntax and documentation schemas, but not executed against active cloud accounts (out of scope for local empirical test harness).
- **Physical Chaos Fault Injection (Network packet loss & pod killing on live cluster)**: Runbooks in Doc 8 were validated for command syntax and rollback logic, but live kernel-level chaos injection was not performed as the current environment is a local test container without a running multi-node Kubernetes cluster.
