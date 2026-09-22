# CodeVault AI - Configuration Reference

**Version:** 0.1.0  
**Last Updated:** September 21, 2026

---

## Table of Contents

- [Configuration File Format](#configuration-file-format)
- [Core Configuration](#core-configuration)
- [LLM Backend Configuration](#llm-backend-configuration)
- [Agent Configuration](#agent-configuration)
- [Git Hooks Configuration](#git-hooks-configuration)
- [Performance Tuning](#performance-tuning)
- [Logging Configuration](#logging-configuration)
- [Complete Examples](#complete-examples)
- [Environment Variables Reference](#environment-variables-reference)

---

## Configuration File Format

CodeVault AI uses YAML configuration files located at:

- **System-wide**: `/etc/codevault/config.yml`
- **User-level**: `~/.codevault/config.yml`
- **Project-level**: `.codevault.yml` (in project root)

**Configuration Precedence** (highest to lowest):
1. Environment variables
2. Project-level config (`.codevault.yml`)
3. User-level config (`~/.codevault/config.yml`)
4. System-wide config
5. Built-in defaults

**Basic Structure:**

```yaml
version: 1

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  url: "postgresql://user:pass@localhost:5432/codevault"

cache:
  url: "redis://localhost:6379/0"
  ttl_seconds: 604800

llm:
  provider: "openai"
  model: "gpt-4-turbo-preview"

agents:
  security:
    enabled: true
  performance:
    enabled: true
  quality:
    enabled: true
```

---

## Core Configuration

### Server Settings

```yaml
server:
  host: "0.0.0.0"              # Listen address (0.0.0.0 = all interfaces)
  port: 8000                    # HTTP port
  workers: 4                    # Number of worker processes
  worker_class: "uvicorn.workers.UvicornWorker"
  keepalive: 5                  # Keep-alive timeout (seconds)
  timeout: 120                  # Request timeout (seconds)
  max_requests: 1000            # Max requests per worker before restart
  max_requests_jitter: 50       # Jitter for max_requests
```

**Environment Variables:**
```bash
CODEVAULT_HOST=0.0.0.0
CODEVAULT_PORT=8000
CODEVAULT_WORKERS=4
```

### Database Configuration

```yaml
database:
  # Connection string
  url: "postgresql://codevault:password@localhost:5432/codevault"
  
  # Or for SQLite (development only)
  # url: "sqlite:///./codevault.db"
  
  # Connection pool settings
  pool_size: 10                 # Max connections in pool
  max_overflow: 20              # Max connections beyond pool_size
  pool_timeout: 30              # Timeout waiting for connection
  pool_recycle: 3600            # Recycle connections after N seconds
  
  # Query settings
  echo: false                   # Log all SQL queries (debug)
  query_timeout: 30             # Individual query timeout
  
  # Migration settings
  auto_migrate: true            # Run migrations on startup
  migration_timeout: 300        # Migration timeout
```

**Environment Variables:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Redis Cache Configuration

```yaml
cache:
  url: "redis://localhost:6379/0"
  
  # TTL settings
  ttl_seconds: 604800           # Default TTL (7 days)
  review_ttl: 604800            # Review results TTL
  llm_response_ttl: 2592000     # LLM responses TTL (30 days)
  
  # Connection settings
  max_connections: 50           # Max Redis connections
  socket_timeout: 5             # Socket timeout
  socket_connect_timeout: 5     # Connection timeout
  
  # Behavior
  enabled: true                 # Enable/disable caching
  key_prefix: "codevault:"      # Redis key prefix
  
  # Eviction
  maxmemory_policy: "allkeys-lru"  # Redis eviction policy
```

**Environment Variables:**
```bash
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_TTL_SECONDS=604800
```

---

## LLM Backend Configuration

### OpenAI Configuration

```yaml
llm:
  provider: "openai"
  
  openai:
    api_key: "${OPENAI_API_KEY}"     # From environment
    organization: ""                  # Optional org ID
    
    # Model settings
    model: "gpt-4-turbo-preview"     # Default model
    temperature: 0.2                  # Lower = more deterministic
    max_tokens: 2000                  # Max response tokens
    top_p: 1.0                        # Nucleus sampling
    frequency_penalty: 0.0
    presence_penalty: 0.0
    
    # Retry settings
    max_retries: 3
    retry_delay: 1.0
    retry_backoff: 2.0
    timeout: 60
    
    # Rate limiting
    requests_per_minute: 60
    tokens_per_minute: 90000
```

**Model Options:**
- `gpt-4-turbo-preview` - Best quality, highest cost (~$0.03/review)
- `gpt-4` - High quality, high cost (~$0.06/review)
- `gpt-3.5-turbo` - Good quality, low cost (~$0.001/review)

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_ORG_ID=org-...
```

### Anthropic Claude Configuration

```yaml
llm:
  provider: "anthropic"
  
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    
    # Model settings
    model: "claude-3-sonnet-20240229"
    max_tokens: 4096
    temperature: 0.2
    
    # Retry settings
    max_retries: 3
    timeout: 60
```

**Model Options:**
- `claude-3-opus-20240229` - Highest capability (~$0.075/review)
- `claude-3-sonnet-20240229` - Balanced (~$0.015/review)
- `claude-3-haiku-20240307` - Fast and affordable (~$0.001/review)

### Ollama Configuration (Local)

```yaml
llm:
  provider: "ollama"
  
  ollama:
    base_url: "http://localhost:11434"
    
    # Model settings
    model: "codellama"            # Or: mistral, llama2, etc.
    
    # Generation options
    temperature: 0.2
    num_ctx: 4096                 # Context window size
    num_predict: 2000             # Max tokens to generate
    
    # Performance
    num_gpu: 1                    # Number of GPUs to use
    num_thread: 8                 # CPU threads
    
    timeout: 120
```

**Available Models:**
- `codellama` - Code-specialized Llama
- `mistral` - Mistral 7B
- `llama2` - Llama 2
- `phi` - Microsoft Phi-2

### Azure OpenAI Configuration

```yaml
llm:
  provider: "azure_openai"
  
  azure_openai:
    api_key: "${AZURE_OPENAI_API_KEY}"
    endpoint: "https://your-resource.openai.azure.com/"
    deployment: "gpt-4"           # Your deployment name
    api_version: "2023-12-01-preview"
    
    # Same settings as OpenAI
    temperature: 0.2
    max_tokens: 2000
    timeout: 60
```

### Multi-Provider Fallback

```yaml
llm:
  provider: "openai"              # Primary provider
  
  # Fallback chain
  fallback_providers:
    - "anthropic"                 # Try Claude if OpenAI fails
    - "ollama"                    # Try local if all cloud fails
  
  # Fallback conditions
  fallback_on:
    - rate_limit_exceeded
    - service_unavailable
    - timeout
```

---

## Agent Configuration

### Global Agent Settings

```yaml
agents:
  # Which agents to enable
  enabled: ["security", "performance", "quality"]
  
  # Default agents for reviews (if not specified)
  default: ["security", "performance", "quality"]
  
  # Execution mode
  execution:
    mode: "parallel"              # parallel, sequential, or priority
    timeout_seconds: 30           # Per-agent timeout
    max_retries: 2                # Retry failed agents
  
  # Severity thresholds
  severity:
    block_on: ["critical", "high"]   # Block commit on these
    warn_on: ["medium"]               # Warn but don't block
    report_all: true                  # Include all findings
```

### Security Agent Configuration

```yaml
agents:
  security:
    enabled: true
    llm_model: "gpt-4-turbo-preview"  # Override default model
    
    # Rule sets
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
        - database_urls
      
      # Custom patterns (regex)
      custom_patterns:
        - regex: "API_KEY_[A-Za-z0-9]{32}"
          name: "Custom API Key Format"
        - regex: "sk-[A-Za-z0-9]{48}"
          name: "OpenAI API Key"
      
      # Ignore patterns (false positives)
      ignore_patterns:
        - "test_api_key_*"
        - "*_EXAMPLE_*"
        - "DEMO_*"
    
    # Vulnerability detection
    vulnerabilities:
      sql_injection: true
      xss: true
      command_injection: true
      path_traversal: true
      xxe: true
      ssrf: true
    
    # Severity mapping
    severity_mapping:
      hardcoded_credentials: "critical"
      sql_injection: "critical"
      xss: "high"
      weak_crypto: "medium"
    
    # Performance
    timeout_seconds: 30
    max_code_size_bytes: 102400    # 100KB
```

### Performance Agent Configuration

```yaml
agents:
  performance:
    enabled: true
    llm_model: "gpt-4-turbo-preview"
    
    # Complexity analysis
    complexity:
      warn_at: "O(n²)"
      error_at: "O(n³)"
      check_nested_loops: true
      check_recursion: true
    
    # Memory analysis
    memory:
      warn_at_mb: 100
      error_at_mb: 500
      detect_leaks: true
      check_large_allocations: true
    
    # Database analysis
    database:
      detect_n_plus_1: true
      suggest_indexes: true
      check_query_complexity: true
      max_result_size: 1000
    
    # Caching analysis
    caching:
      suggest_opportunities: true
      min_computation_time_ms: 100
    
    # I/O analysis
    io:
      detect_blocking_calls: true
      suggest_async: true
    
    timeout_seconds: 30
```

### Code Quality Agent Configuration

```yaml
agents:
  quality:
    enabled: true
    llm_model: "gpt-3.5-turbo"      # Cheaper model OK for quality
    
    # Style guide
    style_guide: "pep8"             # pep8, google, airbnb, etc.
    
    # Complexity limits
    max_function_length: 50         # Lines per function
    max_cyclomatic_complexity: 10   # McCabe complexity
    max_class_size: 20              # Methods per class
    max_nesting_depth: 4            # Max nested blocks
    
    # Documentation requirements
    documentation:
      require_docstrings: true
      require_type_hints: true
      require_examples: false
      check_completeness: true
    
    # Code smells to detect
    detect:
      code_duplication: true
      long_functions: true
      god_classes: true
      primitive_obsession: true
      feature_envy: true
    
    # Best practices
    best_practices:
      solid_principles: true
      dry_principle: true
      naming_conventions: true
      error_handling: true
    
    timeout_seconds: 30
```

---

## Git Hooks Configuration

```yaml
hooks:
  # Pre-commit hook
  pre_commit:
    enabled: true
    blocking: true                # Block commit on failures
    
    agents: ["security", "quality"]
    severity_threshold: "high"    # Block on high+ severity
    
    # Files to review
    include_patterns:
      - "**/*.py"
      - "**/*.js"
      - "**/*.ts"
    
    exclude_patterns:
      - "**/*_test.py"
      - "**/*.min.js"
      - "migrations/**"
    
    # Performance
    max_files: 50                 # Max files per commit
    timeout_seconds: 60
    
    # Behavior
    async_mode: false             # Wait for results
    show_findings: true           # Display findings
    cache_results: true
  
  # Pre-push hook
  pre_push:
    enabled: true
    blocking: true
    
    agents: ["security", "performance", "quality"]
    severity_threshold: "medium"
    
    # More comprehensive review
    review_all_commits: true      # Not just latest
    include_tests: true
    
    timeout_seconds: 300
```

---

## Performance Tuning

### Caching Strategy

```yaml
performance:
  caching:
    # Cache enablement
    enabled: true
    aggressive: true              # Cache more aggressively
    
    # Cache keys
    include_in_key:
      - code_hash
      - agent_versions
      - config_hash
      - llm_model
    
    # Cache invalidation
    invalidate_on:
      - agent_upgrade
      - config_change
      - manual_clear
    
    # Warm-up
    warmup_on_startup: false
    preload_common_patterns: false
```

### Concurrency Settings

```yaml
performance:
  concurrency:
    # Agent execution
    max_concurrent_agents: 3      # Agents per review
    max_concurrent_reviews: 10    # Reviews in parallel
    
    # LLM calls
    max_concurrent_llm_calls: 5
    llm_rate_limit_buffer: 0.8    # Use 80% of rate limit
    
    # Database
    db_pool_size: 10
    db_max_overflow: 20
```

### Rate Limiting

```yaml
rate_limiting:
  enabled: true
  
  # Per API key
  per_key:
    requests_per_hour: 100
    burst: 10                     # Allow bursts
  
  # Per IP
  per_ip:
    requests_per_hour: 50
    burst: 5
  
  # Global
  global:
    max_concurrent_reviews: 50
```

---

## Logging Configuration

```yaml
logging:
  # Log level
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
  
  # Format
  format: "json"                  # json or text
  
  # Output
  output:
    - type: "console"
      level: "INFO"
    - type: "file"
      path: "/var/log/codevault/app.log"
      level: "DEBUG"
      max_size_mb: 100
      backup_count: 5
    - type: "syslog"
      address: "/dev/log"
      level: "WARNING"
  
  # Structured logging
  structured:
    include_timestamp: true
    include_level: true
    include_component: true
    include_request_id: true
  
  # Log rotation
  rotation:
    enabled: true
    when: "midnight"              # midnight, hourly, size
    interval: 1
    backup_count: 30
  
  # Sensitive data
  redact:
    - "api_key"
    - "password"
    - "token"
    - "secret"
```

---

## Complete Examples

### Minimal Configuration (Development)

```yaml
version: 1

database:
  url: "sqlite:///./codevault.db"

cache:
  url: "redis://localhost:6379/0"

llm:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "codellama"

agents:
  enabled: ["security", "quality"]
```

### Recommended Configuration (Production)

```yaml
version: 1

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 40
  pool_recycle: 3600

cache:
  url: "${REDIS_URL}"
  ttl_seconds: 604800
  max_connections: 50

llm:
  provider: "openai"
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4-turbo-preview"
    max_retries: 3
  
  fallback_providers:
    - "anthropic"

agents:
  enabled: ["security", "performance", "quality"]
  execution:
    mode: "parallel"
    timeout_seconds: 30
  
  security:
    rule_sets:
      - owasp_top_10
      - cwe_top_25
    secret_scanning:
      enabled: true
  
  performance:
    complexity:
      warn_at: "O(n²)"
  
  quality:
    style_guide: "pep8"
    max_function_length: 50

performance:
  caching:
    enabled: true
    aggressive: true
  concurrency:
    max_concurrent_reviews: 20

logging:
  level: "INFO"
  format: "json"
  output:
    - type: "console"
    - type: "file"
      path: "/var/log/codevault/app.log"
```

### Advanced Configuration (Enterprise)

```yaml
version: 1

server:
  host: "0.0.0.0"
  port: 8000
  workers: 8
  worker_class: "uvicorn.workers.UvicornWorker"
  max_requests: 1000
  max_requests_jitter: 50

database:
  url: "${DATABASE_URL}"
  pool_size: 50
  max_overflow: 100
  pool_timeout: 30
  pool_recycle: 1800
  query_timeout: 30

cache:
  url: "${REDIS_URL}"
  ttl_seconds: 604800
  max_connections: 100
  socket_timeout: 5

llm:
  provider: "azure_openai"
  azure_openai:
    api_key: "${AZURE_OPENAI_API_KEY}"
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    deployment: "gpt-4"
    max_retries: 3
  
  fallback_providers:
    - "openai"
    - "anthropic"

agents:
  enabled: ["security", "performance", "quality"]
  execution:
    mode: "parallel"
    timeout_seconds: 45
    max_retries: 3
  
  security:
    llm_model: "gpt-4-turbo-preview"
    rule_sets:
      - owasp_top_10
      - cwe_top_25
      - sans_top_25
    secret_scanning:
      enabled: true
      custom_patterns:
        - regex: "API_KEY_[A-Za-z0-9]{32}"
          name: "Custom API Key"
    severity_mapping:
      hardcoded_credentials: "critical"
  
  performance:
    llm_model: "gpt-4-turbo-preview"
    complexity:
      warn_at: "O(n²)"
      error_at: "O(n³)"
    database:
      detect_n_plus_1: true
      suggest_indexes: true
  
  quality:
    llm_model: "gpt-3.5-turbo"
    style_guide: "pep8"
    max_function_length: 50
    max_cyclomatic_complexity: 10
    documentation:
      require_docstrings: true
      require_type_hints: true

performance:
  caching:
    enabled: true
    aggressive: true
  concurrency:
    max_concurrent_reviews: 100
    max_concurrent_llm_calls: 20
  
rate_limiting:
  enabled: true
  per_key:
    requests_per_hour: 1000
  global:
    max_concurrent_reviews: 100

monitoring:
  prometheus:
    enabled: true
    port: 9090
  tracing:
    enabled: true
    jaeger_endpoint: "http://jaeger:14268/api/traces"

logging:
  level: "INFO"
  format: "json"
  output:
    - type: "console"
      level: "WARNING"
    - type: "file"
      path: "/var/log/codevault/app.log"
      level: "INFO"
      max_size_mb: 500
      backup_count: 30
  structured:
    include_timestamp: true
    include_component: true
    include_request_id: true
  redact:
    - "api_key"
    - "password"
    - "token"
```

---

## Environment Variables Reference

Complete list of environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEVAULT_HOST` | `0.0.0.0` | Server listen address |
| `CODEVAULT_PORT` | `8000` | Server port |
| `CODEVAULT_WORKERS` | `4` | Number of worker processes |
| `DATABASE_URL` | - | Database connection string |
| `REDIS_URL` | - | Redis connection string |
| `LLM_PROVIDER` | `openai` | LLM provider (openai, anthropic, ollama, azure_openai) |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4-turbo-preview` | OpenAI model |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-3-sonnet-20240229` | Anthropic model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama base URL |
| `OLLAMA_MODEL` | `codellama` | Ollama model |
| `AZURE_OPENAI_API_KEY` | - | Azure OpenAI key |
| `AZURE_OPENAI_ENDPOINT` | - | Azure OpenAI endpoint |
| `AZURE_OPENAI_DEPLOYMENT` | - | Azure deployment name |
| `CACHE_ENABLED` | `true` | Enable caching |
| `CACHE_TTL_SECONDS` | `604800` | Cache TTL (7 days) |
| `ENABLED_AGENTS` | `security,performance,quality` | Enabled agents |
| `LOG_LEVEL` | `INFO` | Logging level |
| `SECRET_KEY` | - | Application secret key |
| `API_KEY_PREFIX` | `cvai_` | API key prefix |
| `RATE_LIMIT_PER_HOUR` | `100` | Rate limit per API key |
| `PROMETHEUS_ENABLED` | `true` | Enable Prometheus metrics |

---

**Next Steps:**
- [Monitoring & Operations](06-monitoring-operations.md) - Production monitoring
- [Developer Guide](08-developer-guide.md) - Extend functionality

---

*CodeVault AI Configuration Reference - v0.1.0*
