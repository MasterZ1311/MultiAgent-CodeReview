#!/usr/bin/env bash
# ==============================================================================
# cerberus</> Enterprise Multi-Agent Code Review — Live Demo Curl Scripts
# ==============================================================================

BASE_URL="http://localhost:8000"
API_KEY="cvai_dev_key_123"

echo "=========================================================="
echo "1. Health & Cluster Status Check"
echo "=========================================================="
curl -s -X GET "${BASE_URL}/api/v1/health" | jq .

echo -e "\n=========================================================="
echo "2. Active Agent Ecosystem Inspection"
echo "=========================================================="
curl -s -X GET "${BASE_URL}/api/v1/agents" \
  -H "Authorization: Bearer ${API_KEY}" | jq .

echo -e "\n=========================================================="
echo "3. Scenario 1: Critical Security Audit (SQL Injection + Secrets)"
echo "=========================================================="
curl -s -X POST "${BASE_URL}/api/v1/review" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "API_KEY = \"sk-live-98213847291038291029381\"\ndef get_user(uid):\n    return db.execute(f\"SELECT * FROM users WHERE id = {uid}\")",
    "language": "python",
    "agents": ["security", "compliance"]
  }' | jq '{review_id: .review_id, overall_score: .overall_score, critical_issues: .critical_issues}'

echo -e "\n=========================================================="
echo "4. Scenario 2: Algorithmic & DB Bottlenecks (O(n²) + N+1)"
echo "=========================================================="
curl -s -X POST "${BASE_URL}/api/v1/review" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process(items):\n    for i in items:\n        for j in items:\n            pass\n    for item in items:\n        cursor.execute(\"SELECT * FROM t WHERE id = \" + str(item))",
    "language": "python",
    "agents": ["performance"]
  }' | jq '{review_id: .review_id, overall_score: .overall_score, warnings: .warnings}'

echo -e "\n=========================================================="
echo "5. Scenario 3: Healthcare HIPAA & Privacy Compliance"
echo "=========================================================="
curl -s -X POST "${BASE_URL}/api/v1/review" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import logging\nlogger = logging.getLogger(\"audit\")\ndef export(ssn, name):\n    logger.info(f\"Record: {name}, SSN: {ssn}\")\n    return f\"http://api.health.org/sync?ssn={ssn}\"",
    "language": "python",
    "agents": ["compliance"]
  }' | jq '{review_id: .review_id, overall_score: .overall_score, critical_issues: .critical_issues, warnings: .warnings}'

echo -e "\n=========================================================="
echo "6. Scenario 4: Concurrent Batch Code Review (Multi-File)"
echo "=========================================================="
curl -s -X POST "${BASE_URL}/api/v1/review/batch" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"filename": "auth.py", "code": "import os\ndef login(): pass", "language": "python"},
      {"filename": "db.py", "code": "def query(): return db.execute(\"SELECT * FROM users\")", "language": "python"},
      {"filename": "calc.py", "code": "def add(a, b): return a + b", "language": "python"}
    ]
  }' | jq '{batch_id: .batch_id, total_files: .total_files}'

echo -e "\n=========================================================="
echo "7. Prometheus Telemetry Metrics"
echo "=========================================================="
curl -s "${BASE_URL}/metrics" | grep -E "cerberus_review|cerberus_findings" | head -n 15
