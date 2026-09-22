# CodeVault AI - API Reference

**Version:** 0.1.0  
**Last Updated:** September 21, 2026  
**Base URL:** `http://localhost:8000` (local) or your deployed endpoint

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Versioning](#versioning)
- [Core Endpoints](#core-endpoints)
  - [Submit Code Review](#submit-code-review)
  - [Get Review Status](#get-review-status)
  - [Batch Review Submission](#batch-review-submission)
  - [List Available Agents](#list-available-agents)
  - [Update Configuration](#update-configuration)
  - [Health Check](#health-check)
- [Webhooks](#webhooks)
- [SDK Examples](#sdk-examples)
- [Common Integration Patterns](#common-integration-patterns)
- [Error Handling](#error-handling)
- [Response Formats](#response-formats)

---

## Overview

The CodeVault AI REST API provides programmatic access to the multi-agent code review system. All endpoints return JSON responses and follow RESTful conventions.

**Key Features:**
- RESTful design with predictable resource URLs
- JSON request/response bodies
- Standard HTTP status codes
- API key authentication
- Rate limiting and quotas
- Async review processing with webhooks
- Idempotent operations where applicable

**API Characteristics:**
- **Protocol**: HTTPS (HTTP for local development)
- **Content-Type**: `application/json`
- **Character Encoding**: UTF-8
- **Response Format**: JSON
- **Date Format**: ISO 8601 (e.g., `2026-09-21T10:30:00Z`)

---

## Authentication

CodeVault AI uses API key authentication for all non-health check endpoints.

### Obtaining an API Key

**Local Development:**
```bash
# Generate an API key
docker-compose exec api python -m codevault.cli create-api-key --name "my-dev-key"

# Output:
# API Key created successfully!
# Key: cvai_1234567890abcdefghijklmnop
# Name: my-dev-key
# Keep this key secure - it won't be shown again!
```

**Production Deployment:**
```bash
# Using the CLI
codevault-cli auth create-key --name "production-key" --scopes "review:read,review:write"
```

### Using API Keys

Include the API key in the `Authorization` header with the `Bearer` scheme:

```bash
curl -H "Authorization: Bearer cvai_your_api_key_here" \
     https://api.codevault.ai/api/v1/review
```

**Authentication Errors:**

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 401 | `missing_authentication` | No Authorization header provided |
| 401 | `invalid_api_key` | API key is invalid or expired |
| 403 | `insufficient_permissions` | API key lacks required permissions |

---

## Rate Limiting

Rate limits protect the API from abuse and ensure fair usage.

**Default Limits:**
- **Anonymous**: 10 requests per hour
- **Authenticated**: 100 requests per hour per API key
- **Pro Tier**: 1,000 requests per hour
- **Enterprise**: Custom limits

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1695384600
```

**Rate Limit Exceeded Response:**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

**HTTP Status**: `429 Too Many Requests`

---

## Versioning

The API uses URL-based versioning: `/api/v1/`, `/api/v2/`, etc.

**Current Version**: `v1`

**Version Support Policy:**
- Current version: Fully supported
- Previous version: Supported for 12 months after new version release
- Deprecated version: 6-month sunset period with warnings

**Version-Specific Headers:**
```http
X-API-Version: 1.0.0
X-API-Deprecated: false
```

---

## Core Endpoints

### Submit Code Review

Submit code for multi-agent review.

**Endpoint:** `POST /api/v1/review`

**Request Headers:**
```http
Authorization: Bearer cvai_your_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item['price']\n    return total",
  "language": "python",
  "filename": "calculator.py",
  "context": {
    "project_name": "shopping-cart",
    "git_commit": "abc123",
    "file_path": "src/utils/calculator.py"
  },
  "agents": ["security", "performance", "quality"],
  "config": {
    "severity_threshold": "medium",
    "blocking_mode": true
  }
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | The source code to review (max 100KB) |
| `language` | string | No | Programming language (auto-detected if omitted) |
| `filename` | string | No | Original filename for context |
| `context` | object | No | Additional context (project name, git info, etc.) |
| `agents` | array | No | List of agents to run (default: all) |
| `config` | object | No | Review-specific configuration overrides |

**Example 1: Basic Python Review**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\n\nAPI_KEY = \"sk-1234567890\"\n\ndef get_user(user_id):\n    query = \"SELECT * FROM users WHERE id = \" + user_id\n    return db.execute(query)",
    "language": "python",
    "filename": "api.py"
  }'
```

**Response (201 Created):**
```json
{
  "review_id": "rev_8f7e6d5c4b3a2918",
  "status": "processing",
  "created_at": "2026-09-21T10:30:00Z",
  "estimated_completion": "2026-09-21T10:30:15Z",
  "agents_scheduled": ["security", "performance", "quality"],
  "webhook_url": null,
  "_links": {
    "self": "/api/v1/review/rev_8f7e6d5c4b3a2918",
    "results": "/api/v1/review/rev_8f7e6d5c4b3a2918/results"
  }
}
```

**Example 2: JavaScript/TypeScript Review**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function fetchUserData(userId) {\n  return fetch(`https://api.example.com/users/${userId}`)\n    .then(res => res.json())\n    .catch(err => console.log(err))\n}",
    "language": "javascript",
    "filename": "userService.js",
    "agents": ["security", "quality"]
  }'
```

**Response (201 Created):**
```json
{
  "review_id": "rev_9a8b7c6d5e4f3021",
  "status": "processing",
  "created_at": "2026-09-21T10:35:00Z",
  "estimated_completion": "2026-09-21T10:35:12Z",
  "agents_scheduled": ["security", "quality"],
  "webhook_url": null,
  "_links": {
    "self": "/api/v1/review/rev_9a8b7c6d5e4f3021",
    "results": "/api/v1/review/rev_9a8b7c6d5e4f3021/results"
  }
}
```

**Example 3: Review with Webhook Notification**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SELECT * FROM users WHERE email = '\'' + userInput + '\'';",
    "language": "sql",
    "filename": "queries.sql",
    "webhook_url": "https://myapp.com/webhooks/codevault",
    "webhook_secret": "whsec_your_webhook_secret"
  }'
```

**Response (201 Created):**
```json
{
  "review_id": "rev_7f6e5d4c3b2a1908",
  "status": "processing",
  "created_at": "2026-09-21T10:40:00Z",
  "estimated_completion": "2026-09-21T10:40:10Z",
  "agents_scheduled": ["security", "performance", "quality"],
  "webhook_url": "https://myapp.com/webhooks/codevault",
  "_links": {
    "self": "/api/v1/review/rev_7f6e5d4c3b2a1908",
    "results": "/api/v1/review/rev_7f6e5d4c3b2a1908/results"
  }
}
```

**Example 4: Cached Review (Fast Response)**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello, World!\")",
    "language": "python"
  }'
```

**Response (200 OK - Cached):**
```json
{
  "review_id": "rev_6e5d4c3b2a190817",
  "status": "completed",
  "created_at": "2026-09-21T10:45:00Z",
  "completed_at": "2026-09-21T10:45:00Z",
  "cache_hit": true,
  "results": {
    "overall_score": 95,
    "severity_summary": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 1,
      "info": 2
    },
    "agents": [
      {
        "name": "security",
        "status": "completed",
        "score": 100,
        "findings": []
      },
      {
        "name": "performance",
        "status": "completed",
        "score": 95,
        "findings": [
          {
            "severity": "low",
            "title": "Consider using f-strings",
            "message": "For better performance and readability, consider using f-strings instead of concatenation",
            "line": 2,
            "suggestion": "print(f\"Hello, World!\")"
          }
        ]
      },
      {
        "name": "quality",
        "status": "completed",
        "score": 90,
        "findings": [
          {
            "severity": "info",
            "title": "Add docstring",
            "message": "Consider adding a docstring to describe the function's purpose",
            "line": 1,
            "suggestion": "def hello():\n    \"\"\"Print a greeting message.\"\"\"\n    print(\"Hello, World!\")"
          }
        ]
      }
    ]
  },
  "_links": {
    "self": "/api/v1/review/rev_6e5d4c3b2a190817"
  }
}
```

**Example 5: Blocking Review with Severity Threshold**
```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "password = request.GET.get(\"password\")\nuser = authenticate(username, password)",
    "language": "python",
    "filename": "auth.py",
    "config": {
      "severity_threshold": "medium",
      "blocking_mode": true
    }
  }'
```

**Response (200 OK):**
```json
{
  "review_id": "rev_5d4c3b2a19081726",
  "status": "completed",
  "created_at": "2026-09-21T10:50:00Z",
  "completed_at": "2026-09-21T10:50:08Z",
  "blocking": true,
  "should_block": true,
  "block_reason": "Found 1 critical and 1 high severity issues",
  "results": {
    "overall_score": 35,
    "severity_summary": {
      "critical": 1,
      "high": 1,
      "medium": 0,
      "low": 0,
      "info": 0
    },
    "agents": [
      {
        "name": "security",
        "status": "completed",
        "score": 30,
        "execution_time_ms": 3450,
        "findings": [
          {
            "id": "SEC-001",
            "severity": "critical",
            "category": "authentication",
            "title": "Credentials exposed in GET request",
            "message": "Password is transmitted via GET parameter, which is logged in server logs and browser history. This is a critical security vulnerability.",
            "line": 1,
            "column": 11,
            "code_snippet": "password = request.GET.get(\"password\")",
            "explanation": "GET parameters are logged by web servers, proxies, and browsers. Passwords should only be sent via POST in request body or headers.",
            "recommendation": "Use POST request with password in request body. Consider using HTTPS and proper authentication tokens.",
            "references": [
              "https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication",
              "https://cwe.mitre.org/data/definitions/598.html"
            ],
            "suggested_fix": "# Use POST instead\npassword = request.POST.get(\"password\")\n# Better: Use token-based auth\ntoken = request.headers.get(\"Authorization\")"
          },
          {
            "id": "SEC-002",
            "severity": "high",
            "category": "input_validation",
            "title": "Unvalidated user input",
            "message": "User input is passed directly to authentication without validation",
            "line": 2,
            "column": 7,
            "code_snippet": "user = authenticate(username, password)",
            "explanation": "Always validate and sanitize user input before using it in authentication operations.",
            "recommendation": "Add input validation: check length, allowed characters, implement rate limiting",
            "suggested_fix": "if not username or len(username) > 255:\n    raise ValueError(\"Invalid username\")\nif not password or len(password) < 8:\n    raise ValueError(\"Invalid password\")\nuser = authenticate(username, password)"
          }
        ]
      }
    ]
  },
  "_links": {
    "self": "/api/v1/review/rev_5d4c3b2a19081726"
  }
}
```

**Status Codes:**

| Code | Meaning | When |
|------|---------|------|
| 201 | Created | Review successfully created and processing |
| 200 | OK | Review completed immediately (cache hit) |
| 400 | Bad Request | Invalid request body or parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 413 | Payload Too Large | Code exceeds size limit (100KB) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error during review processing |
| 503 | Service Unavailable | LLM provider unavailable |

---

### Get Review Status

Retrieve the current status and results of a review.

**Endpoint:** `GET /api/v1/review/{review_id}`

**Request Headers:**
```http
Authorization: Bearer cvai_your_api_key
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `review_id` | string | The unique review identifier (e.g., `rev_abc123`) |

**Example 1: Get In-Progress Review**
```bash
curl -X GET http://localhost:8000/api/v1/review/rev_8f7e6d5c4b3a2918 \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "review_id": "rev_8f7e6d5c4b3a2918",
  "status": "processing",
  "created_at": "2026-09-21T10:30:00Z",
  "progress": {
    "total_agents": 3,
    "completed_agents": 2,
    "current_agent": "quality",
    "percent_complete": 66
  },
  "agents_status": [
    {
      "name": "security",
      "status": "completed",
      "execution_time_ms": 3200
    },
    {
      "name": "performance",
      "status": "completed",
      "execution_time_ms": 2800
    },
    {
      "name": "quality",
      "status": "processing",
      "started_at": "2026-09-21T10:30:06Z"
    }
  ],
  "_links": {
    "self": "/api/v1/review/rev_8f7e6d5c4b3a2918"
  }
}
```

**Example 2: Get Completed Review**
```bash
curl -X GET http://localhost:8000/api/v1/review/rev_9a8b7c6d5e4f3021 \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "review_id": "rev_9a8b7c6d5e4f3021",
  "status": "completed",
  "created_at": "2026-09-21T10:35:00Z",
  "completed_at": "2026-09-21T10:35:11Z",
  "duration_ms": 11240,
  "cache_hit": false,
  "results": {
    "overall_score": 72,
    "severity_summary": {
      "critical": 0,
      "high": 1,
      "medium": 3,
      "low": 5,
      "info": 2
    },
    "blocking": false,
    "agents": [
      {
        "name": "security",
        "status": "completed",
        "score": 65,
        "execution_time_ms": 4100,
        "token_usage": {
          "prompt_tokens": 1250,
          "completion_tokens": 380,
          "total_tokens": 1630
        },
        "findings_count": 4,
        "findings": [
          {
            "id": "SEC-101",
            "severity": "high",
            "category": "error_handling",
            "title": "Error messages expose sensitive information",
            "message": "Catch block logs full error details which may expose system information",
            "line": 5,
            "code_snippet": ".catch(err => console.log(err))",
            "recommendation": "Log errors securely without exposing details to users",
            "suggested_fix": ".catch(err => {\n  logger.error(err);\n  return { error: 'An error occurred' };\n})"
          }
        ]
      },
      {
        "name": "quality",
        "status": "completed",
        "score": 78,
        "execution_time_ms": 3800,
        "token_usage": {
          "prompt_tokens": 1180,
          "completion_tokens": 420,
          "total_tokens": 1600
        },
        "findings_count": 6,
        "findings": [
          {
            "id": "QUA-201",
            "severity": "medium",
            "category": "error_handling",
            "title": "Insufficient error handling",
            "message": "Promise rejection is logged but not properly handled",
            "line": 5,
            "recommendation": "Return a user-friendly error or propagate for upstream handling"
          }
        ]
      }
    ],
    "metadata": {
      "language": "javascript",
      "filename": "userService.js",
      "file_size_bytes": 234,
      "lines_of_code": 6
    }
  },
  "_links": {
    "self": "/api/v1/review/rev_9a8b7c6d5e4f3021",
    "download_json": "/api/v1/review/rev_9a8b7c6d5e4f3021/export?format=json",
    "download_markdown": "/api/v1/review/rev_9a8b7c6d5e4f3021/export?format=markdown",
    "download_sarif": "/api/v1/review/rev_9a8b7c6d5e4f3021/export?format=sarif"
  }
}
```

**Example 3: Get Failed Review**
```bash
curl -X GET http://localhost:8000/api/v1/review/rev_failed_123 \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "review_id": "rev_failed_123",
  "status": "failed",
  "created_at": "2026-09-21T10:40:00Z",
  "failed_at": "2026-09-21T10:40:05Z",
  "error": {
    "code": "llm_provider_error",
    "message": "OpenAI API rate limit exceeded",
    "details": "Rate limit reached for requests",
    "retry_after": 60
  },
  "agents_status": [
    {
      "name": "security",
      "status": "completed",
      "execution_time_ms": 3100
    },
    {
      "name": "performance",
      "status": "failed",
      "error": "LLM provider rate limit exceeded"
    },
    {
      "name": "quality",
      "status": "cancelled"
    }
  ],
  "_links": {
    "self": "/api/v1/review/rev_failed_123",
    "retry": "/api/v1/review/rev_failed_123/retry"
  }
}
```

**Example 4: Get Review with Query Parameters**
```bash
curl -X GET "http://localhost:8000/api/v1/review/rev_9a8b7c6d5e4f3021?include=findings&severity=high,critical" \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `include` | string | Comma-separated fields to include (e.g., `findings,metadata`) |
| `severity` | string | Filter findings by severity (e.g., `high,critical`) |
| `format` | string | Response format: `json` (default), `markdown`, `sarif` |

**Example 5: Poll for Completion**
```bash
# Poll every 2 seconds until complete
while true; do
  STATUS=$(curl -s -H "Authorization: Bearer cvai_dev_key_123" \
    http://localhost:8000/api/v1/review/rev_8f7e6d5c4b3a2918 | jq -r '.status')
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    echo "Review $STATUS"
    break
  fi
  
  echo "Status: $STATUS... polling again in 2s"
  sleep 2
done
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | OK - Review found |
| 401 | Unauthorized |
| 404 | Not Found - Review ID doesn't exist |
| 429 | Too Many Requests |

---

### Batch Review Submission

Submit multiple files for review in a single request.

**Endpoint:** `POST /api/v1/review/batch`

**Request Headers:**
```http
Authorization: Bearer cvai_your_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "files": [
    {
      "filename": "api.py",
      "language": "python",
      "code": "import os\n\nAPI_KEY = os.getenv('API_KEY')\n\ndef get_data():\n    pass"
    },
    {
      "filename": "utils.js",
      "language": "javascript",
      "code": "function formatDate(date) {\n  return date.toString();\n}"
    }
  ],
  "context": {
    "project_name": "my-project",
    "git_commit": "abc123"
  },
  "config": {
    "parallel_processing": true,
    "agents": ["security", "quality"]
  }
}
```

**Example 1: Batch Review Multiple Files**
```bash
curl -X POST http://localhost:8000/api/v1/review/batch \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {
        "filename": "auth.py",
        "code": "def login(username, password):\n    if username == \"admin\" and password == \"admin\":\n        return True\n    return False"
      },
      {
        "filename": "database.py",
        "code": "def execute_query(user_input):\n    query = \"SELECT * FROM users WHERE name = '\'' + user_input + '\'';\"\n    return db.execute(query)"
      }
    ],
    "config": {
      "agents": ["security"],
      "severity_threshold": "high"
    }
  }'
```

**Response (201 Created):**
```json
{
  "batch_id": "batch_7f6e5d4c3b2a",
  "status": "processing",
  "created_at": "2026-09-21T11:00:00Z",
  "total_files": 2,
  "reviews": [
    {
      "review_id": "rev_auth_py_001",
      "filename": "auth.py",
      "status": "processing",
      "_links": {
        "self": "/api/v1/review/rev_auth_py_001"
      }
    },
    {
      "review_id": "rev_database_py_002",
      "filename": "database.py",
      "status": "processing",
      "_links": {
        "self": "/api/v1/review/rev_database_py_002"
      }
    }
  ],
  "_links": {
    "self": "/api/v1/review/batch/batch_7f6e5d4c3b2a",
    "status": "/api/v1/review/batch/batch_7f6e5d4c3b2a/status"
  }
}
```

**Example 2: Check Batch Status**
```bash
curl -X GET http://localhost:8000/api/v1/review/batch/batch_7f6e5d4c3b2a/status \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "batch_id": "batch_7f6e5d4c3b2a",
  "status": "completed",
  "created_at": "2026-09-21T11:00:00Z",
  "completed_at": "2026-09-21T11:00:18Z",
  "duration_ms": 18450,
  "total_files": 2,
  "summary": {
    "completed": 2,
    "failed": 0,
    "total_findings": 8,
    "critical_findings": 2,
    "high_findings": 3,
    "medium_findings": 2,
    "low_findings": 1
  },
  "reviews": [
    {
      "review_id": "rev_auth_py_001",
      "filename": "auth.py",
      "status": "completed",
      "score": 25,
      "findings_count": 3,
      "severity_summary": {
        "critical": 1,
        "high": 2,
        "medium": 0,
        "low": 0
      },
      "_links": {
        "self": "/api/v1/review/rev_auth_py_001"
      }
    },
    {
      "review_id": "rev_database_py_002",
      "filename": "database.py",
      "status": "completed",
      "score": 15,
      "findings_count": 5,
      "severity_summary": {
        "critical": 1,
        "high": 1,
        "medium": 2,
        "low": 1
      },
      "_links": {
        "self": "/api/v1/review/rev_database_py_002"
      }
    }
  ],
  "_links": {
    "self": "/api/v1/review/batch/batch_7f6e5d4c3b2a/status",
    "download_report": "/api/v1/review/batch/batch_7f6e5d4c3b2a/export"
  }
}
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| 201 | Created - Batch review started |
| 400 | Bad Request - Invalid file data |
| 401 | Unauthorized |
| 413 | Payload Too Large - Too many files or total size exceeded |
| 429 | Too Many Requests |

---

### List Available Agents

Get information about available review agents and their capabilities.

**Endpoint:** `GET /api/v1/agents`

**Request Headers:**
```http
Authorization: Bearer cvai_your_api_key
```

**Example 1: List All Agents**
```bash
curl -X GET http://localhost:8000/api/v1/agents \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "agents": [
    {
      "id": "security",
      "name": "Security Agent",
      "version": "1.2.0",
      "description": "Identifies security vulnerabilities and compliance issues",
      "enabled": true,
      "capabilities": [
        "sql_injection_detection",
        "xss_detection",
        "secret_scanning",
        "authentication_review",
        "cryptography_analysis",
        "dependency_vulnerabilities"
      ],
      "supported_languages": ["*"],
      "average_execution_time_ms": 3500,
      "config_options": {
        "severity_levels": ["critical", "high", "medium", "low"],
        "rule_sets": ["owasp_top_10", "cwe_top_25", "sans_top_25"],
        "secret_patterns": "configurable"
      }
    },
    {
      "id": "performance",
      "name": "Performance Agent",
      "version": "1.1.0",
      "description": "Detects performance bottlenecks and optimization opportunities",
      "enabled": true,
      "capabilities": [
        "complexity_analysis",
        "memory_leak_detection",
        "database_query_optimization",
        "caching_opportunities",
        "algorithm_efficiency"
      ],
      "supported_languages": ["*"],
      "average_execution_time_ms": 3200,
      "config_options": {
        "complexity_threshold": "O(n²) or worse",
        "memory_threshold_mb": 100,
        "query_analysis": true
      }
    },
    {
      "id": "quality",
      "name": "Code Quality Agent",
      "version": "1.3.0",
      "description": "Reviews code maintainability, readability, and best practices",
      "enabled": true,
      "capabilities": [
        "naming_conventions",
        "code_structure",
        "design_patterns",
        "documentation_review",
        "duplication_detection",
        "solid_principles"
      ],
      "supported_languages": ["*"],
      "average_execution_time_ms": 3800,
      "config_options": {
        "style_guide": "configurable",
        "documentation_required": true,
        "max_function_length": 50,
        "max_complexity": 10
      }
    }
  ],
  "total_agents": 3,
  "enabled_agents": 3
}
```

**Example 2: Get Specific Agent Details**
```bash
curl -X GET http://localhost:8000/api/v1/agents/security \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "id": "security",
  "name": "Security Agent",
  "version": "1.2.0",
  "description": "Identifies security vulnerabilities and compliance issues",
  "enabled": true,
  "status": "healthy",
  "last_health_check": "2026-09-21T11:05:00Z",
  "capabilities": [
    "sql_injection_detection",
    "xss_detection",
    "secret_scanning",
    "authentication_review",
    "cryptography_analysis",
    "dependency_vulnerabilities"
  ],
  "statistics": {
    "total_reviews": 15432,
    "total_findings": 8921,
    "average_execution_time_ms": 3480,
    "success_rate": 99.8,
    "last_30_days": {
      "reviews": 1247,
      "findings": 623,
      "critical_findings": 34,
      "high_findings": 189
    }
  },
  "configuration": {
    "llm_provider": "openai",
    "llm_model": "gpt-4-turbo-preview",
    "max_tokens": 2000,
    "temperature": 0.2,
    "timeout_seconds": 30
  },
  "_links": {
    "self": "/api/v1/agents/security",
    "health": "/api/v1/agents/security/health",
    "config": "/api/v1/agents/security/config"
  }
}
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | OK |
| 401 | Unauthorized |
| 404 | Not Found - Agent doesn't exist |

---

### Update Configuration

Update system or agent-specific configuration.

**Endpoint:** `POST /api/v1/config`

**Request Headers:**
```http
Authorization: Bearer cvai_your_api_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "scope": "user",
  "config": {
    "default_agents": ["security", "quality"],
    "severity_threshold": "medium",
    "agents": {
      "security": {
        "enabled": true,
        "rule_sets": ["owasp_top_10"],
        "secret_scanning": {
          "enabled": true,
          "custom_patterns": ["API_KEY_\\w+"]
        }
      }
    },
    "llm": {
      "provider": "openai",
      "model": "gpt-4-turbo-preview",
      "fallback_provider": "anthropic"
    }
  }
}
```

**Example 1: Update User Configuration**
```bash
curl -X POST http://localhost:8000/api/v1/config \
  -H "Authorization: Bearer cvai_dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "user",
    "config": {
      "default_agents": ["security"],
      "severity_threshold": "high",
      "blocking_mode": true
    }
  }'
```

**Response (200 OK):**
```json
{
  "status": "updated",
  "scope": "user",
  "updated_at": "2026-09-21T11:10:00Z",
  "config": {
    "default_agents": ["security"],
    "severity_threshold": "high",
    "blocking_mode": true
  },
  "cache_invalidated": true,
  "message": "Configuration updated successfully. Changes will take effect immediately."
}
```

**Example 2: Get Current Configuration**
```bash
curl -X GET http://localhost:8000/api/v1/config \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response (200 OK):**
```json
{
  "scope": "user",
  "config": {
    "default_agents": ["security"],
    "severity_threshold": "high",
    "blocking_mode": true,
    "agents": {
      "security": {
        "enabled": true,
        "llm_provider": "openai",
        "llm_model": "gpt-4-turbo-preview"
      },
      "performance": {
        "enabled": true,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo"
      },
      "quality": {
        "enabled": true,
        "llm_provider": "openai",
        "llm_model": "gpt-3.5-turbo"
      }
    },
    "cache_ttl_seconds": 604800,
    "max_code_size_bytes": 102400
  },
  "effective_config": {
    "source": "user",
    "inherited_from": ["defaults"]
  }
}
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | OK - Configuration updated |
| 400 | Bad Request - Invalid configuration |
| 401 | Unauthorized |
| 403 | Forbidden - Cannot modify system config |

---

### Health Check

Check the health status of the CodeVault AI service and its dependencies.

**Endpoint:** `GET /api/v1/health`

**No Authentication Required**

**Example 1: Basic Health Check**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-09-21T11:15:00Z",
  "uptime_seconds": 86400,
  "components": {
    "api": {
      "status": "healthy",
      "latency_ms": 2
    },
    "database": {
      "status": "healthy",
      "type": "postgresql",
      "latency_ms": 5,
      "connection_pool": {
        "active": 3,
        "idle": 7,
        "max": 10
      }
    },
    "cache": {
      "status": "healthy",
      "type": "redis",
      "latency_ms": 1,
      "memory_used_mb": 45,
      "memory_max_mb": 512,
      "hit_rate": 0.73
    },
    "llm_providers": {
      "openai": {
        "status": "healthy",
        "latency_ms": 120,
        "last_check": "2026-09-21T11:14:00Z"
      },
      "anthropic": {
        "status": "healthy",
        "latency_ms": 150,
        "last_check": "2026-09-21T11:14:00Z"
      },
      "ollama": {
        "status": "unavailable",
        "error": "Connection refused",
        "last_check": "2026-09-21T11:14:00Z"
      }
    },
    "agents": {
      "security": {
        "status": "healthy",
        "version": "1.2.0"
      },
      "performance": {
        "status": "healthy",
        "version": "1.1.0"
      },
      "quality": {
        "status": "healthy",
        "version": "1.3.0"
      }
    }
  }
}
```

**Example 2: Detailed Health Check**
```bash
curl -X GET "http://localhost:8000/api/v1/health?detailed=true"
```

**Response includes additional metrics:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-09-21T11:15:00Z",
  "uptime_seconds": 86400,
  "components": {
    "... (same as basic) ..."
  },
  "metrics": {
    "requests_total": 15432,
    "requests_per_second": 0.18,
    "average_response_time_ms": 245,
    "error_rate": 0.002,
    "cache_hit_rate": 0.73,
    "active_reviews": 3
  },
  "system": {
    "cpu_usage_percent": 12.5,
    "memory_usage_mb": 256,
    "memory_total_mb": 2048,
    "disk_usage_percent": 45
  }
}
```

**Example 3: Unhealthy Service**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "version": "0.1.0",
  "timestamp": "2026-09-21T11:20:00Z",
  "components": {
    "api": {
      "status": "healthy"
    },
    "database": {
      "status": "unhealthy",
      "error": "Connection timeout",
      "last_successful_check": "2026-09-21T11:18:00Z"
    },
    "cache": {
      "status": "degraded",
      "warning": "High memory usage (95%)"
    },
    "llm_providers": {
      "openai": {
        "status": "unhealthy",
        "error": "Rate limit exceeded",
        "retry_after": 3600
      }
    }
  },
  "message": "Service is experiencing issues. Some features may be unavailable."
}
```

**Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | OK - Service is healthy |
| 503 | Service Unavailable - Service is unhealthy |

---

## Webhooks

Configure webhooks to receive notifications when reviews complete.

### Webhook Configuration

Include webhook URL when submitting a review:

```json
{
  "code": "...",
  "webhook_url": "https://myapp.com/webhooks/codevault",
  "webhook_secret": "whsec_your_secret_key"
}
```

### Webhook Payload

When a review completes, CodeVault AI sends a POST request:

**Webhook Request:**
```http
POST /webhooks/codevault HTTP/1.1
Host: myapp.com
Content-Type: application/json
X-CodeVault-Signature: sha256=abc123...
X-CodeVault-Event: review.completed

{
  "event": "review.completed",
  "timestamp": "2026-09-21T11:25:00Z",
  "review_id": "rev_8f7e6d5c4b3a2918",
  "status": "completed",
  "data": {
    "overall_score": 85,
    "severity_summary": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 3,
      "info": 1
    },
    "agents_completed": ["security", "performance", "quality"],
    "duration_ms": 12450
  },
  "_links": {
    "review": "https://api.codevault.ai/api/v1/review/rev_8f7e6d5c4b3a2918"
  }
}
```

### Verifying Webhook Signatures

**Python Example:**
```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected_sig = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_sig}", signature)

# Usage
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/codevault', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-CodeVault-Signature')
    secret = 'whsec_your_secret_key'
    
    if not verify_webhook(request.data, signature, secret):
        return 'Invalid signature', 401
    
    event = request.json
    # Process event...
    return 'OK', 200
```

**Node.js Example:**
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${expectedSig}`)
  );
}

// Express.js usage
app.post('/webhooks/codevault', express.raw({type: 'application/json'}), (req, res) => {
  const signature = req.headers['x-codevault-signature'];
  const secret = 'whsec_your_secret_key';
  
  if (!verifyWebhook(req.body, signature, secret)) {
    return res.status(401).send('Invalid signature');
  }
  
  const event = JSON.parse(req.body);
  // Process event...
  res.send('OK');
});
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `review.created` | Review was created and queued |
| `review.processing` | Review processing has started |
| `review.completed` | Review completed successfully |
| `review.failed` | Review failed |
| `batch.completed` | Batch review completed |

---

## SDK Examples

### Python SDK

```python
from codevault import CodeVault

# Initialize client
client = CodeVault(api_key="cvai_your_api_key")

# Submit review
review = client.review(
    code="""
    def login(username, password):
        if username == "admin" and password == "admin":
            return True
        return False
    """,
    language="python",
    agents=["security", "quality"]
)

# Wait for completion
result = review.wait()

# Check results
if result.should_block:
    print(f"❌ Review failed with score {result.overall_score}/100")
    for finding in result.critical_findings:
        print(f"  - {finding.title}")
else:
    print(f"✅ Review passed with score {result.overall_score}/100")

# Async usage
async def review_code():
    async with CodeVault(api_key="cvai_key") as client:
        review = await client.review_async(code="...", language="python")
        result = await review.wait_async()
        return result
```

### JavaScript/TypeScript SDK

```javascript
import { CodeVault } from '@codevault/sdk';

// Initialize client
const client = new CodeVault({ apiKey: 'cvai_your_api_key' });

// Submit review
const review = await client.review({
  code: `
    function login(username, password) {
      if (username === "admin" && password === "admin") {
        return true;
      }
      return false;
    }
  `,
  language: 'javascript',
  agents: ['security', 'quality']
});

// Wait for completion
const result = await review.wait();

// Check results
if (result.shouldBlock) {
  console.log(`❌ Review failed with score ${result.overallScore}/100`);
  result.criticalFindings.forEach(finding => {
    console.log(`  - ${finding.title}`);
  });
} else {
  console.log(`✅ Review passed with score ${result.overallScore}/100`);
}

// Stream progress
review.on('progress', (progress) => {
  console.log(`Progress: ${progress.percentComplete}%`);
});

review.on('completed', (result) => {
  console.log('Review completed!', result);
});
```

---

## Common Integration Patterns

### CI/CD Integration (GitHub Actions)

```yaml
name: Code Review
on: [pull_request]

jobs:
  codevault-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run CodeVault AI Review
        env:
          CODEVAULT_API_KEY: ${{ secrets.CODEVAULT_API_KEY }}
        run: |
          # Get changed files
          git diff --name-only origin/main...HEAD > changed_files.txt
          
          # Review each file
          while read file; do
            if [ -f "$file" ]; then
              curl -X POST http://api.codevault.ai/api/v1/review \
                -H "Authorization: Bearer $CODEVAULT_API_KEY" \
                -H "Content-Type: application/json" \
                -d @- << EOF
          {
            "code": "$(cat $file | jq -Rs .)",
            "filename": "$file",
            "context": {
              "pr_number": "${{ github.event.pull_request.number }}",
              "commit": "${{ github.sha }}"
            }
          }
          EOF
            fi
          done < changed_files.txt
```

### Pre-commit Hook Integration

```bash
#!/bin/bash
# .git/hooks/pre-commit

CODEVAULT_API_KEY="cvai_your_api_key"
API_URL="http://localhost:8000/api/v1/review"

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

for FILE in $STAGED_FILES; do
  # Skip if not a code file
  if [[ ! $FILE =~ \.(py|js|ts|java|go|rb)$ ]]; then
    continue
  fi
  
  echo "Reviewing $FILE..."
  
  # Submit for review
  CODE=$(cat "$FILE" | jq -Rs .)
  RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Authorization: Bearer $CODEVAULT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"code\": $CODE, \"filename\": \"$FILE\", \"config\": {\"blocking_mode\": true}}")
  
  # Check if blocking
  SHOULD_BLOCK=$(echo "$RESPONSE" | jq -r '.should_block // false')
  
  if [ "$SHOULD_BLOCK" = "true" ]; then
    echo "❌ Review failed for $FILE"
    echo "$RESPONSE" | jq '.results.agents[].findings[] | "  - [\(.severity)] \(.title)"'
    echo ""
    echo "Commit blocked due to critical issues. Fix them or use 'git commit --no-verify' to bypass."
    exit 1
  fi
done

echo "✅ All files passed review"
exit 0
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "error_code_here",
    "message": "Human-readable error message",
    "details": "Additional context about the error",
    "field": "field_name",
    "documentation_url": "https://docs.codevault.ai/errors/error_code_here"
  },
  "request_id": "req_abc123",
  "timestamp": "2026-09-21T11:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `missing_authentication` | 401 | No API key provided |
| `invalid_api_key` | 401 | API key is invalid or expired |
| `insufficient_permissions` | 403 | API key lacks required permissions |
| `rate_limit_exceeded` | 429 | Too many requests |
| `invalid_request_body` | 400 | Malformed JSON or missing required fields |
| `code_too_large` | 413 | Code exceeds size limit |
| `invalid_language` | 400 | Unsupported programming language |
| `agent_not_found` | 404 | Specified agent doesn't exist |
| `review_not_found` | 404 | Review ID doesn't exist |
| `llm_provider_error` | 503 | LLM provider is unavailable |
| `database_error` | 500 | Database operation failed |
| `internal_error` | 500 | Unexpected server error |

### Retry Logic

Implement exponential backoff for retries:

```python
import time
import requests

def review_with_retry(code, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/review",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"code": code}
            )
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue
            
            if response.status_code >= 500:
                # Server error - exponential backoff
                wait_time = (2 ** attempt) + random.random()
                time.sleep(wait_time)
                continue
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

---

## Response Formats

### JSON (Default)

Standard JSON response format (shown in all examples above).

### Markdown

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/review/rev_abc123/export?format=markdown" \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response:**
```markdown
# Code Review Report

**Review ID:** rev_abc123  
**Status:** Completed  
**Score:** 72/100  
**Date:** 2026-09-21 11:35:00 UTC

## Summary

- **Critical Issues:** 0
- **High Issues:** 1
- **Medium Issues:** 3
- **Low Issues:** 5
- **Info:** 2

## Security Agent (Score: 65/100)

### 🔴 HIGH - Error messages expose sensitive information

**Line 5:** `.catch(err => console.log(err))`

Catch block logs full error details which may expose system information.

**Recommendation:** Log errors securely without exposing details to users

**Suggested Fix:**
```javascript
.catch(err => {
  logger.error(err);
  return { error: 'An error occurred' };
})
```

---
```

### SARIF (Static Analysis Results Interchange Format)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/review/rev_abc123/export?format=sarif" \
  -H "Authorization: Bearer cvai_dev_key_123"
```

**Response:**
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "CodeVault AI",
          "version": "0.1.0",
          "informationUri": "https://codevault.ai"
        }
      },
      "results": [
        {
          "ruleId": "SEC-101",
          "level": "error",
          "message": {
            "text": "Error messages expose sensitive information"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "userService.js"
                },
                "region": {
                  "startLine": 5
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Next Steps

- **[Agent Specifications](03-agent-specifications.md)** - Learn about each agent's capabilities
- **[Configuration Reference](05-configuration-reference.md)** - Customize API behavior
- **[Installation Guide](04-installation-setup.md)** - Set up your own instance

---

**API Version:** 0.1.0  
**Documentation Version:** 1.0  
**Last Updated:** September 21, 2026

*For support, visit [docs.codevault.ai](https://docs.codevault.ai) or open an issue on [GitHub](https://github.com/codevault-ai/codevault/issues)*
