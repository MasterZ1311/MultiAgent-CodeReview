# 🎬 cerberus</> Live Demonstration Script
### *Autonomous Multi-Agent Code Review & Quality Assurance Platform*
**Target Audience**: IBM Evaluators, Technical Directors, Enterprise Architects, Engineering Leads  
**Duration**: 10 Minutes  
**Prerequisites**: Terminal / PowerShell, Web Browser  

---

## ⏱️ Demo Timeline Overview

```
[00:00 - 02:00] ── Executive Problem Statement & Multi-Agent Architecture
[02:00 - 04:00] ── CLI Developer Experience & Automated Pre-Commit Gates
[04:00 - 07:00] ── Interactive Visual Web Dashboard & Compliance Audit
[07:00 - 08:30] ── Automated 5-Scenario Verification (`demo/run_demo.py`)
[08:30 - 09:30] ── High-Throughput Performance & Cache Acceleration (`demo/perf_test.py`)
[09:30 - 10:00] ── IBM watsonx.ai Foundation Models & Q&A
```

---

## 📌 Step-by-Step Presentation Guide

### 1. Introduction & Multi-Agent Architecture (00:00 - 02:00)
**Talking Points:**
> "Modern code review is a notorious bottleneck. Security teams review for injection and leaked secrets, performance engineers look for algorithmic bloat and N+1 queries, while compliance teams struggle to enforce HIPAA, GDPR, and SOC 2 requirements. Human reviews are slow and inconsistent.
> 
> **cerberus</>** solves this by orchestrating a cooperative federation of **five autonomous, specialized AI agents** that evaluate code concurrently in under 10 milliseconds:
> 1. **Security Agent**: OWASP Top 10, CWE-89 SQL injection, CWE-798 secrets, CVSS 3.1 scoring.
> 2. **Performance Agent**: AST-driven Big-O complexity (O(n²)), memory allocations, N+1 query patterns.
> 3. **Quality Agent**: Cognitive complexity, long methods, dangerous bare except clauses, docstrings.
> 4. **Architecture Agent**: Package coupling, circular import hazards, and single-responsibility violations.
> 5. **Compliance Agent**: Regulatory enforcement for HIPAA (45 CFR §164.312), GDPR (Articles 5, 25), SOC 2 (CC6.1), and PCI-DSS v4.0."

---

### 2. Developer Experience & CLI Pre-Commit Demo (02:00 - 04:00)

**Action 1: Inspect the Agent Ecosystem**
```bash
python -m cerberus.cli list-agents
```
*Point out*: All 5 specialized agents are active with individual capability lists.

**Action 2: Execute an On-Demand CLI Review**
```bash
python -m cerberus.cli review --snippet "import os`nAPI_KEY = 'sk-1234567890'`ndef get_user(uid):`n    return db.execute(f'SELECT * FROM users WHERE id = {uid}')"
```
*Showcase*:
- Instant synthesized review in **~5ms**.
- Quality Score calculated dynamically (73.2 / 100).
- Multiple perspectives: Security catches SQL injection, Compliance catches SOC 2 master key violation, Quality catches missing docstrings.
- Actionable, code-diff suggestions provided for every finding.

**Action 3: Demonstrate Git Pre-Commit Blocking Gate**
```bash
python -m cerberus.cli review --snippet "eval(user_input)" --blocking
```
*Point out*: The process exits with code 1 (`⛔ Blocking Commit/Push`), showing how `cerberus` integrates directly into Git hooks and CI/CD pipelines to prevent vulnerable code from entering repositories.

---

### 3. Interactive Web Dashboard Demo (04:00 - 07:00)

**Action 1: Launch the Local Server**
```bash
python -m cerberus.cli serve --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in Chrome or Edge.

**Action 2: Walkthrough the Visual Presets**
1. **⚠️ SQL & Secrets Preset**:
   - Click the preset button.
   - Click **Execute Multi-Agent Review** (or press `Ctrl+Enter`).
   - *Highlight*: Conic gradient score ring turns **RED (24/100)**; Critical severity badges pop up with line numbers and remediations.
2. **⚡ O(n²) & Loops Preset**:
   - Click the preset button and run.
   - *Highlight*: Algorithmic complexity warning (`Quadratic Time Complexity O(n²)`) and N+1 query warning displayed simultaneously.
3. **📋 HIPAA & GDPR Preset**:
   - Click the preset button and run.
   - *Highlight*: Compliance violations flagged: HIPAA ePHI logging, cleartext HTTP endpoint transmission, and GDPR URL PII exposure.
4. **✨ Clean Code Preset**:
   - Click the preset button and run.
   - *Highlight*: Conic gradient turns **VIBRANT GREEN (100/100)** with zero findings.
5. **📋 Copy JSON**:
   - Click **📋 Copy JSON** in the top right.
   - Paste into any editor or notepad to show the machine-readable, structured JSON contract ready for SIEM or enterprise dashboard ingestion.

---

### 4. Automated 5-Scenario Verification Suite (07:00 - 08:30)

**Action: Run the Automated Demo Runner**
```bash
python demo/run_demo.py
```
*Highlights to voice over*:
- *"Here we have an automated test harness executing all 5 enterprise scenarios."*
- Notice the pass badges: **5 / 5 Scenarios Passed**.
- Notice the total execution time across 5 diverse scenarios is under **100 milliseconds combined**.
- Shows both holistic scoring and surgical agent-specific attribution.

---

### 5. High-Throughput Performance & Cache Acceleration (08:30 - 09:30)

**Action: Run the Latency & Cache Profiler**
```bash
python demo/perf_test.py
```
*Key Metrics to Highlight*:
- **Cold Review Latency**: **~4.9 ms** per multi-agent review.
- **Hot Cached Review Latency**: **~0.5 ms** (over **10x faster**, 100% cache hit rate).
- **Concurrent Throughput**: **235+ reviews/second** on standard laptop hardware.
- Zero external network dependencies required during execution.

---

### 6. IBM watsonx.ai Foundation Models & Enterprise Scaling (09:30 - 10:00)

**Talking Points:**
> "In enterprise production, `cerberus` supports a hybrid dual-tier intelligence architecture:
> - **IBM watsonx.ai Foundation Models**: Powered by **IBM Granite** (`ibm/granite-13b-chat-v2`, `ibm/granite-3-8b-instruct`), providing natural language contextual reasoning, enterprise policy interpretation, and deep multi-lingual code refactoring.
> - **Heuristic & AST Deterministic Engine**: Built into every installation to provide sub-10 millisecond offline analysis, ensuring that if a cloud connection or API quota is ever interrupted, code reviews never fail or block engineering teams.
> - Full setup instructions, model mappings, and configuration steps are documented in `WATSONX_INTEGRATION.md`."

---

## 💡 Quick Reference Cheat Sheet

| Command | Purpose |
| :--- | :--- |
| `python -m cerberus.cli health` | Verify cluster & agent health |
| `python -m cerberus.cli list-agents` | Display all 5 active agents |
| `python -m cerberus.cli review --snippet "..."` | Quick CLI review |
| `python -m cerberus.cli serve` | Launch web dashboard on `:8000` |
| `python demo/run_demo.py` | Run 5-scenario automated demo |
| `python demo/perf_test.py` | Run performance & cache benchmark |
| `http://127.0.0.1:8000/docs` | Interactive Swagger OpenAPI docs |
| `http://127.0.0.1:8000/metrics` | Live Prometheus telemetry stream |
