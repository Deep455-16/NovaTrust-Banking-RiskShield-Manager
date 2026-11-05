# 🔐 Security Policy

RiskShield AI is a defensive financial-security platform, so we hold ourselves to a high bar on the security of the platform itself. This document explains how to report vulnerabilities, what the security model is, and how to deploy RiskShield safely.

> See also: [README](README.md) · [ARCHITECTURE](ARCHITECTURE.md)

---

## 📑 Contents

1. [Supported Versions](#-supported-versions)
2. [Reporting a Vulnerability](#-reporting-a-vulnerability)
3. [Security Model](#-security-model)
4. [Threat Model](#-threat-model)
5. [AI / LLM-Specific Security](#-ai--llm-specific-security)
6. [Secure Deployment Checklist](#-secure-deployment-checklist)
7. [Data Handling & Privacy](#-data-handling--privacy)
8. [Security Testing](#-security-testing)
9. [Scope](#-scope)
10. [Responsible Use](#-responsible-use)

---

## ✅ Supported Versions

Security fixes are applied to the latest release and the `main` branch.

| Version | Supported |
|---|---|
| Latest release | ✅ |
| `main` branch | ✅ |
| Older releases | ❌ Please upgrade |

---

## 📣 Reporting a Vulnerability

**Please do not open a public issue for security problems.**

Report privately using either route:

1. **GitHub private vulnerability reporting:** go to the repository's **Security** tab → **Report a vulnerability**.
2. **Direct contact:** message the maintainer, [@Deep455-16](https://github.com/Deep455-16), through GitHub and ask for a private channel.

### What to include

- A clear description of the issue and its impact
- Steps to reproduce, or a proof of concept
- Affected component (Risk Engine, Copilot, API, frontend, installer, Docker/Nginx config)
- Version, commit, or release you tested
- Any suggested fix or mitigation

### What to expect

| Stage | Target |
|---|---|
| Acknowledgement | Within 5 business days |
| Initial assessment and severity | Within 10 business days |
| Fix or mitigation plan | Shared once the issue is confirmed |
| Public disclosure | Coordinated with the reporter after a fix is available |

This is a student-maintained open-source project, so these are good-faith targets, not contractual SLAs. We will credit reporters in the release notes unless they prefer to remain anonymous.

### Please do

- Give us reasonable time to fix the issue before disclosing it
- Test only against your own instances and data
- Avoid accessing, modifying, or destroying data that isn't yours

---

## 🧱 Security Model

RiskShield follows **defense in depth**.

```text
User ─▶ HTTPS / Nginx ─▶ Backend API (validation · CORS · auth)
                              ├─▶ Risk Engine   (authoritative)
                              └─▶ Copilot ─▶ Ollama (private only)
```

### Core controls

| Control | Description |
|---|---|
| **Environment-based secrets** | Keys and credentials come from `.env` or the host environment, never from code |
| **No secrets in Git** | `.env` is git-ignored; `.env.example` documents variable names only |
| **No credentials in the frontend** | The browser never receives secrets or model endpoints |
| **HTTPS in production** | TLS terminated at Nginx |
| **Restricted CORS** | Only origins listed in `CORS_ORIGINS` are allowed |
| **Request validation** | All API inputs are validated against schemas |
| **Safe error handling** | Clients get generic errors; details stay in server logs |
| **Controlled backend tools** | The Copilot has no direct database or shell access |
| **Private Ollama** | Port `11434` is never exposed publicly |
| **Optional authentication** | Integrates with an existing identity layer |

---

## 🎯 Threat Model

| Threat | Example | Mitigation |
|---|---|---|
| **Credential or secret leakage** | `.env` committed, key sent to the browser | Env-based secrets, git-ignore, secret scanning before release |
| **Public model exposure** | Ollama reachable from the internet | Bind to localhost or a private network; firewall `11434` |
| **Injection** | Malformed fields reaching SQL or templates | Schema validation, parameterized queries, no LLM-generated SQL |
| **Cross-origin abuse** | Hostile site calling the API from a victim's browser | Restricted CORS, authentication where enabled |
| **Prompt injection** | Transaction memo field containing "ignore previous instructions" | Fields treated as untrusted data; Copilot has no write or decision powers |
| **Risk-score tampering via AI** | LLM output altering the decision | No write path from Copilot to Risk Engine; analyst decides |
| **Information disclosure** | Stack traces or internals in errors | Safe error handling, minimal API responses |
| **Denial of service** | Oversized context or request floods to the LLM | Timeouts, context-size limits, engine isolated from LLM latency |
| **Supply chain** | Malicious or vulnerable dependency | Pinned versions, dependency auditing |
| **Installer tampering** | Modified `.exe` redistributed | Download only from the official GitHub Releases page |

---

## 🤖 AI / LLM-Specific Security

The Copilot (Zephyr 7B via Ollama) is deliberately **sandboxed from authority**.

| Rule | Detail |
|---|---|
| **Advisory only** | It explains and recommends; it cannot approve, reject, or change a risk score |
| **Evidence-grounded** | Prompts contain only structured evidence from the Risk Engine |
| **No arbitrary SQL** | The model has no database tool |
| **No secrets in prompts** | API keys, `SECRET_KEY`, and connection strings are never included |
| **Untrusted input** | Transaction text such as merchant names or notes is treated as data, not instructions |
| **Honest uncertainty** | When evidence is missing, the Copilot must say so instead of guessing |
| **Fail closed** | If Ollama is down or times out, the Copilot reports unavailable while the Risk Engine keeps running |

**Residual risk:** LLMs can be steered by crafted text and can produce incorrect explanations. This is why a human analyst makes every final decision, and why Copilot output must never be treated as proof of fraud.

---

## 🚀 Secure Deployment Checklist

**Before going live**

- [ ] Copy `.env.example` to `.env` and set a strong, unique `SECRET_KEY`
- [ ] Confirm `.env` is not tracked by Git (`git ls-files | grep .env` returns nothing)
- [ ] Set `APP_ENV=production`
- [ ] Set `CORS_ORIGINS` to your exact frontend origin(s), with no wildcards
- [ ] Serve everything over HTTPS through Nginx with a valid certificate
- [ ] Redirect HTTP to HTTPS

**Network**

- [ ] Ollama bound to `127.0.0.1` or a private Docker network, never `0.0.0.0` on a public interface
- [ ] Firewall allows only 80/443 (and SSH from trusted IPs)
- [ ] Backend port not directly reachable from the internet; only via Nginx
- [ ] SSH uses key authentication, with password login disabled

**Application**

- [ ] Authentication enabled for any multi-user or internet-facing deployment
- [ ] Debug mode and verbose error output disabled
- [ ] Logs do not contain secrets or full transaction payloads
- [ ] Dependencies updated (`pip list --outdated`, `npm audit`)

**Verify**

```bash
docker compose config            # validate configuration
docker compose ps                # confirm only expected services/ports
curl https://<your-domain>/api/health
curl https://<your-domain>/api/copilot/health
# From outside the server, this must FAIL:
curl http://<server-ip>:11434/api/tags
```

---

## 🗂️ Data Handling & Privacy

- **Local-first AI:** with Ollama running locally, transaction context does not need to be sent to an external LLM service.
- **Synthetic data:** use synthetic or anonymized data for demos, testing, and development. Do not load real customer data into a development or demo instance.
- **Minimal context:** the Copilot receives only the evidence needed for the question asked.
- **Retention:** you are responsible for the retention, backup, and deletion policy of the database and logs you deploy.
- **Compliance:** RiskShield is a decision-support tool. Using it with real financial data may bring regulatory obligations (such as data protection and AML rules) that you must evaluate for your jurisdiction.

---

## 🧪 Security Testing

| Area | What we test |
|---|---|
| **Secrets** | No secrets in repo history, frontend bundle, or logs |
| **Input validation** | Malformed, oversized, and unexpected API payloads |
| **CORS** | Disallowed origins are rejected |
| **SQL safety** | No path for LLM-generated or user-supplied SQL execution |
| **Prompt injection** | Adversarial text in transaction fields does not change engine output or leak data |
| **LLM restrictions** | Copilot cannot reach tools beyond its intended scope |
| **Failure handling** | Ollama down, model missing, and timeout cases degrade safely |
| **Deployment** | Compose config, exposed ports, and TLS verified |

---

## 📐 Scope

**In scope:** the RiskShield backend, Risk Engine, Copilot service, frontend, Docker/Nginx configuration, installer scripts, and documentation that could lead to insecure setups.

**Out of scope:**

- Vulnerabilities in third-party software (Ollama, Zephyr model weights, Python, Node.js, Docker, Nginx). Please report those upstream.
- Findings that require physical access, or a device that is already compromised
- Social engineering of maintainers or users
- Denial-of-service from raw volumetric traffic
- Issues in deployments that ignore the [checklist above](#-secure-deployment-checklist) (for example, intentionally exposing Ollama publicly)

---

## ⚖️ Responsible Use

RiskShield is built for **defensive** purposes: detecting suspicious activity, supporting investigations, and reducing financial losses. Do not use it, or findings about it, to commit fraud, evade detection systems, or harm individuals or institutions.

Its outputs are decision support, not a determination of wrongdoing. Qualified analysts and your organization's compliance, legal, and security procedures remain responsible for final decisions.

---

<div align="center">

**🛡️ Thank you for helping keep RiskShield and its users safe.**

</div>
