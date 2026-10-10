"""
cerberus</> Demo Scenarios Catalog.
Pre-configured code snippets designed to trigger specialized agents during live demos.
"""

from typing import Dict, Any, List

SCENARIO_1_SECURITY = {
    "name": "Scenario 1: Critical Security Vulnerabilities (CWE-89, CWE-798, CWE-78)",
    "description": "Triggers Security Agent and Compliance Agent (SOC 2 CC6.1) with SQL injection, API keys, and shell execution.",
    "agents": ["security", "compliance"],
    "expected_findings": ["SQL Injection", "Hardcoded Credentials", "Command Injection"],
    "code": """import os
import sqlite3

# Critical: Hardcoded high-entropy secret
API_KEY = "sk-live-98213847291038291029381"
DB_PASS = "admin123"

def get_user_profile(user_id):
    # Critical: SQL Injection via f-string dynamic query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    return cursor.execute(query).fetchall()

def run_diagnostic(target_host):
    # Critical: Operating system command injection
    os.system("ping -c 1 " + target_host)
"""
}

SCENARIO_2_PERFORMANCE = {
    "name": "Scenario 2: Algorithmic & Database Bottlenecks (O(n²), N+1 Query)",
    "description": "Triggers Performance Agent with quadratic complexity, memory leak allocations, and iterative DB queries.",
    "agents": ["performance"],
    "expected_findings": ["Quadratic Time Complexity", "Repeated In-Place String Concatenation", "N+1 Query Pattern"],
    "code": """import sqlite3

def find_duplicates_and_summarize(items):
    # Performance Issue 1: O(n²) Quadratic nested loop
    duplicates = []
    for i in items:
        for j in items:
            if i == j and i not in duplicates:
                duplicates.append(i)

    # Performance Issue 2: In-place string concatenation in loop creates intermediate allocations
    summary_report = ""
    for item in duplicates:
        summary_report += ","

    # Performance Issue 3: Database N+1 query inside loop
    for dup in duplicates:
        cursor.execute("SELECT * FROM audit_log WHERE item_id = " + str(dup))

    return summary_report
"""
}

SCENARIO_3_COMPLIANCE = {
    "name": "Scenario 3: Healthcare & Privacy Compliance Violations (HIPAA, GDPR)",
    "description": "Triggers Compliance Agent across HIPAA 45 CFR §164.312 and GDPR Articles 5, 25.",
    "agents": ["compliance"],
    "expected_findings": ["HIPAA Violation: PHI", "Cleartext HTTP", "GDPR Data Minimization", "Plaintext PII in URL"],
    "code": """import logging
import requests

logger = logging.getLogger("patient_pipeline")

def dispatch_patient_record(ssn: str, full_name: str, medical_diagnosis: str):
    # HIPAA Violation: ePHI emitted to unmasked application logs
    logger.info(f"Dispatching record for {full_name}, SSN: {ssn}, Diagnosis: {medical_diagnosis}")

    # HIPAA In-Transit Encryption Violation (Cleartext HTTP) & GDPR URL PII exposure
    endpoint = f"http://api.regional-health.org/sync?ssn={ssn}&name={full_name}"
    
    # GDPR Data Minimization Violation (Unbounded SELECT * on user table)
    query = "SELECT * FROM users WHERE status = 'active'"
    
    response = requests.get(endpoint)
    return response.status_code
"""
}

SCENARIO_4_ARCHITECTURE = {
    "name": "Scenario 4: Structural Coupling & Maintainability Anti-Patterns",
    "description": "Triggers Architecture Agent and Quality Agent with relative imports, bare excepts, and missing docs.",
    "agents": ["architecture", "quality"],
    "expected_findings": ["Deep Relative Parent Import", "Bare 'except:' Clause", "Missing Docstring"],
    "code": """from ..core.internal.utils import database_helper, cache_provider

def execute_batch_processing(records):
    try:
        results = []
        for r in records:
            results.append(r)
        return results
    except:
        # Dangerous: bare except suppresses KeyboardInterrupt and MemoryError
        pass
"""
}

SCENARIO_5_CLEAN_CODE = {
    "name": "Scenario 5: Enterprise Gold Standard (100% Pass Clean Code)",
    "description": "Evaluated against all 5 agents; achieves maximum score (>95) with zero critical or high issues.",
    "agents": ["security", "performance", "quality", "architecture", "compliance"],
    "expected_findings": [],
    "code": """from typing import List, Dict, Optional
import os

def calculate_portfolio_metrics(asset_values: List[float], discount_rate: float = 0.05) -> Dict[str, float]:
    \"\"\"Calculate aggregate financial metrics for asset portfolios.

    Args:
        asset_values: List of strictly positive monetary valuations.
        discount_rate: Annual discount percentage between 0.0 and 1.0.

    Returns:
        A dictionary containing gross_value and discounted_net_present_value.
    \"\"\"
    if not asset_values:
        return {"gross_value": 0.0, "net_present_value": 0.0}

    gross = sum(asset_values)
    net_present_value = round(gross * (1.0 - discount_rate), 2)
    return {
        "gross_value": round(gross, 2),
        "net_present_value": net_present_value
    }
"""
}

ALL_SCENARIOS: List[Dict[str, Any]] = [
    SCENARIO_1_SECURITY,
    SCENARIO_2_PERFORMANCE,
    SCENARIO_3_COMPLIANCE,
    SCENARIO_4_ARCHITECTURE,
    SCENARIO_5_CLEAN_CODE,
]
