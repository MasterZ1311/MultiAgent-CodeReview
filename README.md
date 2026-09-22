# MultiAgent-CodeReview

**Autonomous Multi-Agent Code Review & Quality Assurance System (CodeVault AI / Cerberus)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/codevault/api)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](docs/08-developer-guide.md)

CodeVault AI is an intelligent code review system that uses specialized AI agents to analyze your code from multiple perspectives—security, performance, and quality—providing expert-level insights automatically.

---

## ✨ Key Features

🤖 **Multi-Agent Intelligence**
- Three specialized AI agents (Security, Performance, Quality)
- Parallel execution for fast results
- Natural language explanations for every finding

🚀 **Developer-Friendly**
- 5-minute Docker Compose setup
- Git pre-commit/pre-push hooks
- RESTful API for custom integrations
- CLI tool for on-demand reviews

🔒 **Privacy-Focused**
- Support for local LLM models (Ollama)
- OpenAI, Anthropic, Azure OpenAI integration
- Configurable data retention
- Air-gapped deployment support

⚡ **Fast & Efficient**
- Intelligent result caching (70%+ hit rate)
- Incremental reviews (only changed code)
- Batch processing for multiple files

📊 **Actionable Insights**
- Severity-based prioritization
- Specific code recommendations
- Export to JSON, Markdown, HTML, SARIF

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (or Ollama for local LLMs)

### Installation (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/codevault-ai/codevault.git
cd codevault

# 2. Configure
cp .env.example .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# 3. Start services
docker-compose up -d

# 4. Verify installation
curl http://localhost:8000/api/v1/health
```

### First Review

```bash
# Create API key
docker-compose exec api python -m codevault.cli create-api-key --name "my-key"

# Review code
curl -X POST http://localhost:8000/api/v1/review \
  -H "Authorization: Bearer cvai_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def login(user, pwd):\n    if user == \"admin\" and pwd == \"admin\":\n        return True",
    "language": "python"
  }'
```

**Result:** CodeVault AI detects hardcoded credentials (Critical) and weak authentication (High).

---

## 📖 Architecture

```
┌─────────────┐
│   Client    │  Git Hooks, CLI, API
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│     FastAPI Gateway         │  Authentication, Rate Limiting
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│   Review Coordinator        │  Orchestration, Caching
└──────┬──────────────────────┘
       │
       ├──────────┬──────────┬────────────┐
       ▼          ▼          ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Security │ │Performance│ │  Quality │  Specialized AI Agents
│  Agent   │ │  Agent    │ │  Agent   │
└────┬─────┘ └────┬──────┘ └────┬─────┘
     │            │             │
     └────────────┼─────────────┘
                  ▼
         ┌────────────────┐
         │  LLM Provider  │  OpenAI, Anthropic, Ollama
         └────────────────┘
```

**Agents:**
- **Security Agent**: Detects vulnerabilities (SQL injection, XSS, secrets, weak crypto)
- **Performance Agent**: Finds bottlenecks (O(n²) loops, N+1 queries, memory leaks)
- **Code Quality Agent**: Reviews maintainability (naming, structure, documentation)

---

## 📚 Documentation

### Getting Started
- 📖 **[Installation & Setup Guide](docs/04-installation-setup.md)** - Comprehensive setup instructions
- 🏗️ **[Architecture Overview](docs/01-architecture-overview.md)** - System design and components
- 🔌 **[API Reference](docs/02-api-reference.md)** - Complete API documentation

### Configuration & Operations
- ⚙️ **[Configuration Reference](docs/05-configuration-reference.md)** - All configuration options
- 📊 **[Monitoring & Operations](docs/06-monitoring-operations.md)** - Production operations guide
- 🔒 **[Security & Compliance](docs/07-security-compliance.md)** - Security best practices

### Development
- 🤖 **[Agent Specifications](docs/03-agent-specifications.md)** - How agents work
- 👨‍💻 **[Developer Guide](docs/08-developer-guide.md)** - Contributing and extending
- ❓ **[FAQ](docs/FAQ.md)** - Frequently asked questions

---

## 🎯 Use Cases

### 1. Pre-Commit Code Review

```bash
# Install git hook
codevault init

# Automatically reviews code on every commit
git commit -m "Add login feature"
# → CodeVault AI reviews changes
# → Blocks commit if critical issues found
```

### 2. CI/CD Integration

```yaml
# .github/workflows/code-review.yml
- name: Run CodeVault AI
  run: |
    codevault-cli review --path . --format sarif > results.sarif
    
- name: Upload results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### 3. IDE Integration

```python
# VS Code extension
result = codevault.review(active_file)
display_inline_suggestions(result)
```

---

## 🔧 Configuration

### LLM Providers

**OpenAI (Recommended for best quality):**
```yaml
llm:
  provider: openai
  openai:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4-turbo-preview
```

**Ollama (Free, local, privacy-first):**
```yaml
llm:
  provider: ollama
  ollama:
    base_url: http://localhost:11434
    model: codellama
```

**Anthropic Claude:**
```yaml
llm:
  provider: anthropic
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-3-sonnet-20240229
```

### Agent Configuration

```yaml
agents:
  security:
    enabled: true
    severity_threshold: high
    secret_scanning: true
  
  performance:
    enabled: true
    complexity_threshold: "O(n²)"
  
  quality:
    enabled: true
    style_guide: pep8
    max_function_length: 50
```

---

## 🌟 Examples

### Python - Security Issues

**Code:**
```python
import os

API_KEY = "sk-1234567890"  # ❌ Hardcoded secret

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌ SQL injection
    return db.execute(query)
```

**CodeVault AI Findings:**
- 🔴 **Critical**: Hardcoded API key detected
- 🔴 **Critical**: SQL injection vulnerability
- 💡 **Recommendation**: Use environment variables and parameterized queries

### JavaScript - Performance Issues

**Code:**
```javascript
function findDuplicates(items) {
  const duplicates = [];
  for (let i = 0; i < items.length; i++) {  // ❌ O(n²) complexity
    for (let j = i + 1; j < items.length; j++) {
      if (items[i] === items[j]) {
        duplicates.push(items[i]);
      }
    }
  }
  return duplicates;
}
```

**CodeVault AI Findings:**
- 🟡 **High**: O(n²) algorithmic complexity
- 💡 **Recommendation**: Use a Set for O(n) solution
- 📈 **Impact**: 1000x faster for large inputs

---

## 🤝 Contributing

We welcome contributions! See our [Developer Guide](docs/08-developer-guide.md) for:
- Setting up development environment
- Creating custom agents
- Adding new features
- Testing guidelines

**Quick Start for Contributors:**
```bash
git clone https://github.com/codevault-ai/codevault.git
cd codevault
pip install -e ".[dev]"
pytest
```

---

## 📊 Project Status

- ✅ **Core Features**: Complete
- ✅ **Documentation**: Complete
- 🚧 **IDE Plugins**: In Progress
- 📋 **Planned**: Team collaboration features, historical trend analysis

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://langchain.com/) - LLM framework
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://anthropic.com/) - Claude models
- [Ollama](https://ollama.ai/) - Local LLM runtime

---

## 📞 Support

- 📧 Email: support@codevault.ai
- 💬 Discord: [Join our community](https://discord.gg/codevault)
- 🐛 Issues: [GitHub Issues](https://github.com/codevault-ai/codevault/issues)
- 📖 Documentation: [docs.codevault.ai](https://docs.codevault.ai)

---

## ⭐ Star History

If you find CodeVault AI useful, please consider starring the repository!

[![Star History Chart](https://api.star-history.com/svg?repos=codevault-ai/codevault&type=Date)](https://star-history.com/#codevault-ai/codevault&Date)

---

**Built with ❤️ for developers who care about code quality**
