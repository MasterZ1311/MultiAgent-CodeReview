# 🧠 IBM watsonx.ai Integration Guide

This guide details how **cerberus</>** integrates with **IBM watsonx.ai** and **IBM Granite Foundation Models** for enterprise multi-agent code analysis and automated quality assurance.

---

## 🏛️ Architecture & Model Routing

`cerberus</>` is designed with an adaptive multi-tier intelligence pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                 cerberus Review Coordinator                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   ┌─────────────────┐                  ┌──────────────────┐
   │  IBM watsonx.ai │                  │ Heuristic & AST  │
   │ Foundation Model│                  │ Static Engine    │
   └────────┬────────┘                  └────────┬─────────┘
            │ (If Keys Configured)               │ (Zero-Config Default)
            ▼                                    ▼
┌───────────────────────┐              ┌───────────────────┐
│ Granite-13b-chat-v2   │              │ Sub-10ms          │
│ Granite-3-8b-instruct │              │ Deterministic AST │
│ Granite-20b-code      │              │ Zero API Quotas   │
└───────────────────────┘              └───────────────────┘
```

### Supported Granite Foundation Models
1. **`ibm/granite-3-8b-instruct`** *(Default)*: High-throughput, optimized for code reasoning, instruction following, and AST alignment.
2. **`ibm/granite-3-2b-instruct`**: Lightweight, ultra-low latency instruction model.
3. **`ibm/granite-20b-code-instruct`**: Specialized for enterprise multi-lingual code refactoring and compliance.

---

## 🔑 Provisioning Credentials on IBM Cloud

To use live watsonx foundation models:

1. **Log in to IBM Cloud**: Go to [https://cloud.ibm.com](https://cloud.ibm.com).
2. **Provision watsonx.ai**: Navigate to the catalog and create a **watsonx.ai** instance (available in Dallas `us-south`, Frankfurt `eu-de`, or Tokyo `jp-tok`).
3. **Obtain API Key**:
   - Go to **Manage** > **Access (IAM)** > **API keys**.
   - Click **Create an IBM Cloud API key**, name it `cerberus-demo-key`, and copy the secret key.
4. **Obtain Project ID**:
   - Open **watsonx** at [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com).
   - Create or select an existing project (e.g. `MultiAgent-CodeReview`).
   - Go to the **Manage** tab > **General** > copy the **Project ID** GUID.

---

## ⚙️ Configuration in `.env`

Add your credentials to `.env`:

```bash
# Set provider to watsonx
LLM_PROVIDER=watsonx

# IBM Cloud Credentials
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_guid_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model selection (Optional, defaults to ibm/granite-3-8b-instruct)
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

---

## 🛡️ Zero-Downtime Graceful Fallback

`cerberus</>` implements an automatic fallback mechanism:

```python
# cerberus/providers/watsonx_provider.py
async def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
    if not await self.is_available():
        logger.debug("IBM watsonx credentials not configured; deferring to heuristic evaluator.")
        return None
    # Live REST call to IBM watsonx foundation models endpoint...
```

- **If credentials are not present**: The system immediately falls back to `HeuristicEngine` without throwing errors or blocking reviews.
- **If the network drops or API rate limit is reached**: The review completes with AST-analyzed findings, maintaining 100% demo availability.

---

## 🧪 Verifying the Integration

### 1. Test via CLI
```bash
# Check if provider is recognized
python -m cerberus.cli health

# Run review with watsonx enabled
python -m cerberus.cli review --snippet "def query(uid): return db.execute(f'SELECT * FROM users WHERE id = {uid}')"
```

### 2. Test via REST API
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def transfer(src, dst, amt):\n    db.execute(f\"UPDATE acc SET bal = bal - {amt} WHERE id = {src}\")",
    "language": "python",
    "agents": ["security", "compliance"]
  }'
```

---

## 📊 Comparison: watsonx vs. Heuristic Engine

| Feature | IBM watsonx.ai (Granite) | Heuristic & AST Engine |
| :--- | :--- | :--- |
| **Execution Mode** | Cloud-based Neural Inference | Local Python AST & Regex |
| **Typical Latency** | 400ms – 1,200ms | 3ms – 12ms |
| **API Key Required** | Yes (`WATSONX_API_KEY`) | **No (Zero-Config)** |
| **Offline / Air-Gapped** | Requires private VPC / satellite | **100% Offline Capable** |
| **Output Determinism** | Low temperature (0.1) probabilistic | 100% Deterministic & Verifiable |
| **OWASP & CWE IDs** | Contextual explanations | Hardcoded standard mappings |
| **Demo Suitability** | High-level executive presentation | Guaranteed zero-fail backup |
