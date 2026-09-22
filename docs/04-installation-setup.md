# CodeVault AI - Installation & Setup Guide

**Version:** 0.1.0  
**Last Updated:** September 21, 2026

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Local Development Setup](#local-development-setup)
- [Cloud Deployment](#cloud-deployment)
- [Git Hooks Integration](#git-hooks-integration)
- [Verification & Testing](#verification--testing)
- [Troubleshooting](#troubleshooting)
- [Upgrade & Migration](#upgrade--migration)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| **Docker** | 24.0+ | Container runtime |
| **Docker Compose** | 2.20+ | Multi-container orchestration |
| **Git** | 2.30+ | Version control (for hooks) |
| **Python** | 3.11+ | CLI tool (optional) |

### LLM Provider Requirements

Choose at least one:

**Option 1: OpenAI**
- API key from [platform.openai.com](https://platform.openai.com)
- Credit balance or payment method
- Cost: ~$0.03 per review (GPT-4-turbo)

**Option 2: Anthropic Claude**
- API key from [console.anthropic.com](https://console.anthropic.com)
- Cost: ~$0.025 per review (Claude 3 Sonnet)

**Option 3: Ollama (Local, Free)**
- Ollama installed locally
- ~8GB RAM free for models
- Cost: $0 (local execution)

**Option 4: Azure OpenAI**
- Azure subscription with OpenAI enabled
- Deployment created in Azure Portal

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB free

**Recommended:**
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 20GB+ free
- SSD storage

---

## Quick Start (5 Minutes)

Get CodeVault AI running locally in under 5 minutes.

### Step 1: Clone and Configure

```bash
# Clone repository
git clone https://github.com/codevault-ai/codevault.git
cd codevault

# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env

# For Ollama (local):
echo "LLM_PROVIDER=ollama" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
```

### Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                STATUS              PORTS
codevault-api       Up 30 seconds       0.0.0.0:8000->8000/tcp
codevault-redis     Up 30 seconds       6379/tcp
codevault-db        Up 30 seconds       5432/tcp
prometheus          Up 30 seconds       9090/tcp
grafana             Up 30 seconds       3000/tcp
```

### Step 3: Verify Installation

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Should return: {"status": "healthy", ...}
```

### Step 4: Create API Key

```bash
# Generate your first API key
docker-compose exec api python -m codevault.cli create-api-key --name "my-dev-key"

# Save the output - you'll need this key!
# Output: cvai_1234567890abcdefghijklmnop
```

### Step 5: Run First Review

```bash
# Test review
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"Hello, World!\")",
    "language": "python"
  }'
```

**Success!** You now have CodeVault AI running locally. 🎉

---

## Local Development Setup

### Docker Compose Configuration

**Production docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    image: codevault/api:latest
    container_name: codevault-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://codevault:password@db:5432/codevault
      - REDIS_URL=redis://redis:6379/0
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    container_name: codevault-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=codevault
      - POSTGRES_USER=codevault
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U codevault"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: codevault-redis
    restart: unless-stopped
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    container_name: codevault-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    container_name: codevault-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Environment Configuration

**Complete .env file:**

```bash
# ============================================
# CodeVault AI Configuration
# ============================================

# --- Application Settings ---
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-production

# --- Server Settings ---
HOST=0.0.0.0
PORT=8000
WORKERS=4

# --- Database ---
DATABASE_URL=postgresql://codevault:password@db:5432/codevault
# For SQLite (development only):
# DATABASE_URL=sqlite:///./codevault.db

# --- Redis Cache ---
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=604800  # 7 days

# --- LLM Provider Configuration ---
# Options: openai, anthropic, ollama, azure_openai
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_ORG_ID=  # Optional

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama

# Azure OpenAI
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2023-12-01-preview

# --- Agent Configuration ---
ENABLED_AGENTS=security,performance,quality
DEFAULT_AGENTS=security,performance,quality

# --- Security ---
API_KEY_PREFIX=cvai_
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# --- Rate Limiting ---
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_BURST=10

# --- Monitoring ---
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# --- Feature Flags ---
ENABLE_WEBHOOKS=true
ENABLE_BATCH_REVIEWS=true
ENABLE_CACHE=true
```

### Connecting to Different LLM Backends

#### OpenAI Setup

```bash
# Get API key from platform.openai.com
export OPENAI_API_KEY="sk-..."

# Optional: Specify model
export OPENAI_MODEL="gpt-4-turbo-preview"  # or gpt-3.5-turbo for lower cost

# Test connection
docker-compose exec api python -c "
from openai import OpenAI
client = OpenAI()
print(client.models.list())
"
```

#### Ollama Setup (Local)

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from ollama.ai

# Pull a model
ollama pull codellama

# Verify it's running
curl http://localhost:11434/api/tags

# Configure CodeVault to use Ollama
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://host.docker.internal:11434  # From Docker
export OLLAMA_MODEL=codellama

# Restart CodeVault
docker-compose restart api
```

#### Anthropic Claude Setup

```bash
# Get API key from console.anthropic.com
export ANTHROPIC_API_KEY="sk-ant-..."
export LLM_PROVIDER=anthropic
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"

docker-compose restart api
```

#### Azure OpenAI Setup

```bash
# From Azure Portal, get:
# - API Key
# - Endpoint URL
# - Deployment name

export LLM_PROVIDER=azure_openai
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

docker-compose restart api
```

### Volume Mounting

For development with hot reload:

```yaml
# docker-compose.dev.yml
services:
  api:
    volumes:
      - ./codevault:/app/codevault  # Mount source code
      - ./config:/app/config
    environment:
      - RELOAD=true  # Enable hot reload
```

```bash
# Run in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Cloud Deployment

### AWS Deployment (ECS Fargate)

**Step 1: Build and Push Docker Image**

```bash
# Build image
docker build -t codevault/api:latest .

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag codevault/api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/codevault:latest

# Push to ECR
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/codevault:latest
```

**Step 2: Create ECS Task Definition**

```json
{
  "family": "codevault-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "codevault-api",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/codevault:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:...:secret:codevault/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/codevault",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

**Step 3: Create ECS Service**

```bash
aws ecs create-service \
  --cluster codevault-cluster \
  --service-name codevault-api \
  --task-definition codevault-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=codevault-api,containerPort=8000"
```

### GCP Deployment (Cloud Run)

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/codevault

# Deploy to Cloud Run
gcloud run deploy codevault \
  --image gcr.io/PROJECT-ID/codevault \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..." \
  --set-secrets="OPENAI_API_KEY=codevault-openai-key:latest" \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### Azure Deployment (Container Apps)

```bash
# Create Container App
az containerapp create \
  --name codevault \
  --resource-group codevault-rg \
  --environment codevault-env \
  --image codevault/api:latest \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0 \
  --env-vars \
    DATABASE_URL=postgresql://... \
    REDIS_URL=redis://... \
  --secrets \
    openai-key=sk-... \
  --min-replicas 1 \
  --max-replicas 10
```

### Kubernetes Deployment

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codevault-api
  namespace: codevault
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codevault-api
  template:
    metadata:
      labels:
        app: codevault-api
    spec:
      containers:
      - name: api
        image: codevault/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codevault-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: codevault-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: codevault-api
  namespace: codevault
spec:
  selector:
    app: codevault-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**

```bash
# Create namespace
kubectl create namespace codevault

# Create secrets
kubectl create secret generic codevault-secrets \
  --from-literal=openai-api-key=sk-... \
  --from-literal=database-url=postgresql://... \
  -n codevault

# Deploy
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -n codevault
kubectl logs -f deployment/codevault-api -n codevault
```

---

## Git Hooks Integration

### Installing Pre-commit Hook

**Automatic Installation:**

```bash
# Install CodeVault CLI
pip install codevault-cli

# Initialize in your project
cd /path/to/your/project
codevault init

# This creates:
# - .git/hooks/pre-commit
# - .codevault.yml (config file)
```

**Manual Installation:**

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

CODEVAULT_API_URL="${CODEVAULT_API_URL:-http://localhost:8000}"
CODEVAULT_API_KEY="${CODEVAULT_API_KEY}"

if [ -z "$CODEVAULT_API_KEY" ]; then
  echo "⚠️  CODEVAULT_API_KEY not set. Skipping review."
  exit 0
fi

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|java|go|rb|php|cpp|c|cs)$')

if [ -z "$STAGED_FILES" ]; then
  echo "No code files to review."
  exit 0
fi

echo "🔍 Running CodeVault AI review..."

FAILED=0

for FILE in $STAGED_FILES; do
  if [ ! -f "$FILE" ]; then
    continue
  fi
  
  echo "  Reviewing $FILE..."
  
  CODE=$(cat "$FILE" | jq -Rs .)
  RESPONSE=$(curl -s -X POST "$CODEVAULT_API_URL/api/v1/review" \
    -H "Authorization: Bearer $CODEVAULT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"code\": $CODE, \"filename\": \"$FILE\", \"config\": {\"blocking_mode\": true}}")
  
  SHOULD_BLOCK=$(echo "$RESPONSE" | jq -r '.should_block // false')
  
  if [ "$SHOULD_BLOCK" = "true" ]; then
    echo "  ❌ Review failed for $FILE"
    echo "$RESPONSE" | jq -r '.results.agents[].findings[] | "    [\(.severity)] \(.title)"'
    FAILED=1
  else
    echo "  ✅ $FILE passed"
  fi
done

if [ $FAILED -eq 1 ]; then
  echo ""
  echo "❌ Commit blocked due to critical issues."
  echo "   Fix the issues or use 'git commit --no-verify' to bypass."
  exit 1
fi

echo "✅ All files passed review!"
exit 0
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### Installing Pre-push Hook

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

CODEVAULT_API_URL="${CODEVAULT_API_URL:-http://localhost:8000}"
CODEVAULT_API_KEY="${CODEVAULT_API_KEY}"

echo "🔍 Running comprehensive CodeVault AI review before push..."

# Get all changed files in commits being pushed
CHANGED_FILES=$(git diff --name-only HEAD@{u}..HEAD | grep -E '\.(py|js|ts|java|go|rb|php|cpp|c|cs)$')

# Submit batch review
# (implementation similar to pre-commit but with batch endpoint)

echo "✅ Push review complete!"
exit 0
EOF

chmod +x .git/hooks/pre-push
```

### Hook Configuration

**.codevault.yml:**

```yaml
version: 1

# Git hook configuration
hooks:
  pre_commit:
    enabled: true
    blocking: true  # Fail commit on critical issues
    agents: ["security", "quality"]
    severity_threshold: "high"
  
  pre_push:
    enabled: true
    blocking: true
    agents: ["security", "performance", "quality"]
    severity_threshold: "medium"

# File patterns to review
include:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"
  - "**/*.java"

# File patterns to ignore
exclude:
  - "**/*_test.py"
  - "**/*.min.js"
  - "migrations/**"
  - "vendor/**"
  - "node_modules/**"

# Agent-specific configuration
agents:
  security:
    enabled: true
    severity_threshold: "high"
  performance:
    enabled: true
    complexity_threshold: "O(n²)"
  quality:
    enabled: true
    max_function_length: 50
```

### Bypass Mechanisms

```bash
# Bypass pre-commit hook
git commit --no-verify -m "Emergency fix"

# Bypass specific review (environment variable)
CODEVAULT_SKIP=1 git commit -m "Skip review"

# Advisory mode (warning only, don't block)
export CODEVAULT_ADVISORY_MODE=1
git commit -m "Warn but don't block"
```

---

## Verification & Testing

### Health Check Commands

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Detailed health check
curl "http://localhost:8000/api/v1/health?detailed=true"

# Check specific components
docker-compose exec api python -c "
from codevault.health import check_database, check_redis, check_llm
print('DB:', check_database())
print('Redis:', check_redis())
print('LLM:', check_llm())
"
```

### Running Test Reviews

**Test with sample code:**

```bash
# Create test file
cat > test_code.py << 'EOF'
import os

# Hardcoded secret (should be detected)
API_KEY = "sk-1234567890"

# SQL injection vulnerability (should be detected)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

# O(n²) complexity (should be detected)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
EOF

# Review it
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer $CODEVAULT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"$(cat test_code.py | jq -Rs .)\", \"language\": \"python\"}"
```

**Expected to detect:**
- Critical: Hardcoded API key
- Critical: SQL injection vulnerability  
- High: O(n²) algorithmic complexity

---

## Troubleshooting

### Common Issues

**Issue: "Connection refused" when calling API**

```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs api

# Restart services
docker-compose restart
```

**Issue: "Invalid API key"**

```bash
# Verify key format
echo $CODEVAULT_API_KEY  # Should start with cvai_

# Create new key
docker-compose exec api python -m codevault.cli create-api-key --name "new-key"
```

**Issue: "LLM provider unavailable"**

```bash
# Test OpenAI connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Ollama connection
curl http://localhost:11434/api/tags

# Check provider configuration
docker-compose exec api python -c "
import os
print('Provider:', os.getenv('LLM_PROVIDER'))
print('OpenAI Key:', os.getenv('OPENAI_API_KEY')[:10] + '...' if os.getenv('OPENAI_API_KEY') else 'Not set')
"
```

**Issue: "Database connection failed"**

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db psql -U codevault -c "SELECT 1"

# Reset database
docker-compose down -v  # WARNING: Deletes data
docker-compose up -d
```

**Issue: Slow reviews**

```bash
# Check cache hit rate
curl http://localhost:8000/api/v1/health?detailed=true | jq '.components.cache'

# Clear cache if needed
docker-compose exec redis redis-cli FLUSHALL

# Check LLM response times
docker-compose logs api | grep "llm_latency"
```

---

## Upgrade & Migration

### Upgrading CodeVault

```bash
# Pull latest version
docker-compose pull

# Backup database
docker-compose exec db pg_dump -U codevault codevault > backup.sql

# Stop services
docker-compose down

# Start with new version
docker-compose up -d

# Run migrations
docker-compose exec api python -m codevault.cli migrate
```

### Migrating from SQLite to PostgreSQL

```bash
# Export from SQLite
docker-compose exec api python -m codevault.cli export --format sql > export.sql

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://codevault:password@db:5432/codevault

# Restart with PostgreSQL
docker-compose up -d db
sleep 10

# Import data
docker-compose exec api python -m codevault.cli import < export.sql
```

---

**Next Steps:**
- [Configuration Reference](05-configuration-reference.md) - Fine-tune settings
- [Monitoring & Operations](06-monitoring-operations.md) - Production operations

---

*CodeVault AI Installation Guide - v0.1.0*
