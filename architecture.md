# 🛡️ RiskShield AI — Architecture

> **A modular, explainable, AI-assisted financial risk detection and investigation platform.**

## 🏗️ Unified System Architecture

```text
                                      ┌──────────────────────┐
                                      │      👨‍💼 ANALYST      │
                                      └──────────┬───────────┘
                                                 │
                                      HTTPS / REST / JSON
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         🖥️ RISKSHIELD FRONTEND                              │
│                                                                              │
│ Dashboard │ Transactions │ Risk Analysis │ Investigation │ AI Copilot       │
│ Next.js / React / TypeScript / Tailwind CSS                                 │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            ⚙️ BACKEND API                                   │
│                     Python / FastAPI / Uvicorn                              │
│                                                                              │
│ Authentication │ Validation │ Transaction API │ Risk API │ Copilot API      │
└───────────────┬──────────────────────┬───────────────────────┬───────────────┘
                │                      │                       │
                ▼                      ▼                       ▼
┌────────────────────────┐   ┌────────────────────┐   ┌───────────────────────┐
│ 🔍 RISK ENGINE         │   │ 📊 DATA LAYER      │   │ 🤖 AI COPILOT         │
│                        │   │                    │   │                       │
│ Preprocessing          │   │ Banking Data       │   │ Context Builder       │
│ Feature Engineering    │   │ Fraud Data         │   │ Prompt Engine         │
│ ML Prediction          │   │ Synthetic Data     │   │ Response Validation   │
│ Rule Engine             │   │ Historical Cases   │   │ Investigation Logic   │
│ Anomaly Detection      │   │ Processed Data     │   │                       │
└───────────┬────────────┘   └────────────────────┘   └───────────┬───────────┘
            │                                                      │
            ▼                                                      ▼
┌────────────────────────┐                              ┌───────────────────────┐
│ 🛡️ RISK EVIDENCE       │                              │       OLLAMA          │
│                        │                              │                       │
│ Risk Score             │                              │ Local Model Server    │
│ Fraud Probability      │                              └───────────┬───────────┘
│ Risk Level             │                                          │
│ Risk Factors           │                                          ▼
│ Triggered Rules        │                              ┌───────────────────────┐
│ Anomalies              │                              │      ZEPHYR 7B        │
│ Recommended Action     │                              │ HuggingFaceH4 Model   │
└───────────┬────────────┘                              └───────────┬───────────┘
            │                                                      │
            └──────────────────────┬───────────────────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │ 💬 COPILOT RESPONSE  │
                         │                      │
                         │ Explain │ Investigate│
                         │ Summarize │ Recommend│
                         └──────────┬───────────┘
                                    │
                                    ▼
                              👨‍💼 ANALYST
```

---

## 🔄 Unified Data Flow

```text
Transaction
    │
    ▼
Validation → Preprocessing → Feature Engineering
    │
    ▼
┌───────────────────────────────────────┐
│ ML Detection + Rules + Anomaly Engine │
└───────────────────┬───────────────────┘
                    ▼
             Risk Evidence
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Risk Dashboard        AI Copilot
                              │
                     Context + Question
                              │
                              ▼
                           Ollama
                              │
                              ▼
                         Zephyr 7B
                              │
                              ▼
                 Explain / Investigate /
                 Summarize / Recommend
                              │
                              ▼
                        Analyst Review
                              │
                              ▼
                       Final Decision
```

---

## 🧠 Core Architecture Principles

| Principle             | Implementation                                                      |
| --------------------- | ------------------------------------------------------------------- |
| **Risk Authority**    | Risk Engine determines the authoritative risk                       |
| **AI Assistance**     | Zephyr interprets evidence; it does not determine fraud             |
| **Explainability**    | Every AI response is grounded in structured risk evidence           |
| **Human-in-the-Loop** | Analyst makes the final decision                                    |
| **Failure Isolation** | Core Risk Engine works even when AI is unavailable                  |
| **Security**          | Backend controls data and AI access                                 |
| **Modularity**        | Frontend, backend, risk engine and AI are independently replaceable |
| **Local-First**       | Ollama + Zephyr can run locally                                     |
| **Deployment Ready**  | Supports EXE, Docker and cloud/VPS deployment                       |
| **Scalability**       | AI inference can later be separated or GPU-accelerated              |

---

## 💻 Technology Stack

```text
Frontend       → Next.js + React + TypeScript + Tailwind CSS
Backend        → Python + FastAPI + Uvicorn
Risk Engine    → ML + Rule Engine + Anomaly Detection
AI             → Zephyr 7B
Model Server   → Ollama
Data           → Banking + Fraud + Synthetic Datasets
Deployment     → Docker + Docker Compose + Nginx + Ubuntu VPS
Protocol       → REST / HTTP / HTTPS / JSON
Local Runtime  → Existing EXE Launchers
Version Control→ Git
```

---

## 🚀 Deployment Architecture

### Local

```text
RiskShield EXE
      │
      ├── Frontend
      ├── Backend
      ├── Risk Engine
      └── Optional Ollama → Zephyr 7B
```

### Docker / Production

```text
                 INTERNET
                    │
                 HTTPS
                    ▼
                  NGINX
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Frontend              Backend
     Container             Container
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
              Risk Engine                Copilot
                                             │
                                             ▼
                                          Ollama
                                             │
                                             ▼
                                         Zephyr 7B
```

**Ollama remains on the private network and should not be publicly exposed.**

---

## 🔐 Security & Reliability

```text
User
 │
 ▼
HTTPS / Nginx
 │
 ▼
Backend Authentication & Validation
 │
 ├── Risk Engine
 │
 └── Controlled AI Context
          │
          ▼
       Ollama
          │
          ▼
       Zephyr 7B
```

Key controls:

* Environment-based secrets
* HTTPS
* Restricted CORS
* Backend input validation
* Controlled AI context
* No arbitrary SQL execution by the LLM
* No direct public Ollama access
* Graceful AI failure
* Core risk detection independent of LLM availability
* Human approval for final decisions

---

## 📁 Logical Project Structure

```text
RiskShield/
├── frontend/          # Next.js UI
├── backend/           # FastAPI services
│   ├── api/           # REST endpoints
│   ├── risk_engine/   # ML + rules + anomalies
│   ├── copilot/       # Zephyr/Ollama integration
│   └── services/      # Business logic
├── data/              # Datasets and processed data
├── scripts/           # Utilities/startup scripts
├── exe/               # Local application launchers
├── nginx/             # Reverse-proxy configuration
├── docker-compose.yml
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

---

## 🔮 Future-Ready Design

The architecture allows future integration of:

```text
Graph Fraud Detection
       ↓
Advanced Behavioral Analytics
       ↓
RAG / Historical Case Retrieval
       ↓
GPU Inference
       ↓
Distributed AI Services
       ↓
Real-Time Transaction Streaming
       ↓
Enterprise Authentication & Audit
```

---

## 🎯 Architecture in One Line

> **RiskShield AI combines ML-based risk detection, rule-based intelligence, anomaly detection and an evidence-grounded Zephyr 7B Copilot into a secure, human-in-the-loop architecture that runs locally and scales to Docker-based cloud deployment.**
