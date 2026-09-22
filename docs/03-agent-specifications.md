# CodeVault AI - Agent Specifications

**Version:** 0.1.0  
**Last Updated:** September 21, 2026

---

## Table of Contents

- [Agent Architecture Overview](#agent-architecture-overview)
- [Security Agent](#security-agent)
- [Performance Agent](#performance-agent)
- [Code Quality Agent](#code-quality-agent)
- [Agent Customization](#agent-customization)
- [Creating Custom Agents](#creating-custom-agents)
- [Agent Orchestration](#agent-orchestration)

---

## Agent Architecture Overview

CodeVault AI uses a multi-agent architecture where each agent is a specialized module focused on a specific aspect of code review.

### Agent Lifecycle

```
┌─────────────┐
│ Initialize  │ ← Load config, connect to LLM
└──────┬──────┘
       │
┌──────▼──────┐
│  Prepare    │ ← Parse code, extract context
└──────┬──────┘
       │
┌──────▼──────┐
│  Analyze    │ ← Send to LLM, get findings
└──────┬──────┘
       │
┌──────▼──────┐
│  Process    │ ← Parse LLM response, structure findings
└──────┬──────┘
       │
┌──────▼──────┐
│  Return     │ ← Return structured results
└─────────────┘
```

### Base Agent Interface

All agents implement the following interface:

```python
class BaseAgent(ABC):
    """Base class for all code review agents."""
    
    def __init__(self, config: AgentConfig, llm_provider: LLMProvider):
        self.config = config
        self.llm = llm_provider
    
    @abstractmethod
    async def analyze(self, code: str, context: CodeContext) -> AgentResult:
        """Analyze code and return findings."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass
    
    async def health_check(self) -> bool:
        """Check if agent is healthy and LLM is accessible."""
        pass
```

---

## Security Agent

**ID:** `security`  
**Version:** 1.2.0  
**Purpose:** Identify security vulnerabilities and compliance issues

### Capabilities

The Security Agent detects the following types of issues:

#### 1. Injection Vulnerabilities

**SQL Injection:**
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)

# ❌ Vulnerable
query = "SELECT * FROM users WHERE name = '" + username + "'"
db.execute(query)

# ✅ Secure
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))
```

**Command Injection:**
```python
# ❌ Vulnerable
os.system(f"ping {user_input}")

# ✅ Secure
subprocess.run(["ping", user_input], check=True)
```

**XSS (Cross-Site Scripting):**
```javascript
// ❌ Vulnerable
element.innerHTML = userInput;

// ❌ Vulnerable
document.write("<div>" + userInput + "</div>");

// ✅ Secure
element.textContent = userInput;
// Or use a sanitization library
element.innerHTML = DOMPurify.sanitize(userInput);
```

#### 2. Authentication & Authorization

**Hardcoded Credentials:**
```python
# ❌ Insecure
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"

# ✅ Secure
API_KEY = os.getenv("API_KEY")
PASSWORD = os.getenv("PASSWORD")
```

**Weak Authentication:**
```python
# ❌ Weak
def login(username, password):
    if username == "admin" and password == "admin":
        return True
    return False

# ✅ Strong
def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return create_session(user)
    return None
```

**Missing Authorization Checks:**
```python
# ❌ Missing auth
@app.route('/api/user/<user_id>')
def get_user(user_id):
    return User.query.get(user_id).to_json()

# ✅ With auth
@app.route('/api/user/<user_id>')
@require_auth
def get_user(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    return User.query.get(user_id).to_json()
```

#### 3. Cryptography Issues

**Weak Hashing:**
```python
# ❌ Weak (MD5)
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()

# ✅ Strong (bcrypt)
import bcrypt
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Insecure Random:**
```python
# ❌ Insecure
import random
token = ''.join(random.choices(string.ascii_letters, k=32))

# ✅ Secure
import secrets
token = secrets.token_urlsafe(32)
```

#### 4. Data Exposure

**Sensitive Data in Logs:**
```python
# ❌ Exposes data
logger.info(f"User login: {username}, password: {password}")

# ✅ Safe logging
logger.info(f"User login: {username}")
```

**PII Leakage:**
```python
# ❌ Exposes PII
return {"user": user.to_dict()}  # Includes SSN, credit card, etc.

# ✅ Sanitized
return {"user": user.to_public_dict()}  # Only public fields
```

#### 5. Dependency Vulnerabilities

The Security Agent checks for known vulnerabilities in imported packages:

```python
# ❌ Vulnerable versions detected
import requests  # Using requests 2.25.0 (CVE-2023-xxxxx)

# ✅ Agent recommends
# Update to requests >= 2.31.0 to fix security vulnerabilities
```

#### 6. Insecure Configurations

```python
# ❌ Insecure
app.config['SECRET_KEY'] = 'dev'
app.config['DEBUG'] = True  # In production

# ✅ Secure
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'
```

### Analysis Methodology

The Security Agent uses a multi-layered approach:

1. **Pattern Matching**: Regex patterns for common vulnerabilities
2. **Contextual Analysis**: LLM understands code context and intent
3. **Data Flow Tracking**: Traces user input through the code
4. **Best Practices**: Compares against security frameworks (OWASP, CWE)

### Severity Classification

| Severity | Criteria | Example |
|----------|----------|---------|
| **Critical** | Immediate exploit possible, high impact | SQL injection, hardcoded credentials |
| **High** | Exploit likely, significant impact | Weak authentication, XSS |
| **Medium** | Exploit possible with conditions | Missing input validation, weak crypto |
| **Low** | Potential security improvement | Verbose error messages, missing HTTPS |
| **Info** | Best practice recommendation | Add security headers, enable CSP |

### Configuration

```yaml
agents:
  security:
    enabled: true
    llm_model: "gpt-4-turbo-preview"  # Best model for security
    
    # Rule sets to enable
    rule_sets:
      - owasp_top_10
      - cwe_top_25
      - sans_top_25
    
    # Secret scanning
    secret_scanning:
      enabled: true
      patterns:
        - api_keys
        - passwords
        - private_keys
        - tokens
      custom_patterns:
        - regex: "API_KEY_[A-Za-z0-9]{32}"
          name: "Custom API Key"
    
    # Severity thresholds
    severity:
      block_on: ["critical", "high"]
      warn_on: ["medium"]
      report_all: true
    
    # Timeouts
    timeout_seconds: 30
    max_retries: 2
```

### Example Output

```json
{
  "agent": "security",
  "version": "1.2.0",
  "status": "completed",
  "execution_time_ms": 3450,
  "score": 45,
  "findings": [
    {
      "id": "SEC-001",
      "severity": "critical",
      "category": "sql_injection",
      "title": "SQL Injection vulnerability detected",
      "message": "User input is directly concatenated into SQL query without sanitization",
      "line": 42,
      "column": 12,
      "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
      "explanation": "This code constructs an SQL query by directly embedding user input, allowing attackers to inject malicious SQL code. For example, if user_id is \"1 OR 1=1\", it would return all users.",
      "impact": "Attackers can read, modify, or delete database contents, potentially compromising all data.",
      "cwe_id": "CWE-89",
      "owasp_category": "A03:2021 – Injection",
      "references": [
        "https://owasp.org/www-community/attacks/SQL_Injection",
        "https://cwe.mitre.org/data/definitions/89.html"
      ],
      "recommendation": "Use parameterized queries or an ORM to safely handle user input",
      "suggested_fix": "query = \"SELECT * FROM users WHERE id = ?\"\ndb.execute(query, (user_id,))",
      "confidence": 0.95
    }
  ],
  "token_usage": {
    "prompt_tokens": 1250,
    "completion_tokens": 380,
    "total_tokens": 1630,
    "estimated_cost_usd": 0.0326
  }
}
```

---

## Performance Agent

**ID:** `performance`  
**Version:** 1.1.0  
**Purpose:** Detect performance bottlenecks and optimization opportunities

### Capabilities

#### 1. Algorithmic Complexity

**Nested Loops:**
```python
# ❌ O(n²) complexity
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# ✅ O(n) complexity
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Inefficient Searching:**
```python
# ❌ O(n) lookup in list
def is_valid_user(user_id, valid_users):
    return user_id in valid_users  # valid_users is a list

# ✅ O(1) lookup in set
def is_valid_user(user_id, valid_users):
    return user_id in valid_users  # valid_users is a set
```

#### 2. Database Query Optimization

**N+1 Query Problem:**
```python
# ❌ N+1 queries
users = User.query.all()
for user in users:
    print(user.posts)  # Separate query for each user

# ✅ Single query with join
users = User.query.options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded
```

**Missing Indexes:**
```python
# ❌ Slow query without index
# Agent detects: SELECT * FROM users WHERE email = ?
# Recommendation: Add index on 'email' column

# ✅ With index
# CREATE INDEX idx_users_email ON users(email);
```

**Large Result Sets:**
```python
# ❌ Loading all records
users = User.query.all()  # Could be millions

# ✅ Pagination
users = User.query.paginate(page=page, per_page=100)
```

#### 3. Memory Management

**Memory Leaks:**
```python
# ❌ Potential memory leak
cache = {}
def get_data(key):
    if key not in cache:
        cache[key] = expensive_operation(key)  # Unbounded growth
    return cache[key]

# ✅ Bounded cache
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_data(key):
    return expensive_operation(key)
```

**Large Data Structures:**
```python
# ❌ Loading entire file into memory
data = open('large_file.csv').read()  # Could be GBs

# ✅ Streaming
for line in open('large_file.csv'):
    process(line)
```

#### 4. Caching Opportunities

**Redundant Computations:**
```python
# ❌ Recomputing expensive operations
def get_user_data(user_id):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    permissions = calculate_permissions(user)  # Expensive
    return user, permissions

# ✅ Cache expensive computations
@cache(ttl=300)
def calculate_permissions(user):
    # Expensive computation
    return permissions
```

#### 5. I/O Optimization

**Synchronous I/O in Loops:**
```python
# ❌ Sequential API calls
results = []
for user_id in user_ids:
    result = requests.get(f"https://api.example.com/users/{user_id}")
    results.append(result.json())

# ✅ Parallel API calls
import asyncio
import aiohttp

async def fetch_all(user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user(session, uid) for uid in user_ids]
        return await asyncio.gather(*tasks)
```

#### 6. Resource-Intensive Operations

```python
# ❌ Heavy computation in request handler
@app.route('/report')
def generate_report():
    report = complex_calculation()  # Takes 30 seconds
    return report

# ✅ Background processing
@app.route('/report')
def generate_report():
    task_id = queue.enqueue(complex_calculation)
    return {"task_id": task_id, "status": "processing"}
```

### Performance Scoring

The agent calculates a performance score (0-100) based on:

- **Algorithmic Efficiency** (40%): Complexity analysis
- **Database Queries** (30%): Query efficiency
- **Memory Usage** (15%): Memory patterns
- **I/O Operations** (15%): I/O efficiency

### Configuration

```yaml
agents:
  performance:
    enabled: true
    llm_model: "gpt-4-turbo-preview"
    
    # Complexity thresholds
    complexity:
      warn_at: "O(n²)"
      error_at: "O(n³)"
    
    # Memory thresholds
    memory:
      warn_at_mb: 100
      error_at_mb: 500
    
    # Database analysis
    database:
      detect_n_plus_1: true
      suggest_indexes: true
      max_result_size: 1000
    
    # Caching
    caching:
      suggest_opportunities: true
      min_computation_time_ms: 100
```

### Example Output

```json
{
  "agent": "performance",
  "status": "completed",
  "score": 68,
  "findings": [
    {
      "id": "PERF-001",
      "severity": "high",
      "category": "algorithmic_complexity",
      "title": "Nested loop creates O(n²) complexity",
      "line": 15,
      "explanation": "The nested loop iterates over the same list twice, resulting in quadratic time complexity. For a list of 1000 items, this means 1,000,000 operations.",
      "performance_impact": "For n=1000: ~1M operations. For n=10000: ~100M operations",
      "recommendation": "Use a set or dictionary for O(1) lookups",
      "suggested_fix": "seen = set(items)\nfor item in items:\n    if item in seen:\n        # O(1) lookup",
      "estimated_improvement": "1000x faster for large inputs"
    }
  ]
}
```

---

## Code Quality Agent

**ID:** `quality`  
**Version:** 1.3.0  
**Purpose:** Review maintainability, readability, and best practices

### Capabilities

#### 1. Naming Conventions

```python
# ❌ Poor naming
def f(x, y):
    z = x + y
    return z

# ✅ Clear naming
def calculate_total_price(base_price, tax_amount):
    total_price = base_price + tax_amount
    return total_price
```

#### 2. Code Structure

```python
# ❌ Long function
def process_order(order):
    # 200 lines of code...
    pass

# ✅ Decomposed
def process_order(order):
    validate_order(order)
    calculate_total(order)
    charge_payment(order)
    send_confirmation(order)
```

#### 3. Design Patterns

```python
# ❌ Tight coupling
class OrderProcessor:
    def __init__(self):
        self.payment = PayPalPayment()  # Hardcoded dependency
    
    def process(self, order):
        self.payment.charge(order.total)

# ✅ Dependency injection
class OrderProcessor:
    def __init__(self, payment_provider):
        self.payment = payment_provider
    
    def process(self, order):
        self.payment.charge(order.total)
```

#### 4. Documentation

```python
# ❌ Missing documentation
def calculate(a, b, c):
    return (a + b) * c

# ✅ Well documented
def calculate_order_total(subtotal, tax_rate, quantity):
    """
    Calculate the total order amount including tax.
    
    Args:
        subtotal: Base price before tax
        tax_rate: Tax rate as a decimal (e.g., 0.08 for 8%)
        quantity: Number of items ordered
    
    Returns:
        Total amount including tax
    
    Example:
        >>> calculate_order_total(100, 0.08, 2)
        216.0
    """
    return (subtotal + subtotal * tax_rate) * quantity
```

#### 5. Code Duplication

```python
# ❌ Duplicated logic
def get_active_users():
    return User.query.filter(User.active == True).all()

def get_active_admins():
    return User.query.filter(User.active == True, User.is_admin == True).all()

# ✅ DRY principle
def get_users(active=None, is_admin=None):
    query = User.query
    if active is not None:
        query = query.filter(User.active == active)
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    return query.all()
```

#### 6. Error Handling

```python
# ❌ Bare except
try:
    risky_operation()
except:
    pass

# ✅ Specific error handling
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return default_value
```

#### 7. SOLID Principles

**Single Responsibility:**
```python
# ❌ Multiple responsibilities
class User:
    def save_to_database(self):
        pass
    
    def send_welcome_email(self):
        pass
    
    def generate_report(self):
        pass

# ✅ Single responsibility
class User:
    pass

class UserRepository:
    def save(self, user):
        pass

class EmailService:
    def send_welcome_email(self, user):
        pass

class ReportGenerator:
    def generate_user_report(self, user):
        pass
```

### Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Cyclomatic Complexity** | Number of independent paths | < 10 per function |
| **Function Length** | Lines of code per function | < 50 lines |
| **Class Size** | Number of methods | < 20 methods |
| **Documentation Coverage** | % of functions with docstrings | > 80% |
| **Naming Clarity** | Descriptive variable names | Subjective, LLM evaluates |

### Configuration

```yaml
agents:
  quality:
    enabled: true
    llm_model: "gpt-3.5-turbo"  # Good enough for quality checks
    
    # Style guide
    style_guide: "pep8"  # Or: "google", "airbnb", etc.
    
    # Complexity limits
    max_function_length: 50
    max_cyclomatic_complexity: 10
    max_class_size: 20
    
    # Documentation
    require_docstrings: true
    require_type_hints: true
    
    # Patterns to detect
    detect_code_smells: true
    detect_duplication: true
    suggest_refactoring: true
```

### Example Output

```json
{
  "agent": "quality",
  "status": "completed",
  "score": 78,
  "findings": [
    {
      "id": "QUAL-001",
      "severity": "medium",
      "category": "naming",
      "title": "Non-descriptive variable name",
      "line": 10,
      "code_snippet": "x = calculate_value()",
      "explanation": "Variable 'x' doesn't convey meaning. Use descriptive names.",
      "recommendation": "Rename to indicate what the variable represents",
      "suggested_fix": "total_price = calculate_value()"
    },
    {
      "id": "QUAL-002",
      "severity": "low",
      "category": "documentation",
      "title": "Missing docstring",
      "line": 5,
      "explanation": "Function lacks documentation explaining its purpose",
      "suggested_fix": "def calculate_value():\n    \"\"\"\n    Calculate the total value including tax.\n    \n    Returns:\n        float: Total value\n    \"\"\""
    }
  ]
}
```

---

## Agent Customization

### Per-Review Configuration

Override agent behavior for specific reviews:

```python
client.review(
    code="...",
    config={
        "agents": {
            "security": {
                "severity_threshold": "critical",  # Only critical issues
                "rule_sets": ["owasp_top_10"]       # Limited rule set
            },
            "performance": {
                "enabled": False  # Skip performance analysis
            }
        }
    }
)
```

### Project-Level Configuration

Create `.codevault.yml` in your project root:

```yaml
version: 1

agents:
  security:
    enabled: true
    severity_threshold: high
    secret_scanning:
      enabled: true
      ignore_patterns:
        - "test_api_key_*"
        - "*_EXAMPLE_*"
  
  performance:
    enabled: true
    complexity:
      warn_at: "O(n²)"
  
  quality:
    enabled: true
    style_guide: pep8
    max_function_length: 30

ignore:
  - "**/*_test.py"
  - "migrations/**"
  - "vendor/**"
```

---

## Creating Custom Agents

### Agent Development SDK

```python
from codevault.agents import BaseAgent, AgentResult, Finding

class TypeScriptLinterAgent(BaseAgent):
    """Custom agent for TypeScript-specific linting."""
    
    def __init__(self, config, llm_provider):
        super().__init__(config, llm_provider)
        self.name = "typescript_linter"
        self.version = "1.0.0"
    
    async def analyze(self, code: str, context: CodeContext) -> AgentResult:
        # Only analyze TypeScript files
        if context.language not in ["typescript", "tsx"]:
            return AgentResult(status="skipped")
        
        # Build prompt
        prompt = self._build_prompt(code, context)
        
        # Call LLM
        response = await self.llm.complete(prompt)
        
        # Parse response into findings
        findings = self._parse_findings(response)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        return AgentResult(
            agent_name=self.name,
            status="completed",
            score=score,
            findings=findings
        )
    
    def _build_prompt(self, code: str, context: CodeContext) -> str:
        return f"""
        You are a TypeScript expert. Review this code for TypeScript-specific issues:
        
        {code}
        
        Focus on:
        - Type safety
        - Interface usage
        - Async/await patterns
        - TypeScript best practices
        
        Return findings in JSON format.
        """
    
    def _parse_findings(self, llm_response: str) -> List[Finding]:
        # Parse LLM response into structured findings
        pass
    
    def _calculate_score(self, findings: List[Finding]) -> int:
        # Calculate overall score based on findings
        pass
    
    def get_capabilities(self) -> List[str]:
        return [
            "typescript_type_checking",
            "interface_review",
            "async_patterns"
        ]
```

### Registering Custom Agents

```python
from codevault import CodeVault
from my_agents import TypeScriptLinterAgent

client = CodeVault(api_key="...")

# Register custom agent
client.register_agent(TypeScriptLinterAgent)

# Use in reviews
result = client.review(
    code="...",
    language="typescript",
    agents=["security", "typescript_linter"]
)
```

---

## Agent Orchestration

### Execution Modes

**Parallel (Default):**
```yaml
execution:
  mode: parallel
  timeout_seconds: 30
```

All agents run simultaneously. Fastest but uses more resources.

**Sequential:**
```yaml
execution:
  mode: sequential
  order: ["security", "performance", "quality"]
```

Agents run one after another. Slower but uses less resources.

**Priority-Based:**
```yaml
execution:
  mode: priority
  priorities:
    security: 1    # Run first
    performance: 2  # Run second
    quality: 3      # Run last
  parallel_within_priority: true
```

### Consensus Logic

When agents have overlapping findings:

```yaml
consensus:
  enabled: true
  strategy: "highest_severity"  # Or: "majority_vote", "all_agree"
  deduplication: true
```

**Example:**
- Security Agent: "Potential SQL injection (HIGH)"
- Quality Agent: "Unsafe string concatenation (MEDIUM)"
- Result: Single finding with HIGH severity and combined context

---

**Next Steps:**
- [Configuration Reference](05-configuration-reference.md) - Configure agents
- [Developer Guide](08-developer-guide.md) - Create custom agents

---

*CodeVault AI Agent Specifications - v0.1.0*
