# Security Policy

The **Cerberus** team takes the security of our multi-agent code review platform and its users seriously. If you discover a vulnerability, please follow the guidelines below to report it responsibly.

---

## 🛡️ Supported Versions

We actively maintain and provide security patches for the following versions:

| Version | Supported          | Security Notes |
|:-------:|:------------------:|:---------------|
| `0.1.x` | :white_check_mark: | Current active release branch |
| `< 0.1.0` | :x:              | Development prototypes |

---

## 🚨 Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues, discussions, or pull requests.**

If you discover a potential security vulnerability in Cerberus:

1. **Email the maintainers**: Send a detailed advisory to `thenappanmasterz1311@gmail.com` with the subject tag `[SECURITY] Cerberus Vulnerability Report`.
2. **GitHub Private Security Advisory**: Alternatively, navigate to the **Security** tab of this repository and click **"Report a vulnerability"** to open a private advisory.

### What to include in your report

To help us triage and resolve the issue quickly, please provide:
- A descriptive summary of the issue and affected components (e.g., API Gateway, Agent Orchestrator, LLM Provider, Key Storage).
- Clear step-by-step reproduction steps or a minimal proof-of-concept (PoC) script.
- Potential impact and severity assessment (e.g., CVSS estimate).
- Any proposed mitigations or workarounds.

---

## ⏱️ Response Timelines

- **Initial Acknowledgment**: Within 24-48 hours of receipt.
- **Triage & Assessment**: Within 5 business days.
- **Patch Development & Release**: Critical vulnerabilities will be prioritized for expedited release.
- **Public Disclosure**: Coordinated after a fix has been verified and released to users.

---

## 🔒 Safe Harbor

We will not pursue legal action against individuals who conduct security research in good faith, provided that:
- You make every effort to avoid privacy violations, data destruction, and service interruption.
- You give us reasonable time to remedy the issue before making any details public.
- You do not exploit the vulnerability beyond what is strictly necessary to demonstrate proof-of-concept.
