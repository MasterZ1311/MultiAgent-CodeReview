"""
Heuristic and AST-Driven Static Analysis Engine.
Provides high-precision contextual findings out-of-the-box without requiring live cloud LLM keys.
"""

import ast
import re
from typing import List, Tuple
from cerberus.models.schemas import Finding, SeverityEnum


class HeuristicEngine:
    """Intelligent rule and AST-based evaluator for code reviews."""

    # -------------------------------------------------------------
    # SECURITY FINDINGS
    # -------------------------------------------------------------
    @staticmethod
    def analyze_security(code: str, language: str = "python") -> Tuple[List[Finding], float]:
        findings: List[Finding] = []
        lines = code.split("\n")

        # 1. SQL Injection Detection
        sql_patterns = [
            (r"""(["'].*SELECT\s+.*FROM\s+.*WHERE\s+.*['"]\s*\+\s*\w+)""", "SQL injection via string concatenation"),
            (r"""f["'].*SELECT\s+.*FROM\s+.*WHERE\s+.*\{.*\}""", "SQL injection via f-string interpolation"),
            (r"""execute\s*\(\s*["'].*SELECT.*WHERE.*%s.*["']\s*%\s*\w+\)""", "SQL injection via string formatting %"),
        ]
        for idx, line in enumerate(lines, 1):
            for pat, desc in sql_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    findings.append(Finding(
                        id=f"SEC-SQLI-{idx}",
                        severity=SeverityEnum.CRITICAL,
                        category="injection",
                        title="SQL Injection Vulnerability",
                        message=f"{desc}. User input is concatenated directly into SQL query.",
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="Untrusted user input injected into dynamic queries allows attackers to bypass authentication or extract sensitive database contents.",
                        recommendation="Use parameterized queries with placeholders (e.g., db.execute('SELECT * FROM users WHERE id = ?', (user_id,)))",
                        suggestion="db.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
                        cwe_id="CWE-89",
                        cvss_score=9.8,
                        exploitability=0.95
                    ))

        # 2. Hardcoded Credentials & API Keys
        cred_patterns = [
            (r"""(?:api[_-]?key|secret|token|password|auth_token)\s*=\s*["'][A-Za-z0-9_\-]{8,}["']""", "Hardcoded API Key or Secret"),
            (r"""sk-[a-zA-Z0-9]{20,}""", "Exposed OpenAI / Service Secret Key"),
            (r"""password\s*=\s*["']admin(?:123)?["']""", "Default / Weak Hardcoded Password"),
        ]
        for idx, line in enumerate(lines, 1):
            for pat, desc in cred_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    findings.append(Finding(
                        id=f"SEC-CRED-{idx}",
                        severity=SeverityEnum.CRITICAL,
                        category="secrets",
                        title="Hardcoded Credentials Detected",
                        message=f"{desc} identified in source code.",
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="Committing secrets directly into version control leads to immediate credential leakage and system compromise.",
                        recommendation="Load secrets from environment variables or a secure key management vault.",
                        suggestion="API_KEY = os.getenv('API_KEY')",
                        cwe_id="CWE-798",
                        cvss_score=8.9,
                        exploitability=0.85
                    ))

        # 3. Command Injection
        cmd_patterns = [
            (r"""os\.system\s*\(""", "os.system executes shell command without sanitization"),
            (r"""subprocess\.(?:Popen|call|run)\s*\(.*shell\s*=\s*True""", "Subprocess executed with shell=True"),
        ]
        for idx, line in enumerate(lines, 1):
            for pat, desc in cmd_patterns:
                if re.search(pat, line):
                    findings.append(Finding(
                        id=f"SEC-CMD-{idx}",
                        severity=SeverityEnum.HIGH,
                        category="injection",
                        title="Command Injection Vulnerability",
                        message=desc,
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="Passing raw strings to shell execution functions enables remote attackers to execute arbitrary system binaries.",
                        recommendation="Use subprocess.run with argument lists and shell=False.",
                        suggestion='subprocess.run(["ping", "-c", "1", host], check=True)',
                        cwe_id="CWE-78",
                        cvss_score=8.4,
                        exploitability=0.80
                    ))

        # 4. Weak Cryptography & Insecure Hashes
        crypto_patterns = [
            (r"""hashlib\.md5\s*\(""", "Use of MD5 cryptographic hash function"),
            (r"""hashlib\.sha1\s*\(""", "Use of SHA1 cryptographic hash function"),
        ]
        for idx, line in enumerate(lines, 1):
            for pat, desc in crypto_patterns:
                if re.search(pat, line):
                    findings.append(Finding(
                        id=f"SEC-CRYPTO-{idx}",
                        severity=SeverityEnum.MEDIUM,
                        category="cryptography",
                        title="Weak Hash Algorithm (Collision Vulnerable)",
                        message=f"{desc} detected.",
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="MD5 and SHA-1 have known collision attacks and are broken for digital signatures and secure hashing.",
                        recommendation="Use SHA-256 for integrity or bcrypt/argon2 for password hashing.",
                        suggestion="hashlib.sha256(data.encode()).hexdigest()",
                        cwe_id="CWE-328",
                        cvss_score=5.3
                    ))

        # 5. Insecure Deserialization
        if "pickle.loads" in code or "yaml.load(" in code:
            for idx, line in enumerate(lines, 1):
                if "pickle.loads" in line or "yaml.load(" in line:
                    findings.append(Finding(
                        id=f"SEC-DESER-{idx}",
                        severity=SeverityEnum.HIGH,
                        category="deserialization",
                        title="Insecure Object Deserialization",
                        message="Deserializing untrusted data with pickle or unsafe yaml can trigger remote code execution.",
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="Python's pickle module is not secure against erroneous or maliciously constructed data.",
                        recommendation="Use safe serialization formats like JSON or yaml.safe_load.",
                        suggestion="data = json.loads(payload)",
                        cwe_id="CWE-502",
                        cvss_score=8.1
                    ))

        # Calculate security score (100 minus deductions)
        score = 100.0
        for f in findings:
            if f.severity == SeverityEnum.CRITICAL:
                score -= 30.0
            elif f.severity == SeverityEnum.HIGH:
                score -= 20.0
            elif f.severity == SeverityEnum.MEDIUM:
                score -= 10.0
            else:
                score -= 5.0
        return findings, max(0.0, score)

    # -------------------------------------------------------------
    # PERFORMANCE FINDINGS
    # -------------------------------------------------------------
    @staticmethod
    def analyze_performance(code: str, language: str = "python") -> Tuple[List[Finding], float]:
        findings: List[Finding] = []
        lines = code.split("\n")

        # 1. AST Analysis for Nested Loops (O(n²) Complexity)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    for inner in ast.walk(node):
                        if inner is not node and isinstance(inner, (ast.For, ast.While)):
                            line_no = getattr(node, "lineno", 1)
                            findings.append(Finding(
                                id=f"PERF-NESTED-{line_no}",
                                severity=SeverityEnum.MEDIUM,
                                category="algorithmic_complexity",
                                title="Quadratic Time Complexity O(n²)",
                                message="Nested loop detected. Execution time will grow quadratically with input size.",
                                line=line_no,
                                code_snippet=lines[line_no - 1].strip() if line_no <= len(lines) else "",
                                explanation="Nested iterations over collections lead to high CPU latency as datasets grow to thousands of items.",
                                recommendation="Consider using hash maps, sets, or list comprehensions to reduce complexity to O(n) or O(n log n).",
                                suggestion="# Build a lookup dictionary beforehand for O(1) lookups:\nlookup = {item.id: item for item in items}",
                            ))
                            break
        except Exception:
            pass

        # 2. Inefficient string concatenation in loops
        for idx, line in enumerate(lines, 1):
            if re.search(r"""\b\w+\s*\+=\s*["'].*["']""", line) or re.search(r"""\b\w+\s*=\s*\w+\s*\+\s*str\(.+""", line):
                findings.append(Finding(
                    id=f"PERF-STRCAT-{idx}",
                    severity=SeverityEnum.LOW,
                    category="memory_efficiency",
                    title="Repeated In-Place String Concatenation",
                    message="String concatenation in loops creates intermediate immutable string copies.",
                    line=idx,
                    code_snippet=line.strip(),
                    explanation="Strings are immutable in Python; repeated concatenation generates O(n²) allocations.",
                    recommendation="Accumulate items in a list and call ''.join(items).",
                    suggestion="''.join(chunk_list)",
                ))

        # 3. Database query inside loop (N+1 Query Pattern)
        for idx, line in enumerate(lines, 1):
            if re.search(r"""(?:db|session|cursor|repository|User|Product)\.(?:execute|query|find|get)\(""", line):
                # Check if preceding lines have a for loop
                for prev in range(max(0, idx - 5), idx):
                    if "for " in lines[prev] or "while " in lines[prev]:
                        findings.append(Finding(
                            id=f"PERF-NPLUS1-{idx}",
                            severity=SeverityEnum.HIGH,
                            category="database",
                            title="N+1 Query Pattern Detected",
                            message="Database operation detected inside iterative loop.",
                            line=idx,
                            code_snippet=line.strip(),
                            explanation="Executing queries inside loops leads to high roundtrip network latency and database connection saturation.",
                            recommendation="Batch fetch records using SQL IN clauses or join queries before the loop.",
                            suggestion="items = db.query(Item).filter(Item.id.in_(ids)).all()",
                        ))
                        break

        # Calculate performance score
        score = 100.0
        for f in findings:
            if f.severity == SeverityEnum.HIGH:
                score -= 25.0
            elif f.severity == SeverityEnum.MEDIUM:
                score -= 15.0
            else:
                score -= 5.0
        return findings, max(0.0, score)

    # -------------------------------------------------------------
    # CODE QUALITY FINDINGS
    # -------------------------------------------------------------
    @staticmethod
    def analyze_quality(code: str, language: str = "python") -> Tuple[List[Finding], float]:
        findings: List[Finding] = []
        lines = code.split("\n")

        # 1. Missing Docstrings on Functions & Classes
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if not docstring and not node.name.startswith("_"):
                        line_no = node.lineno
                        findings.append(Finding(
                            id=f"QUAL-DOC-{line_no}",
                            severity=SeverityEnum.INFO,
                            category="documentation",
                            title=f"Missing Docstring on '{node.name}'",
                            message=f"Public function/class '{node.name}' lacks documentation docstring.",
                            line=line_no,
                            code_snippet=lines[line_no - 1].strip() if line_no <= len(lines) else "",
                            explanation="Clear docstrings communicate expected arguments, return types, and side effects to other engineers.",
                            recommendation="Add a descriptive triple-quoted docstring explaining the component.",
                            suggestion=f'def {node.name}():\n    """Brief description of {node.name}."""\n    pass',
                        ))

                # 2. Long Functions (> 40 lines)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    if (end_lineno - node.lineno) > 40:
                        findings.append(Finding(
                            id=f"QUAL-LEN-{node.lineno}",
                            severity=SeverityEnum.LOW,
                            category="maintainability",
                            title=f"Function '{node.name}' is Excessively Long ({end_lineno - node.lineno} lines)",
                            message="Long functions reduce readability and testability.",
                            line=node.lineno,
                            code_snippet=lines[node.lineno - 1].strip(),
                            explanation="Large functions often violate the Single Responsibility Principle and are harder to unit test.",
                            recommendation="Refactor into smaller, focused helper methods.",
                        ))
        except Exception:
            pass

        # 3. Bare Except Clauses
        for idx, line in enumerate(lines, 1):
            if re.search(r"""^\s*except\s*:""", line):
                findings.append(Finding(
                    id=f"QUAL-EXCEPT-{idx}",
                    severity=SeverityEnum.MEDIUM,
                    category="error_handling",
                    title="Bare 'except:' Clause",
                    message="Catching all exceptions without specifying exception type hides critical errors.",
                    line=idx,
                    code_snippet=line.strip(),
                    explanation="Bare exceptions inadvertently suppress KeyboardInterrupt, SystemExit, and memory errors.",
                    recommendation="Catch specific exceptions such as except ValueError: or at least except Exception:.",
                    suggestion="except Exception as e:",
                ))

        # 4. Wildcard Imports
        for idx, line in enumerate(lines, 1):
            if re.search(r"""^\s*from\s+[\w\.]+\s+import\s+\*""", line):
                findings.append(Finding(
                    id=f"QUAL-IMPORT-{idx}",
                    severity=SeverityEnum.LOW,
                    category="style",
                    title="Wildcard Import Detected (from module import *)",
                    message="Wildcard imports pollute the local namespace and obscure symbol origins.",
                    line=idx,
                    code_snippet=line.strip(),
                    explanation="Explicit imports prevent unintended variable shadowing and make static linters faster.",
                    recommendation="Import explicitly required symbols or the module name.",
                ))

        # Calculate quality score
        score = 100.0
        for f in findings:
            if f.severity == SeverityEnum.MEDIUM:
                score -= 15.0
            elif f.severity == SeverityEnum.LOW:
                score -= 8.0
            else:
                score -= 3.0
        return findings, max(0.0, score)

    # -------------------------------------------------------------
    # ARCHITECTURE FINDINGS
    # -------------------------------------------------------------
    @staticmethod
    def analyze_architecture(code: str, language: str = "python") -> Tuple[List[Finding], float]:
        findings: List[Finding] = []
        lines = code.split("\n")

        # Circular import or tight coupling detection
        for idx, line in enumerate(lines, 1):
            if "import " in line and "from .." in line:
                findings.append(Finding(
                    id=f"ARCH-COUPLE-{idx}",
                    severity=SeverityEnum.LOW,
                    category="architecture",
                    title="Deep Relative Parent Import",
                    message="Importing from deep parent packages indicates potential architectural coupling.",
                    line=idx,
                    code_snippet=line.strip(),
                    explanation="Deep relative imports make components difficult to extract into separate packages or microservices.",
                    recommendation="Use absolute package imports or inversion of control.",
                ))

        score = 100.0 - (len(findings) * 10.0)
        return findings, max(0.0, score)

    # -------------------------------------------------------------
    # COMPLIANCE FINDINGS (HIPAA / GDPR / SOC 2 / PCI-DSS)
    # -------------------------------------------------------------
    @staticmethod
    def analyze_compliance(code: str, language: str = "python") -> Tuple[List[Finding], float]:
        findings: List[Finding] = []
        lines = code.split("\n")

        pii_patterns = [
            (r"""\b(?:ssn|social_security|credit_card|card_number|cvv|dob|date_of_birth)\b""", "PII / PCI-DSS Sensitive Data Exposure"),
            (r"""(?:logger|logging)\.(?:debug|info|warning|warn|error|critical)\s*\(.*(?:password|token|secret|ssn)""", "Sensitive Data Emitted in Logs (HIPAA / SOC 2 violation)"),
            (r"""print\s*\(.*(?:password|token|secret|ssn)""", "Sensitive Data Emitted via print() (HIPAA / SOC 2 violation)"),
        ]

        for idx, line in enumerate(lines, 1):
            for pat, desc in pii_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    findings.append(Finding(
                        id=f"COMP-{idx}",
                        severity=SeverityEnum.HIGH,
                        category="compliance",
                        title=desc,
                        message="Potential regulatory compliance violation regarding personal or cardholder data.",
                        line=idx,
                        code_snippet=line.strip(),
                        explanation="HIPAA, GDPR, and PCI-DSS require that unencrypted identifiers and credentials are never stored or logged in plain text.",
                        recommendation="Mask or redact sensitive fields before processing or logging.",
                        suggestion="# Sanitize sensitive fields:\nlogger.info(f'User login: {sanitize_user(user)}')",
                    ))

        score = 100.0 - (len(findings) * 20.0)
        return findings, max(0.0, score)
