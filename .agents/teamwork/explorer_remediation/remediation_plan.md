# Exhaustive Technical Remediation Plan: Forensic Audit & Defect Rectification

**Target Work Products**:
1. `PHASE_1_DETAILED_IMPLEMENTATION.md`
2. `AGENT_SPECIFICATIONS.md`
3. `DEPLOYMENT_GUIDE.md`
4. `MONITORING_OPERATIONS.md`

**Author**: `explorer_remediation` (Senior Technical Exploration & Remediation Strategy Engineer)  
**Parent Conversation ID**: `40dd2dae-3b0b-4a1f-aff5-27055825037a`  
**Date**: 2026-09-24  
**Integrity Mode**: Zero-Tolerance Enterprise Integrity Forensics  

---

## 1. Executive Summary & Remediation Scope

A comprehensive forensic audit and adversarial verification conducted by `auditor_all`, `reviewer_doc1_4`, and `challenger_doc5_8` identified specific, localized violations of markdown code block discipline, runtime Kubernetes probe contracts, and Prometheus PromQL syntax across 4 core deliverables. 

This remediation plan provides an exhaustive, line-by-line, copy-paste-ready specification for the implementing engineers (`worker_doc1_2` and `worker_doc5_6` / `worker_doc7_8`). Every defect is cataloged with its exact file path, line numbers, verbatim current content, root cause analysis, and verbatim remediated content.

### Summary of Targeted Edits

| Target Document | Defect Identifier | Exact Lines | Issue Description | Proposed Remediation |
|---|---|---|---|---|
| `PHASE_1_DETAILED_IMPLEMENTATION.md` | Violation 1.1 | 39–48 | Bare code block (Roadmap diagram) lacking language tag and file path header | Tag with `text`, add `# File: docs/architecture/directory_structure.txt` (or `# File: docs/phase1_roadmap.txt`) |
| `PHASE_1_DETAILED_IMPLEMENTATION.md` | Violation 1.2 | 1510–1513 | Python snippet (`finally:` socket cleanup) missing file path comment | Prepend `# File: src/codevault/api/v1/endpoints/streaming.py` inside block |
| `AGENT_SPECIFICATIONS.md` | Violation 2.1 | 47–68 | Three-Tier Execution Matrix diagram enclosed in bare backticks | Tag with `text`, add `# File: docs/architecture/agent_matrix.txt` |
| `AGENT_SPECIFICATIONS.md` | Violation 2.2 | 20 diagram blocks | 20 ASCII state machines enclosed in bare backticks without file headers | Tag with `text`, add `# File: src/codevault/agents/<agent_slug>/state_machine.txt` |
| `AGENT_SPECIFICATIONS.md` | Violation 2.3 | 40 prompt blocks | 20 System + 20 User Prompt blocks untagged without headers | Tag with `text` (or `json`), add `# File: src/codevault/agents/<agent_slug>/prompts.txt` |
| `AGENT_SPECIFICATIONS.md` | Violation 2.4 | 12 User Prompt blocks | Nested unescaped triple backticks terminate markdown code blocks prematurely | Wrap outer fences in 4 backticks ````text ... ```` to preserve inner snippets |
| `DEPLOYMENT_GUIDE.md` | Violation 3.1 | 1156–1167 | Helm deployment template lacks `startupProbe` to mirror `k8s/deployment.yaml` | Add `startupProbe` targeting `/api/v1/health` with `initialDelaySeconds: 10` |
| `MONITORING_OPERATIONS.md` | Violation 4.1 | 1010–1012 | PromQL syntax error in `HighReviewFailureRate`: `{status="failed"[5m]}` | Shift range vector `[5m]` outside braces: `{status="failed"}[5m]` |

---

## 2. Document 1: `PHASE_1_DETAILED_IMPLEMENTATION.md`

### 2.1 Violation 1.1: Missing Language Tag & File Header on Architecture/Roadmap Block

- **Target File**: `PHASE_1_DETAILED_IMPLEMENTATION.md`
- **Location**: Lines 39–48
- **Root Cause**: The Phase 1 Implementation Roadmap overview block is wrapped in bare triple backticks (` ``` `) without a language specifier (`text`) and without a `# File: ...` comment header.
- **Specification Alignment**: Zero-tolerance discipline requires 100% of code blocks to include a syntax identifier and file path header.

#### Current Verbatim Content (Lines 39–48):
```markdown
```
==================================================================================================
PHASE 1 IMPLEMENTATION ROADMAP: 4 WEEKS × 7 DAYS = 28 ENGINEERING DAYS
==================================================================================================
WEEK 1: Foundation, Core Schemas & LangGraph State Graph (Days 1–7)
WEEK 2: 5 Core Review Agents & IBM watsonx Integration (Days 8–14)
WEEK 3: Result Aggregation, Weighted Scoring & Persistence Engine (Days 15–21)
WEEK 4: Enterprise Hardening, Real-Time Streaming, CI/CD & Final Verification (Days 22–28)
==================================================================================================
```
```

#### Remediated Verbatim Content:
```markdown
```text
# File: docs/architecture/directory_structure.txt
==================================================================================================
PHASE 1 IMPLEMENTATION ROADMAP: 4 WEEKS × 7 DAYS = 28 ENGINEERING DAYS
==================================================================================================
WEEK 1: Foundation, Core Schemas & LangGraph State Graph (Days 1–7)
WEEK 2: 5 Core Review Agents & IBM watsonx Integration (Days 8–14)
WEEK 3: Result Aggregation, Weighted Scoring & Persistence Engine (Days 15–21)
WEEK 4: Enterprise Hardening, Real-Time Streaming, CI/CD & Final Verification (Days 22–28)
==================================================================================================
```
```
*(Note: If preferred by documentation tooling, `# File: docs/phase1_roadmap.txt` is an acceptable alternative; `# File: docs/architecture/directory_structure.txt` directly satisfies the task prompt).*

---

### 2.2 Violation 1.2: Missing File Path Header in Troubleshooting Python Block

- **Target File**: `PHASE_1_DETAILED_IMPLEMENTATION.md`
- **Location**: Lines 1510–1513
- **Root Cause**: In Troubleshooting Scenario 5 (WebSocket connection leak), the second remediation step provides a 2-line Python code snippet (`finally:\n    await connection_manager.close_and_remove(websocket, client_id)`) tagged with `python`, but lacks a `# File: ...` header. Step 1 right above it (line 1500) correctly includes `# File: src/codevault/api/v1/endpoints/streaming.py`.

#### Current Verbatim Content (Lines 1509–1513):
```markdown
   2. Enforce socket cleanup in a guaranteed `finally:` block:
      ```python
      finally:
          await connection_manager.close_and_remove(websocket, client_id)
      ```
```

#### Remediated Verbatim Content:
```markdown
   2. Enforce socket cleanup in a guaranteed `finally:` block:
      ```python
      # File: src/codevault/api/v1/endpoints/streaming.py
      finally:
          await connection_manager.close_and_remove(websocket, client_id)
      ```
```

---

## 3. Document 2: `AGENT_SPECIFICATIONS.md`

### 3.1 Violation 2.1: Three-Tier Classification Matrix Diagram

- **Target File**: `AGENT_SPECIFICATIONS.md`
- **Location**: Lines 47–68
- **Root Cause**: Section 2 opening diagram displays the Three-Tier Agent Execution Matrix wrapped in bare triple backticks (` ``` `) with no language tag and no file header.

#### Current Verbatim Content (Lines 47–51, 67–68):
```markdown
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MASTER ORCHESTRATOR GRAPH                                │
└────────────┬───────────────────────────────┬───────────────────────────────┬───────────┘
...
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```
```

#### Remediated Verbatim Content:
```markdown
```text
# File: docs/architecture/agent_matrix.txt
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MASTER ORCHESTRATOR GRAPH                                │
└────────────┬───────────────────────────────┬───────────────────────────────┬───────────┘
             │                               │                               │
             ▼                               ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│         TIER 1          │     │         TIER 2          │     │         TIER 3          │
│   (Critical Blocking)   │     │  (Deep Analysis & Law)  │     │   (Team & Operations)   │
│ Latency SLA: < 4.0s     │     │ Latency SLA: < 10.0s    │     │ Latency SLA: Asynch/Bg  │
├─────────────────────────┤     ├─────────────────────────┤     ├─────────────────────────┤
│ 1. Predictive Bug       │     │ 5. Technical Debt       │     │ 12. IDE Integration     │
│ 2. Supply Chain Sec     │     │ 6. Code Fixer           │     │ 13. Cost Analysis       │
│ 3. Perf Regression      │     │ 7. Custom Rule Engine   │     │ 16. Codebase Fine-tune  │
│ 4. Architecture Viol    │     │ 8. Multi-Language Rev   │     │ 17. Expertise Router    │
│                         │     │ 9. Historical Trends    │     │ 18. Knowledge Base      │
│                         │     │ 10. ML Code Auditor     │     │ 19. Burndown Predict    │
│                         │     │ 11. Compliance Stds     │     │ 20. Collab Review       │
│                         │     │ 14. Accessibility WCAG  │     │                         │
│                         │     │ 15. Anomaly Detection   │     │                         │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```
```

---

### 3.2 Violation 2.2: All 20 ASCII State Machine Diagrams (Section 2 of Each Agent)

- **Target File**: `AGENT_SPECIFICATIONS.md`
- **Root Cause**: Each agent includes an ASCII state machine diagram under `#### 2. ASCII State Machine Diagram`. All 20 diagrams currently use bare triple backticks (` ``` `) lacking the `text` language specifier and lacking a file header comment.
- **Agent Slug Mapping**: Derived from the canonical agent module directory structure already established in `src/codevault/agents/<agent_slug>/schemas.py` and `tools.py`.

#### Complete Inventory & Remediation Table for State Machines

| Agent # | Agent Name | Canonical Slug | Current Fence Line Range | Target File Path Header | Remediated Fence Tag |
|:---:|---|---|:---:|---|:---:|
| 1 | Predictive Bug Detection | `bug_predictor` | Lines 108–134 | `# File: src/codevault/agents/bug_predictor/state_machine.txt` | ```` ```text ```` |
| 2 | Supply Chain Security | `supply_chain` | Lines 273–304 | `# File: src/codevault/agents/supply_chain/state_machine.txt` | ```` ```text ```` |
| 3 | Performance Regression | `perf_regression` | Lines 444–470 | `# File: src/codevault/agents/perf_regression/state_machine.txt` | ```` ```text ```` |
| 4 | Architecture Violation | `architecture` | Lines 606–632 | `# File: src/codevault/agents/architecture/state_machine.txt` | ```` ```text ```` |
| 5 | Technical Debt Quantifier | `technical_debt` | Lines 749–775 | `# File: src/codevault/agents/technical_debt/state_machine.txt` | ```` ```text ```` |
| 6 | Code Fixer | `code_fixer` | Lines 893–919 | `# File: src/codevault/agents/code_fixer/state_machine.txt` | ```` ```text ```` |
| 7 | Custom Rule Engine | `custom_rules` | Lines 1038–1062 | `# File: src/codevault/agents/custom_rules/state_machine.txt` | ```` ```text ```` |
| 8 | Multi-Language Reviewer | `multi_language` | Lines 1186–1212 | `# File: src/codevault/agents/multi_language/state_machine.txt` | ```` ```text ```` |
| 9 | Historical Trend Analysis | `historical_trends` | Lines 1334–1358 | `# File: src/codevault/agents/historical_trends/state_machine.txt` | ```` ```text ```` |
| 10 | ML Code Auditor | `ml_auditor` | Lines 1466–1492 | `# File: src/codevault/agents/ml_auditor/state_machine.txt` | ```` ```text ```` |
| 11 | Compliance Standards | `compliance` | Lines 1606–1630 | `# File: src/codevault/agents/compliance/state_machine.txt` | ```` ```text ```` |
| 12 | IDE Integration | `ide_integration` | Lines 1748–1772 | `# File: src/codevault/agents/ide_integration/state_machine.txt` | ```` ```text ```` |
| 13 | Cost Analysis (Cloud & LLM) | `cost_analysis` | Lines 1879–1903 | `# File: src/codevault/agents/cost_analysis/state_machine.txt` | ```` ```text ```` |
| 14 | Accessibility Checker | `accessibility` | Lines 2006–2032 | `# File: src/codevault/agents/accessibility/state_machine.txt` | ```` ```text ```` |
| 15 | Anomaly Detection | `anomaly_detection` | Lines 2148–2174 | `# File: src/codevault/agents/anomaly_detection/state_machine.txt` | ```` ```text ```` |
| 16 | Codebase Fine-tuning | `fine_tuning` | Lines 2273–2297 | `# File: src/codevault/agents/fine_tuning/state_machine.txt` | ```` ```text ```` |
| 17 | Team Expertise Router | `expertise_router` | Lines 2403–2427 | `# File: src/codevault/agents/expertise_router/state_machine.txt` | ```` ```text ```` |
| 18 | Knowledge Base Builder | `knowledge_base` | Lines 2524–2548 | `# File: src/codevault/agents/knowledge_base/state_machine.txt` | ```` ```text ```` |
| 19 | Burndown Predictor | `burndown_predictor` | Lines 2644–2668 | `# File: src/codevault/agents/burndown_predictor/state_machine.txt` | ```` ```text ```` |
| 20 | Collaborative Review | `collaborative_review` | Lines 2769–2793 | `# File: src/codevault/agents/collaborative_review/state_machine.txt` | ```` ```text ```` |

#### Representative Example (Agent 1: Lines 107–113):
- **Before**:
  ```markdown
  #### 2. ASCII State Machine Diagram
  ```
  ┌────────────────────────────────┐
  │   Input: Source Code & Diff    │
  ```
- **After**:
  ```markdown
  #### 2. ASCII State Machine Diagram
  ```text
  # File: src/codevault/agents/bug_predictor/state_machine.txt
  ┌────────────────────────────────┐
  │   Input: Source Code & Diff    │
  ```

---

### 3.3 Violation 2.3 & 2.4: All 20 watsonx Prompt Blocks & Nested Code Fence Escaping

- **Target File**: `AGENT_SPECIFICATIONS.md`
- **Root Cause**:
  1. **Missing Language Specifier & Header**: Under `#### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)`, all 20 agents contain a System Prompt block and a User Prompt block opened with bare triple backticks (` ``` `) lacking `text` (or `json`) and lacking `# File: src/codevault/agents/<agent_slug>/prompts.txt`.
  2. **Nested Fence Markdown Corruption**: 12 agents include inner triple-backtick markdown blocks inside User Prompts (e.g., ````{language}\n{code}\n````, ````diff\n{diff}\n````, ````yaml\n{custom_rules_yaml}\n````, ````{framework}\n{code}\n````, ````{component_type}\n{code}\n````) or System Prompts (Agent 6). In standard CommonMark/GFM markdown parsers, the internal triple backticks terminate the outer block prematurely, leaving downstream headings, text, and subsequent code fences corrupt and unrendered.
- **Architectural Fix**:
  - Enclose prompt template blocks in **4 backticks** (` ````text ... ```` `).
  - Prepend `# File: src/codevault/agents/<agent_slug>/prompts.txt` (or `# File: src/codevault/agents/<agent_slug>/system_prompt.txt` / `user_prompt.txt`).
  - Using 4 backticks for outer fences ensures that any 3-backtick sequences inside the prompt templates are treated strictly as string content, preventing syntax highlighting collapse.

#### Comprehensive Prompt Inventory & Remediation Matrix (All 20 Agents)

| Agent # | Slug | System Prompt Lines | User Prompt Lines | Nested Fences? | Inner Fences Observed | Target Outer Fence |
|:---:|---|:---:|:---:|:---:|---|:---:|
| 1 | `bug_predictor` | 202–220 | 222–231 | **YES** | ````{language}```` (L224), ````diff```` (L228) | ````text ... ```` |
| 2 | `supply_chain` | 377–395 | 397–402 | No | Plain string `{packages}` | ````text ... ```` |
| 3 | `perf_regression` | 547–559 | 561–566 | **YES** | ````{language}```` (L563) | ````text ... ```` |
| 4 | `architecture` | 690–703 | 705–710 | **YES** | ````{language}```` (L707) | ````text ... ```` |
| 5 | `technical_debt` | 833–845 | 847–852 | **YES** | ````{language}```` (L849) | ````text ... ```` |
| 6 | `code_fixer` | 979–987 | 989–995 | **YES** (Both) | System: ````{language}```` (L984); User: ````{language}```` (L992) | ````text ... ```` |
| 7 | `custom_rules` | 1123–1134 | 1136–1145 | **YES** | ````yaml```` (L1138), ````{language}```` (L1142) | ````text ... ```` |
| 8 | `multi_language` | 1274–1285 | 1287–1292 | **YES** | ````{language}```` (L1289) | ````text ... ```` |
| 9 | `historical_trends` | 1409–1421 | 1423–1426 | No | Plain string `{time_series_points}` | ````text ... ```` |
| 10 | `ml_auditor` | 1548–1559 | 1561–1566 | **YES** | ````{framework}```` (L1563) | ````text ... ```` |
| 11 | `compliance` | 1690–1701 | 1703–1708 | **YES** | ````{language}```` (L1705) | ````text ... ```` |
| 12 | `ide_integration` | 1822–1832 | 1834–1839 | **YES** | Bare triple backticks (L1836) | ````text ... ```` |
| 13 | `cost_analysis` | 1949–1961 | 1963–1968 | **YES** | ````{language}```` (L1965) | ````text ... ```` |
| 14 | `accessibility` | 2090–2101 | 2103–2108 | **YES** | ````{component_type}```` (L2105) | ````text ... ```` |
| 15 | `anomaly_detection` | 2216–2228 | 2230–2235 | No | Plain string `{pr_metrics}` | ````text ... ```` |
| 16 | `fine_tuning` | 2341–2356 | 2358–2363 | No | Plain strings `{original_code}` | ````text ... ```` |
| 17 | `expertise_router` | 2469–2481 | 2483–2485 | No | Plain string `{changed_files}` | ````text ... ```` |
| 18 | `knowledge_base` | 2588–2600 | 2602–2605 | No | Plain string `{review_threads}` | ````text ... ```` |
| 19 | `burndown_predictor` | 2712–2724 | 2726–2730 | No | Plain string `{pr_size_lines}` | ````text ... ```` |
| 20 | `collaborative_review` | 2857–2869 | 2871–2876 | No | Plain string `{unresolved_blocking_issues}` | ````text ... ```` |

---

### 3.4 Verbatim Before & After for All 20 Prompt Sections

#### Agent 1: Predictive Bug Detection (Lines 200–232)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Enterprise Defect Prediction Specialist utilizing IBM Granite.
    [TASK]: Analyze the provided code diff and identify latent bugs, unhandled null pointers, off-by-one boundary hazards, and race conditions before runtime.
    [CONSTRAINTS]: Return strictly valid JSON adhering to the BugPredictorOutput schema. No markdown conversational filler.
    [FORMAT]:
    {
      "agent_name": "predictive_bug_detection",
      "bug_probability": 0.85,
      "high_risk_lines": [42, 87],
      "findings": [
        {
          "category": "logic_defect",
          "title": "Potential Null Pointer Dereference",
          "line": 42,
          "message": "Variable may be None prior to member access."
        }
      ]
    }
    ```
  - **User Prompt**:
    ```
    Analyze this {language} snippet for latent bugs and defect probability:
    ```{language}
    {code}
    ```
    Diff Context:
    ```diff
    {diff}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/bug_predictor/prompts.txt
    [ROLE]: Enterprise Defect Prediction Specialist utilizing IBM Granite.
    [TASK]: Analyze the provided code diff and identify latent bugs, unhandled null pointers, off-by-one boundary hazards, and race conditions before runtime.
    [CONSTRAINTS]: Return strictly valid JSON adhering to the BugPredictorOutput schema. No markdown conversational filler.
    [FORMAT]:
    {
      "agent_name": "predictive_bug_detection",
      "bug_probability": 0.85,
      "high_risk_lines": [42, 87],
      "findings": [
        {
          "category": "logic_defect",
          "title": "Potential Null Pointer Dereference",
          "line": 42,
          "message": "Variable may be None prior to member access."
        }
      ]
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/bug_predictor/prompts.txt
    Analyze this {language} snippet for latent bugs and defect probability:
    ```{language}
    {code}
    ```
    Diff Context:
    ```diff
    {diff}
    ```
    ````
  ````

---

#### Agent 2: Supply Chain Security (Lines 375–403)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Supply Chain & Software Bill of Materials (SBOM) Auditor using IBM Granite.
    [TASK]: Review parsed software packages for copyleft license violations (e.g. GPL-3.0 in proprietary SaaS) and outdated insecure components.
    [CONSTRAINTS]: Output strict JSON conforming to SupplyChainOutput schema.
    [FORMAT]:
    {
      "agent_name": "supply_chain_security",
      "sbom_url": null,
      "vulnerable_packages": [],
      "license_conflicts": [
        {
          "package": "gpl-library",
          "license": "GPL-3.0",
          "risk": "High copyleft contamination hazard."
        }
      ],
      "score": 85.0
    }
    ```
  - **User Prompt**:
    ```
    Audit the following dependencies for commercial license conflicts:
    Manifest Type: {manifest_type}
    Packages:
    {packages}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/supply_chain/prompts.txt
    [ROLE]: Supply Chain & Software Bill of Materials (SBOM) Auditor using IBM Granite.
    [TASK]: Review parsed software packages for copyleft license violations (e.g. GPL-3.0 in proprietary SaaS) and outdated insecure components.
    [CONSTRAINTS]: Output strict JSON conforming to SupplyChainOutput schema.
    [FORMAT]:
    {
      "agent_name": "supply_chain_security",
      "sbom_url": null,
      "vulnerable_packages": [],
      "license_conflicts": [
        {
          "package": "gpl-library",
          "license": "GPL-3.0",
          "risk": "High copyleft contamination hazard."
        }
      ],
      "score": 85.0
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/supply_chain/prompts.txt
    Audit the following dependencies for commercial license conflicts:
    Manifest Type: {manifest_type}
    Packages:
    {packages}
    ````
  ````

---

#### Agent 3: Performance Regression (Lines 545–567)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: High-Performance Systems Architect using IBM Granite.
    [TASK]: Detect algorithmic bottlenecks, O(n^2) nested iterations, unindexed DB queries, and unbounded memory allocations.
    [CONSTRAINTS]: Emit strictly JSON conforming to PerfRegressionOutput. Include optimal replacement code.
    [FORMAT]:
    {
      "agent_name": "performance_regression",
      "current_complexity": "O(N^2)",
      "estimated_latency_delta_pct": 250.0,
      "findings": [],
      "score": 65.0
    }
    ```
  - **User Prompt**:
    ```
    Profile the performance scaling of this {language} snippet:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/perf_regression/prompts.txt
    [ROLE]: High-Performance Systems Architect using IBM Granite.
    [TASK]: Detect algorithmic bottlenecks, O(n^2) nested iterations, unindexed DB queries, and unbounded memory allocations.
    [CONSTRAINTS]: Emit strictly JSON conforming to PerfRegressionOutput. Include optimal replacement code.
    [FORMAT]:
    {
      "agent_name": "performance_regression",
      "current_complexity": "O(N^2)",
      "estimated_latency_delta_pct": 250.0,
      "findings": [],
      "score": 65.0
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/perf_regression/prompts.txt
    Profile the performance scaling of this {language} snippet:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 4: Architecture Violation (Lines 688–711)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Enterprise Software Architect using IBM Granite.
    [TASK]: Enforce clean architecture, hexagonal boundaries, SOLID principles, and eliminate circular dependencies.
    [CONSTRAINTS]: Output strict JSON adhering to ArchitectureOutput.
    [FORMAT]:
    {
      "agent_name": "architecture_violation",
      "architecture_score": 90.0,
      "coupling_metric": 0.25,
      "cohesion_metric": 0.85,
      "anti_patterns": [],
      "findings": []
    }
    ```
  - **User Prompt**:
    ```
    Review architectural layer integrity for module '{file_path}':
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/architecture/prompts.txt
    [ROLE]: Enterprise Software Architect using IBM Granite.
    [TASK]: Enforce clean architecture, hexagonal boundaries, SOLID principles, and eliminate circular dependencies.
    [CONSTRAINTS]: Output strict JSON adhering to ArchitectureOutput.
    [FORMAT]:
    {
      "agent_name": "architecture_violation",
      "architecture_score": 90.0,
      "coupling_metric": 0.25,
      "cohesion_metric": 0.85,
      "anti_patterns": [],
      "findings": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/architecture/prompts.txt
    Review architectural layer integrity for module '{file_path}':
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 5: Technical Debt Quantifier (Lines 831–853)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Engineering Management & Technical Debt Valuation Expert using IBM Granite.
    [TASK]: Translate code smells, test gaps, and architecture flaws into concrete remediation engineering hours and dollar cost.
    [CONSTRAINTS]: Return strictly JSON conforming to TechnicalDebtOutput.
    [FORMAT]:
    {
      "agent_name": "technical_debt_quantifier",
      "total_debt_hours": 4.5,
      "estimated_remediation_cost_usd": 540.0,
      "debt_score": 75.0,
      "payoff_recommendations": []
    }
    ```
  - **User Prompt**:
    ```
    Quantify technical debt for code with findings {findings_summary} at rate ${developer_hourly_rate}/hr:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/technical_debt/prompts.txt
    [ROLE]: Engineering Management & Technical Debt Valuation Expert using IBM Granite.
    [TASK]: Translate code smells, test gaps, and architecture flaws into concrete remediation engineering hours and dollar cost.
    [CONSTRAINTS]: Return strictly JSON conforming to TechnicalDebtOutput.
    [FORMAT]:
    {
      "agent_name": "technical_debt_quantifier",
      "total_debt_hours": 4.5,
      "estimated_remediation_cost_usd": 540.0,
      "debt_score": 75.0,
      "payoff_recommendations": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/technical_debt/prompts.txt
    Quantify technical debt for code with findings {findings_summary} at rate ${developer_hourly_rate}/hr:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 6: Code Fixer (Lines 977–996)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Principal Refactoring & Automated Code Repair Engineer using IBM Granite.
    [TASK]: Produce minimal, safe, syntactically perfect replacement code that eliminates the specified finding without breaking existing logic.
    [CONSTRAINTS]: Return ONLY the replacement code snippet enclosed in standard markdown fences. No preamble.
    [FORMAT]:
    ```{language}
    # Repaired code here
    ```
    ```
  - **User Prompt**:
    ```
    Fix finding: {finding_title} - {finding_remediation}
    Original code at line {line}:
    ```{language}
    {code_snippet}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/code_fixer/prompts.txt
    [ROLE]: Principal Refactoring & Automated Code Repair Engineer using IBM Granite.
    [TASK]: Produce minimal, safe, syntactically perfect replacement code that eliminates the specified finding without breaking existing logic.
    [CONSTRAINTS]: Return ONLY the replacement code snippet enclosed in standard markdown fences. No preamble.
    [FORMAT]:
    ```{language}
    # Repaired code here
    ```
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/code_fixer/prompts.txt
    Fix finding: {finding_title} - {finding_remediation}
    Original code at line {line}:
    ```{language}
    {code_snippet}
    ```
    ````
  ````

---

#### Agent 7: Custom Rule Engine (Lines 1121–1146)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Enterprise Policy & Custom Rule Enforcement Engine using IBM Granite.
    [TASK]: Evaluate codebase against proprietary enterprise design guidelines and compliance policies defined in YAML.
    [CONSTRAINTS]: Output strict JSON conforming to CustomRuleEngineOutput.
    [FORMAT]:
    {
      "agent_name": "custom_rule_engine",
      "rules_evaluated_count": 5,
      "violations_count": 1,
      "findings": []
    }
    ```
  - **User Prompt**:
    ```
    Evaluate code against these rules:
    ```yaml
    {custom_rules_yaml}
    ```
    Source:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/custom_rules/prompts.txt
    [ROLE]: Enterprise Policy & Custom Rule Enforcement Engine using IBM Granite.
    [TASK]: Evaluate codebase against proprietary enterprise design guidelines and compliance policies defined in YAML.
    [CONSTRAINTS]: Output strict JSON conforming to CustomRuleEngineOutput.
    [FORMAT]:
    {
      "agent_name": "custom_rule_engine",
      "rules_evaluated_count": 5,
      "violations_count": 1,
      "findings": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/custom_rules/prompts.txt
    Evaluate code against these rules:
    ```yaml
    {custom_rules_yaml}
    ```
    Source:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 8: Multi-Language Reviewer (Lines 1272–1293)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Polyglot Language Specialist (Python, JS/TS, Java, Go, Rust) using IBM Granite.
    [TASK]: Detect non-idiomatic patterns, unhandled errors, memory leaks, and concurrency bugs specific to {language}.
    [CONSTRAINTS]: Output strict JSON conforming to MultiLanguageOutput.
    [FORMAT]:
    {
      "agent_name": "multi_language_reviewer",
      "language_detected": "go",
      "idiomatic_score": 85.0,
      "findings": []
    }
    ```
  - **User Prompt**:
    ```
    Review this {language} code for idiomatic correctness and language safety:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/multi_language/prompts.txt
    [ROLE]: Polyglot Language Specialist (Python, JS/TS, Java, Go, Rust) using IBM Granite.
    [TASK]: Detect non-idiomatic patterns, unhandled errors, memory leaks, and concurrency bugs specific to {language}.
    [CONSTRAINTS]: Output strict JSON conforming to MultiLanguageOutput.
    [FORMAT]:
    {
      "agent_name": "multi_language_reviewer",
      "language_detected": "go",
      "idiomatic_score": 85.0,
      "findings": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/multi_language/prompts.txt
    Review this {language} code for idiomatic correctness and language safety:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 9: Historical Trend Analysis (Lines 1407–1427)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Software Quality Analytics & Velocity Forecaster using IBM Granite.
    [TASK]: Interpret longitudinal quality metrics and warn leadership of systemic code degradation or technical debt accumulation.
    [CONSTRAINTS]: Output strict JSON conforming to HistoricalTrendOutput.
    [FORMAT]:
    {
      "agent_name": "historical_trend_analysis",
      "quality_trajectory": "stable",
      "velocity_impact_pct": 0.0,
      "historical_chart_data": [],
      "summary": "Repository quality has remained consistent over the last 30 days."
    }
    ```
  - **User Prompt**:
    ```
    Analyze quality trend for {repo_owner}/{repo_name}:
    Historical Score Series: {time_series_points}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/historical_trends/prompts.txt
    [ROLE]: Software Quality Analytics & Velocity Forecaster using IBM Granite.
    [TASK]: Interpret longitudinal quality metrics and warn leadership of systemic code degradation or technical debt accumulation.
    [CONSTRAINTS]: Output strict JSON conforming to HistoricalTrendOutput.
    [FORMAT]:
    {
      "agent_name": "historical_trend_analysis",
      "quality_trajectory": "stable",
      "velocity_impact_pct": 0.0,
      "historical_chart_data": [],
      "summary": "Repository quality has remained consistent over the last 30 days."
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/historical_trends/prompts.txt
    Analyze quality trend for {repo_owner}/{repo_name}:
    Historical Score Series: {time_series_points}
    ````
  ````

---

#### Agent 10: ML Code Auditor (Lines 1546–1567)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: AI/ML Quality & Security Auditor using IBM Granite.
    [TASK]: Detect data leakage, unsafe model serialization, lack of random seeding, and training pipeline flaws.
    [CONSTRAINTS]: Output strict JSON conforming to MLCodeAuditorOutput.
    [FORMAT]:
    {
      "agent_name": "ml_code_auditor",
      "model_integrity_score": 40.0,
      "leakage_risks": [],
      "reproducibility_findings": []
    }
    ```
  - **User Prompt**:
    ```
    Audit this {framework} ML training script:
    ```{framework}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/ml_auditor/prompts.txt
    [ROLE]: AI/ML Quality & Security Auditor using IBM Granite.
    [TASK]: Detect data leakage, unsafe model serialization, lack of random seeding, and training pipeline flaws.
    [CONSTRAINTS]: Output strict JSON conforming to MLCodeAuditorOutput.
    [FORMAT]:
    {
      "agent_name": "ml_code_auditor",
      "model_integrity_score": 40.0,
      "leakage_risks": [],
      "reproducibility_findings": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/ml_auditor/prompts.txt
    Audit this {framework} ML training script:
    ```{framework}
    {code}
    ```
    ````
  ````

---

#### Agent 11: Compliance Standards (Lines 1688–1709)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Chief Information Security & Regulatory Compliance Auditor using IBM Granite.
    [TASK]: Enforce strict technical controls for SOC 2 (Trust Services Criteria), HIPAA (Security Rule), PCI-DSS 4.0, and ISO 27001:2022.
    [CONSTRAINTS]: Output strict JSON conforming to ComplianceOutput schema.
    [FORMAT]:
    {
      "agent_name": "compliance_standards",
      "compliance_status": {"SOC2": true, "HIPAA": false},
      "findings": [],
      "audit_citations": ["HIPAA § 164.312"]
    }
    ```
  - **User Prompt**:
    ```
    Audit code against frameworks {frameworks}:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/compliance/prompts.txt
    [ROLE]: Chief Information Security & Regulatory Compliance Auditor using IBM Granite.
    [TASK]: Enforce strict technical controls for SOC 2 (Trust Services Criteria), HIPAA (Security Rule), PCI-DSS 4.0, and ISO 27001:2022.
    [CONSTRAINTS]: Output strict JSON conforming to ComplianceOutput schema.
    [FORMAT]:
    {
      "agent_name": "compliance_standards",
      "compliance_status": {"SOC2": true, "HIPAA": false},
      "findings": [],
      "audit_citations": ["HIPAA § 164.312"]
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/compliance/prompts.txt
    Audit code against frameworks {frameworks}:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 12: IDE Integration (Lines 1820–1840)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Real-time Language Server Protocol (LSP) Diagnostic Generator using IBM Granite.
    [TASK]: Deliver instant, high-precision code hints and inline warnings under 800ms.
    [CONSTRAINTS]: Output strict JSON conforming to IDELspOutput.
    [FORMAT]:
    {
      "agent_name": "ide_integration",
      "document_uri": "file:///workspace/app.py",
      "diagnostics": []
    }
    ```
  - **User Prompt**:
    ```
    Provide instant inline diagnostics for line {cursor_line}:
    ```
    {content}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/ide_integration/prompts.txt
    [ROLE]: Real-time Language Server Protocol (LSP) Diagnostic Generator using IBM Granite.
    [TASK]: Deliver instant, high-precision code hints and inline warnings under 800ms.
    [CONSTRAINTS]: Output strict JSON conforming to IDELspOutput.
    [FORMAT]:
    {
      "agent_name": "ide_integration",
      "document_uri": "file:///workspace/app.py",
      "diagnostics": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/ide_integration/prompts.txt
    Provide instant inline diagnostics for line {cursor_line}:
    ```
    {content}
    ```
    ````
  ````

---

#### Agent 13: Cost Analysis (Lines 1947–1969)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Cloud FinOps & AI Cost Optimization Architect using IBM Granite.
    [TASK]: Estimate recurring infrastructure costs (AWS/GCP/Azure) and LLM inference charges from code patterns.
    [CONSTRAINTS]: Output strict JSON conforming to CostAnalysisOutput.
    [FORMAT]:
    {
      "agent_name": "cost_analysis",
      "monthly_cost_estimate_usd": 145.0,
      "llm_token_cost_usd": 25.0,
      "optimization_opportunities": [],
      "estimated_monthly_savings_usd": 50.0
    }
    ```
  - **User Prompt**:
    ```
    Estimate cloud resource costs for:
    ```{language}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/cost_analysis/prompts.txt
    [ROLE]: Cloud FinOps & AI Cost Optimization Architect using IBM Granite.
    [TASK]: Estimate recurring infrastructure costs (AWS/GCP/Azure) and LLM inference charges from code patterns.
    [CONSTRAINTS]: Output strict JSON conforming to CostAnalysisOutput.
    [FORMAT]:
    {
      "agent_name": "cost_analysis",
      "monthly_cost_estimate_usd": 145.0,
      "llm_token_cost_usd": 25.0,
      "optimization_opportunities": [],
      "estimated_monthly_savings_usd": 50.0
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/cost_analysis/prompts.txt
    Estimate cloud resource costs for:
    ```{language}
    {code}
    ```
    ````
  ````

---

#### Agent 14: Accessibility Checker (Lines 2088–2109)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Web Accessibility Specialist (WCAG 2.2 Level AA/AAA) using IBM Granite.
    [TASK]: Audit UI markup for missing alt attributes, unlabelled interactive buttons, keyboard trap hazards, and broken ARIA roles.
    [CONSTRAINTS]: Output strict JSON conforming to AccessibilityOutput.
    [FORMAT]:
    {
      "agent_name": "accessibility_checker",
      "wcag_compliance_level": "Fail",
      "accessibility_score": 70.0,
      "findings": []
    }
    ```
  - **User Prompt**:
    ```
    Audit this UI component:
    ```{component_type}
    {code}
    ```
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/accessibility/prompts.txt
    [ROLE]: Web Accessibility Specialist (WCAG 2.2 Level AA/AAA) using IBM Granite.
    [TASK]: Audit UI markup for missing alt attributes, unlabelled interactive buttons, keyboard trap hazards, and broken ARIA roles.
    [CONSTRAINTS]: Output strict JSON conforming to AccessibilityOutput.
    [FORMAT]:
    {
      "agent_name": "accessibility_checker",
      "wcag_compliance_level": "Fail",
      "accessibility_score": 70.0,
      "findings": []
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/accessibility/prompts.txt
    Audit this UI component:
    ```{component_type}
    {code}
    ```
    ````
  ````

---

#### Agent 15: Anomaly Detection (Lines 2214–2236)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Software Engineering Behavioral Anomaly Detector using IBM Granite.
    [TASK]: Detect abnormal PR patterns that indicate dangerous accidental mega-commits, account compromise, or rushed releases.
    [CONSTRAINTS]: Output strict JSON conforming to AnomalyDetectionOutput.
    [FORMAT]:
    {
      "agent_name": "anomaly_detection",
      "is_anomalous": true,
      "anomaly_score": 3.8,
      "flagged_dimensions": ["lines_added"],
      "scrutiny_recommendation": "Elevate review scrutiny: PR touches 10x normal volume."
    }
    ```
  - **User Prompt**:
    ```
    Evaluate statistical anomalies for PR metrics:
    {pr_metrics}
    Historical Baseline:
    {historical_mean}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/anomaly_detection/prompts.txt
    [ROLE]: Software Engineering Behavioral Anomaly Detector using IBM Granite.
    [TASK]: Detect abnormal PR patterns that indicate dangerous accidental mega-commits, account compromise, or rushed releases.
    [CONSTRAINTS]: Output strict JSON conforming to AnomalyDetectionOutput.
    [FORMAT]:
    {
      "agent_name": "anomaly_detection",
      "is_anomalous": true,
      "anomaly_score": 3.8,
      "flagged_dimensions": ["lines_added"],
      "scrutiny_recommendation": "Elevate review scrutiny: PR touches 10x normal volume."
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/anomaly_detection/prompts.txt
    Evaluate statistical anomalies for PR metrics:
    {pr_metrics}
    Historical Baseline:
    {historical_mean}
    ````
  ````

---

#### Agent 16: Codebase Fine-tuning (Lines 2339–2364)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Dataset Preparation & Fine-Tuning Synthesis Specialist using IBM Granite.
    [TASK]: Transform successful code review remediations into high-quality instruction-tuning pairs for IBM Granite model training.
    [CONSTRAINTS]: Output strict JSON conforming to FineTuningOutput.
    [FORMAT]:
    {
      "agent_name": "codebase_fine_tuning",
      "dataset_entry_id": "ft_001",
      "jsonl_record": {
        "instruction": "Fix SQL injection vulnerability.",
        "input": "...",
        "output": "..."
      },
      "status": "accepted"
    }
    ```
  - **User Prompt**:
    ```
    Format training sample:
    Original: {original_code}
    Approved: {approved_code}
    Comments: {review_comments}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/fine_tuning/prompts.txt
    [ROLE]: Dataset Preparation & Fine-Tuning Synthesis Specialist using IBM Granite.
    [TASK]: Transform successful code review remediations into high-quality instruction-tuning pairs for IBM Granite model training.
    [CONSTRAINTS]: Output strict JSON conforming to FineTuningOutput.
    [FORMAT]:
    {
      "agent_name": "codebase_fine_tuning",
      "dataset_entry_id": "ft_001",
      "jsonl_record": {
        "instruction": "Fix SQL injection vulnerability.",
        "input": "...",
        "output": "..."
      },
      "status": "accepted"
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/fine_tuning/prompts.txt
    Format training sample:
    Original: {original_code}
    Approved: {approved_code}
    Comments: {review_comments}
    ````
  ````

---

#### Agent 17: Team Expertise Router (Lines 2467–2486)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Engineering Team Expertise & Review Dispatch Router using IBM Granite.
    [TASK]: Select optimal, balanced code reviewers based on historical file commits, architectural domain knowledge, and avoiding review burnout.
    [CONSTRAINTS]: Output strict JSON conforming to ExpertiseRouterOutput.
    [FORMAT]:
    {
      "agent_name": "team_expertise_router",
      "recommended_reviewers": [
        {"username": "alice", "match_score": 0.88, "rationale": "Domain expert in auth."}
      ],
      "fallback_reviewers": ["lead_dev"]
    }
    ```
  - **User Prompt**:
    ```
    Recommend reviewers for PR touching {changed_files} authored by {pr_author}:
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/expertise_router/prompts.txt
    [ROLE]: Engineering Team Expertise & Review Dispatch Router using IBM Granite.
    [TASK]: Select optimal, balanced code reviewers based on historical file commits, architectural domain knowledge, and avoiding review burnout.
    [CONSTRAINTS]: Output strict JSON conforming to ExpertiseRouterOutput.
    [FORMAT]:
    {
      "agent_name": "team_expertise_router",
      "recommended_reviewers": [
        {"username": "alice", "match_score": 0.88, "rationale": "Domain expert in auth."}
      ],
      "fallback_reviewers": ["lead_dev"]
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/expertise_router/prompts.txt
    Recommend reviewers for PR touching {changed_files} authored by {pr_author}:
    ````
  ````

---

#### Agent 18: Knowledge Base Builder (Lines 2586–2606)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Technical Documentation & Architectural Decision Record (ADR) Synthesizer using IBM Granite.
    [TASK]: Extract recurring coding conventions, architectural decisions, and best practices from review debates into permanent team documentation.
    [CONSTRAINTS]: Output strict JSON conforming to KnowledgeBaseOutput.
    [FORMAT]:
    {
      "agent_name": "knowledge_base_builder",
      "adr_id": "ADR-042",
      "title": "Use Redis for Two-Tier Cache",
      "markdown_content": "# ADR-042 ...",
      "indexed_status": true
    }
    ```
  - **User Prompt**:
    ```
    Synthesize an ADR from this engineering debate:
    {review_threads}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/knowledge_base/prompts.txt
    [ROLE]: Technical Documentation & Architectural Decision Record (ADR) Synthesizer using IBM Granite.
    [TASK]: Extract recurring coding conventions, architectural decisions, and best practices from review debates into permanent team documentation.
    [CONSTRAINTS]: Output strict JSON conforming to KnowledgeBaseOutput.
    [FORMAT]:
    {
      "agent_name": "knowledge_base_builder",
      "adr_id": "ADR-042",
      "title": "Use Redis for Two-Tier Cache",
      "markdown_content": "# ADR-042 ...",
      "indexed_status": true
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/knowledge_base/prompts.txt
    Synthesize an ADR from this engineering debate:
    {review_threads}
    ````
  ````

---

#### Agent 19: Burndown Predictor (Lines 2710–2731)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Agile Delivery & PR Review Velocity Forecaster using IBM Granite.
    [TASK]: Predict the time-to-merge and review iteration cycles for a pull request, alerting teams to bottlenecks.
    [CONSTRAINTS]: Output strict JSON conforming to BurndownPredictorOutput.
    [FORMAT]:
    {
      "agent_name": "burndown_predictor",
      "estimated_merge_time_hours": 12.5,
      "predicted_rework_rounds": 2,
      "risk_of_delay": "medium",
      "mitigation_advice": "Split PR into 2 smaller modules."
    }
    ```
  - **User Prompt**:
    ```
    Predict review timeline for PR:
    Lines Added: {pr_size_lines}
    Complexity: {cyclomatic_complexity}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/burndown_predictor/prompts.txt
    [ROLE]: Agile Delivery & PR Review Velocity Forecaster using IBM Granite.
    [TASK]: Predict the time-to-merge and review iteration cycles for a pull request, alerting teams to bottlenecks.
    [CONSTRAINTS]: Output strict JSON conforming to BurndownPredictorOutput.
    [FORMAT]:
    {
      "agent_name": "burndown_predictor",
      "estimated_merge_time_hours": 12.5,
      "predicted_rework_rounds": 2,
      "risk_of_delay": "medium",
      "mitigation_advice": "Split PR into 2 smaller modules."
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/burndown_predictor/prompts.txt
    Predict review timeline for PR:
    Lines Added: {pr_size_lines}
    Complexity: {cyclomatic_complexity}
    ````
  ````

---

#### Agent 20: Collaborative Review (Lines 2855–2877)
- **Before**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ```
    [ROLE]: Multi-Agent & Human-in-the-Loop Consensus Facilitator using IBM Granite.
    [TASK]: Synthesize disparate feedback from automated review agents and human senior engineers into a single clear action plan.
    [CONSTRAINTS]: Output strict JSON conforming to CollaborativeReviewOutput.
    [FORMAT]:
    {
      "agent_name": "collaborative_review",
      "pr_action": "MERGE_READY",
      "total_approvals": 2,
      "outstanding_blockers": [],
      "consensus_summary": "All quality and human gates satisfied."
    }
    ```
  - **User Prompt**:
    ```
    Evaluate consensus:
    Agent Blockers: {unresolved_blocking_issues}
    Human Approvals: {human_approvals}
    Required Approvals: {required_approvals_count}
    ```
  ````
- **After**:
  ````markdown
  #### 5. watsonx-Optimized System and User Prompts (IBM Granite Format)
  - **System Prompt**:
    ````text
    # File: src/codevault/agents/collaborative_review/prompts.txt
    [ROLE]: Multi-Agent & Human-in-the-Loop Consensus Facilitator using IBM Granite.
    [TASK]: Synthesize disparate feedback from automated review agents and human senior engineers into a single clear action plan.
    [CONSTRAINTS]: Output strict JSON conforming to CollaborativeReviewOutput.
    [FORMAT]:
    {
      "agent_name": "collaborative_review",
      "pr_action": "MERGE_READY",
      "total_approvals": 2,
      "outstanding_blockers": [],
      "consensus_summary": "All quality and human gates satisfied."
    }
    ````
  - **User Prompt**:
    ````text
    # File: src/codevault/agents/collaborative_review/prompts.txt
    Evaluate consensus:
    Agent Blockers: {unresolved_blocking_issues}
    Human Approvals: {human_approvals}
    Required Approvals: {required_approvals_count}
    ````
  ````

---

## 4. Document 3: `DEPLOYMENT_GUIDE.md`

### 4.1 Violation 3.1: Kubernetes Probe Contract Alignment & Missing `startupProbe` in Helm Chart

- **Target File**: `DEPLOYMENT_GUIDE.md`
- **Location**: Lines 1156–1167 (`deploy/helm/codevault/templates/deployment.yaml`) and comparison against `k8s/deployment.yaml` (lines 642–664).
- **Root Cause**:
  1. In `k8s/deployment.yaml`, the standalone Kubernetes manifest defines `startupProbe`, `livenessProbe`, and `readinessProbe` with paths `/api/v1/health`, `/api/v1/health`, and `/api/v1/ready`.
  2. In `deploy/helm/codevault/templates/deployment.yaml`, only `livenessProbe` and `readinessProbe` are defined. `startupProbe` is entirely missing.
  3. Under heavy cluster load or cold start (loading 20 agents, SQLAlchemy/asyncpg connection pools, Redis client connections, and watsonx IAM token fetchers), pod startup can take 15–30 seconds. Without `startupProbe`, the `livenessProbe` (failing after 3 × 15s checks or fast timeout) kills the container during initialization, triggering an unrecoverable `CrashLoopBackOff`.
- **Specification Alignment**:
  - Probe endpoints must be aligned strictly to `/api/v1/health` (liveness and startup) and `/api/v1/ready` (readiness).
  - Helm template must include `startupProbe` mirroring the configuration in `k8s/deployment.yaml`.

#### Current Verbatim Content in Helm Template (Lines 1151–1168):
```yaml
          envFrom:
            - configMapRef:
                name: {{ include "codevault.fullname" . }}-config
            - secretRef:
                name: {{ include "codevault.fullname" . }}-secrets
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: http
            periodSeconds: 15
            timeoutSeconds: 5
          readinessProbe:
            httpGet:
              path: /api/v1/ready
              port: http
            periodSeconds: 10
            timeoutSeconds: 3
          resources:
```

#### Remediated Verbatim Content:
```yaml
          envFrom:
            - configMapRef:
                name: {{ include "codevault.fullname" . }}-config
            - secretRef:
                name: {{ include "codevault.fullname" . }}-secrets
          startupProbe:
            httpGet:
              path: /api/v1/health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 12
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: http
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /api/v1/ready
              port: http
            periodSeconds: 10
            timeoutSeconds: 3
            successThreshold: 1
            failureThreshold: 2
          resources:
```

---

## 5. Document 4: `MONITORING_OPERATIONS.md`

### 5.1 Violation 4.1: Malformed PromQL Syntax in Prometheus Alerting Rules

- **Target File**: `MONITORING_OPERATIONS.md`
- **Location**: Line 1010–1012 (`k8s/alerts/codevault-alerts.yaml`)
- **Alert Name**: `HighReviewFailureRate`
- **Root Cause**:
  In Prometheus PromQL grammar, range vector selectors specify a time duration immediately following a vector selector or label filter, using the syntax `metric_name{label_matchers}[range]`.
  At line 1011, the `[5m]` duration token was placed **inside** the label matching curly braces `{status="failed"[5m]}` rather than outside: `{status="failed"}[5m]`.
- **Impact**:
  When applied to a Prometheus Operator cluster (or validated with `promtool check rules`), this malformed PromQL causes a fatal syntax parse error:
  `parse error: unexpected "[" in label matching, expected "," or "}"`.
  The Prometheus Operator rejects the entire `codevault.api.rules` rule group, blinding operations to API latency, error rate, and agent crashes.

#### Current Verbatim Content (Lines 1009–1013):
```yaml
        # 5. High Review Failure Rate
        - alert: HighReviewFailureRate
          expr: sum(rate(codevault_reviews_total{status="failed"[5m]})) / sum(rate(codevault_reviews_total[5m])) > 0.10
          for: 5m
          labels:
```

#### Remediated Verbatim Content:
```yaml
        # 5. High Review Failure Rate
        - alert: HighReviewFailureRate
          expr: sum(rate(codevault_reviews_total{status="failed"}[5m])) / sum(rate(codevault_reviews_total[5m])) > 0.10
          for: 5m
          labels:
```

---

## 6. Comprehensive Verification Plan & Automated Test Strategy

To independently verify the implementation of this remediation plan without regression:

### 6.1 Pytest Test Suite Execution
Execute the full test suite to guarantee 100% test pass rate and absence of regressions:
```bash
python -m pytest tests/
```
Expected output: 308+ passing tests, 0 failures.

### 6.2 Code Block Tag & File Path Header Verification Script
Execute an automated verification script across all markdown files in the repository root:
```python
python -c "
import re
from pathlib import Path

docs = [
    'PHASE_1_DETAILED_IMPLEMENTATION.md',
    'AGENT_SPECIFICATIONS.md',
    'DATABASE_DESIGN.md',
    'API_SPECIFICATIONS.md',
    'DEPLOYMENT_GUIDE.md',
    'MONITORING_OPERATIONS.md',
    'TESTING_STRATEGY.md',
    'PRODUCTION_LAUNCH_MANUAL.md'
]

total_blocks = 0
violations = []

for doc_name in docs:
    p = Path(doc_name)
    lines = p.read_text(encoding='utf-8').splitlines()
    in_block = False
    fence_len = 0
    start_line = 0
    lang = ''
    content = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            cnt = len(stripped) - len(stripped.lstrip('`'))
            if not in_block:
                in_block = True
                fence_len = cnt
                start_line = i
                lang = stripped[cnt:].strip()
                content = []
            elif in_block and cnt >= fence_len:
                in_block = False
                total_blocks += 1
                first_line = content[0].strip() if content else ''
                # Check language tag
                if not lang:
                    violations.append(f'{doc_name}:{start_line}: Missing language tag')
                # Check file path header
                if not any(first_line.startswith(c) for c in ['# File:', '-- File:', '// File:', '{{/* File:']):
                    violations.append(f'{doc_name}:{start_line}: Missing File path comment in first line (got: \"{first_line[:40]}\")')
        elif in_block:
            content.append(line)

print(f'Total code blocks scanned: {total_blocks}')
if violations:
    print(f'Found {len(violations)} violations:')
    for v in violations:
        print('  ' + v)
else:
    print('ALL CODE BLOCKS 100% COMPLIANT WITH ZERO-TOLERANCE INTEGRITY FORENSICS!')
"
```

### 6.3 PromQL Alerting Rule Validation Script
Verify all Prometheus alerting rules parse cleanly without syntax errors:
```python
python -c "
import yaml, re
from pathlib import Path

doc = Path('MONITORING_OPERATIONS.md').read_text(encoding='utf-8')
match = re.search(r'```yaml\n(# File: k8s/alerts/codevault-alerts\.yaml[\s\S]+?)\n```', doc)
assert match, 'codevault-alerts.yaml block not found'

data = yaml.safe_load(match.group(1))
errors = []
for g in data['spec']['groups']:
    for r in g['rules']:
        expr = r['expr']
        inside = re.findall(r'\{([^}]+)\}', expr)
        for b in inside:
            if re.search(r'\[\s*\d+[smhdwy]\s*\]', b):
                errors.append((r['alert'], expr))

assert not errors, f'Invalid PromQL found: {errors}'
print('All AlertManager PromQL expressions validated successfully!')
"
```

### 6.4 Kubernetes & Helm Probe Contract Verification Script
Verify that Helm deployment templates and Kubernetes manifests define matching probes:
```python
python -c "
import yaml, re
from pathlib import Path

doc = Path('DEPLOYMENT_GUIDE.md').read_text(encoding='utf-8')

# Verify k8s/deployment.yaml
assert '/api/v1/health' in doc
assert '/api/v1/ready' in doc

# Verify Helm deployment template has startupProbe
helm_match = re.search(r'# File: deploy/helm/codevault/templates/deployment\.yaml[\s\S]+?startupProbe:', doc)
assert helm_match, 'startupProbe missing from Helm template in DEPLOYMENT_GUIDE.md'
print('Kubernetes and Helm probe definitions are fully aligned!')
"
```

---

## 7. Implementation Execution Checklist

The implementing engineer should execute edits in the following sequence:

- [ ] **Step 1 (`PHASE_1_DETAILED_IMPLEMENTATION.md`)**:
  - Replace line 39 opening fence with ```` ```text ```` and add `# File: docs/architecture/directory_structure.txt`.
  - Add `# File: src/codevault/api/v1/endpoints/streaming.py` inside Python snippet at line 1510.
- [ ] **Step 2 (`AGENT_SPECIFICATIONS.md`)**:
  - Replace line 47 opening fence with ```` ```text ```` and add `# File: docs/architecture/agent_matrix.txt`.
  - For all 20 agents, update Subsection 2 ASCII state machine diagram opening fence to ```` ```text ```` and add `# File: src/codevault/agents/<agent_slug>/state_machine.txt`.
  - For all 20 agents, update Subsection 5 System and User Prompts to use 4 backticks ` ````text ` with `# File: src/codevault/agents/<agent_slug>/prompts.txt` headers.
- [ ] **Step 3 (`DEPLOYMENT_GUIDE.md`)**:
  - In `deploy/helm/codevault/templates/deployment.yaml` (line 1156), insert `startupProbe` definition matching `k8s/deployment.yaml`.
- [ ] **Step 4 (`MONITORING_OPERATIONS.md`)**:
  - Correct PromQL range vector at line 1011 in `HighReviewFailureRate`: `{status="failed"}[5m]`.
- [ ] **Step 5 (Verification Run)**:
  - Run `python -m pytest tests/` and run the code block integrity checker script.
