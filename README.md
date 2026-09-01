# 🛡️ RiskShield AI

### AI-Powered Financial Risk Detection, Fraud Intelligence & Investigation Copilot

> **RiskShield AI** is an intelligent financial risk-management platform that combines machine-learning-based transaction risk detection with an AI-powered investigation copilot to help analysts identify suspicious financial activity, understand the reasons behind risk scores, investigate transactions, and make evidence-based decisions.

---

## 🌐 Overview

**RiskShield AI** is designed as an end-to-end financial risk intelligence platform.

Instead of relying solely on an AI chatbot to determine whether a transaction is fraudulent, RiskShield separates **risk detection** from **AI-assisted investigation**.

The core Risk Engine analyzes financial transactions and produces structured evidence such as:

* Risk Score
* Fraud Probability
* Risk Level
* Anomalies
* Triggered Risk Rules
* Risk Factors
* Transaction Features
* Recommended Actions

The **RiskShield AI Copilot**, powered by **Zephyr 7B through Ollama**, converts this structured evidence into human-readable explanations and investigation assistance.

### Core Philosophy

```text
             TRANSACTION
                  │
                  ▼
        ┌───────────────────┐
        │   RISK ENGINE     │
        │ ML + Rules +      │
        │ Anomaly Detection │
        └─────────┬─────────┘
                  │
                  ▼
           RISK EVIDENCE
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   Risk Dashboard      AI COPILOT
                            │
                            ▼
                       Zephyr 7B
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
       Explain          Investigate       Recommend
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                     ANALYST DECISION
```

---

## ✨ Key Features

### 🔍 Intelligent Risk Detection

Analyze financial transactions using the RiskShield risk-analysis pipeline.

Provides:

* Transaction risk scoring
* Fraud probability
* Risk classification
* Anomaly detection
* Rule-based risk signals
* Behavioral indicators
* Suspicious transaction identification

### 🧠 AI Risk Investigation Copilot

RiskShield includes an optional AI Copilot powered by:

```text
HuggingFaceH4/zephyr-7b-beta
        ↓
      Ollama
```

The Copilot can answer questions such as:

> Why is this transaction high risk?

> What are the strongest risk indicators?

> Which rules were triggered?

> What should the analyst investigate next?

> Summarize this case.

> Investigate this transaction.

### 📊 Explainable Risk Analysis

RiskShield does not simply output:

```text
HIGH RISK
```

It provides the evidence behind the decision.

Example:

```text
Risk Score: 87/100
Risk Level: HIGH
Fraud Probability: 87%

Primary Risk Factors:
• Unusually high transaction amount
• Previously unseen device
• Geographic anomaly
• Abnormal transaction frequency

Triggered Rules:
• RULE_HIGH_AMOUNT
• RULE_NEW_DEVICE

Recommended Action:
STEP-UP AUTHENTICATION
```

The Copilot transforms this structured evidence into an analyst-friendly explanation.

---

## 🤖 AI Copilot

### Why use an LLM?

Traditional risk engines are excellent at detecting patterns but often produce technical outputs that require interpretation.

The Copilot acts as an **investigation intelligence layer**.

```text
Risk Engine
     │
     ▼
Structured Evidence
     │
     ▼
RiskShield Copilot
     │
     ▼
Zephyr 7B
     │
     ▼
Human-readable Investigation
```

### Copilot Capabilities

| Capability                 | Description                                        |
| -------------------------- | -------------------------------------------------- |
| 🔍 Explain Risk            | Explains why a transaction received its risk score |
| 🧩 Risk Factors            | Identifies important contributing signals          |
| 📜 Rule Explanation        | Explains triggered risk rules                      |
| 🕵️ Investigation          | Assists analysts in investigating transactions     |
| 💡 Recommendations         | Suggests evidence-based next steps                 |
| 📝 Summarization           | Generates investigation summaries                  |
| 💬 Analyst Q&A             | Answers natural-language questions                 |
| 📊 Evidence Interpretation | Converts structured signals into readable insights |

---

## 🔐 AI Safety Architecture

Zephyr is **not** the authoritative fraud-detection engine.

```text
                 TRANSACTION
                      │
                      ▼
              ┌───────────────┐
              │  RISK ENGINE  │
              └───────┬───────┘
                      │
                      ▼
               AUTHORITATIVE
               RISK EVIDENCE
                      │
                      ▼
               ┌──────────────┐
               │   ZEPHYR 7B  │
               └──────┬───────┘
                      │
                      ▼
              HUMAN-READABLE
               INTERPRETATION
```

The Copilot:

* cannot modify the risk score
* cannot override the Risk Engine
* cannot invent transaction information
* cannot fabricate investigation evidence
* cannot arbitrarily execute SQL
* cannot access secrets
* must distinguish observed evidence from interpretation
* must explicitly state when information is unavailable

---

## 🏗️ Complete System Architecture

### High-Level Architecture

```text
                           ┌─────────────────────┐
                           │       ANALYST       │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  RISKSHIELD FRONTEND│
                           │                     │
                           │ Dashboard           │
                           │ Transactions        │
                           │ Risk Analysis       │
                           │ AI Copilot          │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │    BACKEND API      │
                           │                     │
                           │ Transaction API     │
                           │ Risk API            │
                           │ Copilot API          │
                           │ Authentication      │
                           └──────────┬──────────┘
                                      │
                  ┌───────────────────┼───────────────────┐
                  │                   │                   │
                  ▼                   ▼                   ▼
          ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
          │ RISK ENGINE  │    │ DATA LAYER   │    │ AI COPILOT   │
          │              │    │              │    │              │
          │ ML Models    │    │ Transactions │    │ Context      │
          │ Rules        │    │ Datasets     │    │ Builder      │
          │ Features     │    │ History      │    │ Prompting    │
          │ Anomalies    │    │              │    │              │
          └──────┬───────┘    └──────────────┘    └──────┬───────┘
                 │                                       │
                 ▼                                       ▼
          ┌──────────────┐                        ┌──────────────┐
          │ Risk Score   │                        │   Ollama     │
          │ Risk Level   │                        └──────┬───────┘
          │ Fraud Prob.  │                               │
          │ Risk Signals │                               ▼
          └──────────────┘                        ┌──────────────┐
                                                  │  Zephyr 7B   │
                                                  └──────────────┘
```

---

## 🔄 End-to-End Transaction Flow

```text
1. Transaction enters RiskShield
             │
             ▼
2. Transaction preprocessing
             │
             ▼
3. Feature extraction
             │
             ▼
4. ML / risk analysis
             │
             ▼
5. Rule evaluation
             │
             ▼
6. Anomaly detection
             │
             ▼
7. Risk score generation
             │
             ▼
8. Risk evidence generated
             │
             ▼
9. Evidence displayed in dashboard
             │
             ▼
10. Analyst opens Copilot
             │
             ▼
11. Structured evidence supplied to Zephyr
             │
             ▼
12. Zephyr interprets the evidence
             │
             ▼
13. Explanation / investigation / recommendation
             │
             ▼
14. Analyst makes final decision
```

---

## 🧠 AI Architecture

```text
                ┌────────────────────────┐
                │    Financial Data      │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ Feature Engineering    │
                └────────────┬───────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ Risk Detection Engine  │
                └────────────┬───────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
             ML Prediction        Rule Engine
                  │                     │
                  └──────────┬──────────┘
                             ▼
                     Risk Evidence
                             │
                             ▼
                   Copilot Context
                             │
                             ▼
                       Zephyr 7B
                             │
                             ▼
                   Analyst Response
```

---

## 🧩 Risk Engine

The Risk Engine is the authoritative component responsible for evaluating transaction risk.

### Responsibilities

* Transaction preprocessing
* Feature engineering
* Risk scoring
* Fraud probability estimation
* Rule evaluation
* Anomaly identification
* Risk classification
* Risk evidence generation

### Example Risk Output

```json
{
  "transaction_id": "TX-102",
  "risk_score": 87,
  "risk_level": "HIGH",
  "fraud_probability": 0.87,
  "signals": [
    {
      "name": "unusual_amount",
      "severity": "high"
    },
    {
      "name": "new_device",
      "severity": "medium"
    }
  ],
  "triggered_rules": [
    "RULE_HIGH_AMOUNT",
    "RULE_NEW_DEVICE"
  ]
}
```

---

## 📚 Data Layer

RiskShield can operate using banking and financial datasets for model development, testing and evaluation.

Supported data sources include:

* Fraud transaction datasets
* Banking transaction datasets
* Financial crime datasets
* Synthetic transaction data
* Historical risk cases

### Synthetic Dataset

A synthetic dataset consists of artificially generated financial records designed to resemble real-world transaction behavior without exposing actual customer information.

Synthetic data can be used for:

* development
* testing
* demonstrations
* edge-case generation
* model experimentation

---

## 🛡️ Fraud & Risk Intelligence

Potential indicators include:

```text
Transaction Amount
Transaction Frequency
Location
Device
User Behaviour
Historical Activity
Transaction Timing
Velocity
Anomaly Score
Rule Violations
```

These signals can be combined to generate a comprehensive risk assessment.

---

## 💻 Technology Stack

### Frontend

```text
Next.js
React
JavaScript / TypeScript
Tailwind CSS
HTML5
CSS3
```

### Backend

```text
Python
FastAPI / existing Python backend architecture
Uvicorn / Gunicorn
REST APIs
```

### Artificial Intelligence

```text
Machine Learning
Rule-Based Detection
Anomaly Detection
Feature Engineering
```

### AI Copilot

```text
HuggingFaceH4/zephyr-7b-beta
        ↓
Ollama
        ↓
RiskShield Copilot
```

### Infrastructure

```text
Docker
Docker Compose
Nginx
Ubuntu VPS
HTTPS
Git
```

---

## 🔌 API Architecture

### Health

```http
GET /api/health
```

### Copilot Health

```http
GET /api/copilot/health
```

### Copilot Chat

```http
POST /api/copilot/chat
```

### Investigation

```http
POST /api/copilot/investigate
```

The exact endpoints should follow the project's current API conventions.

---

## 🔄 Copilot Request Flow

```text
Analyst
   │
   ▼
"Why is TX-102 high risk?"
   │
   ▼
Frontend
   │
   ▼
Backend API
   │
   ▼
Transaction Context
   │
   ├── Transaction Data
   ├── Risk Score
   ├── Fraud Probability
   ├── Risk Factors
   ├── Triggered Rules
   └── Recommended Action
   │
   ▼
Context Builder
   │
   ▼
Ollama
   │
   ▼
Zephyr 7B
   │
   ▼
Evidence-based Answer
   │
   ▼
Frontend
   │
   ▼
Analyst
```

---

## 🖥️ Local Application Architecture

RiskShield supports the existing local execution workflow.

```text
             EXISTING EXE
                  │
                  ▼
        Dependency Verification
                  │
                  ▼
          Environment Setup
                  │
                  ▼
          Application Server
                  │
          ┌───────┴───────┐
          ▼               ▼
      Frontend         Backend
                          │
                          ▼
                     Risk Engine
```

The existing `.exe` launchers remain preserved.

The AI Copilot is an **optional capability**.

---

## 🐳 Docker Architecture

```text
                 Docker Compose
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
      Frontend                   Backend
                                    │
                                    ▼
                                 Ollama
                                    │
                                    ▼
                                Zephyr 7B
```

For the primary VPS architecture, Ollama can run directly on the host while Frontend and Backend run in Docker.

---

## ☁️ Production VPS Architecture

```text
                         INTERNET
                            │
                            ▼
                     HTTPS / DOMAIN
                            │
                            ▼
                         NGINX
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
         FRONTEND                    BACKEND API
                                           │
                                           ▼
                                        OLLAMA
                                           │
                                           ▼
                                      ZEPHYR 7B
```

### Production Components

```text
Ubuntu VPS
│
├── Nginx
│
├── Docker
│   ├── RiskShield Frontend
│   └── RiskShield Backend
│
└── Ollama
    └── Zephyr 7B
```

Ollama's port `11434` must not be exposed publicly.

---

## 🚀 Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd riskshield-ai
```

### 2. Configure Environment

Create:

```text
.env
```

based on:

```text
.env.example
```

### 3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 4. Download Zephyr

```bash
ollama pull zephyr:7b-beta
```

### 5. Build Docker Containers

```bash
docker compose build
```

### 6. Start RiskShield

```bash
docker compose up -d
```

### 7. Verify

```bash
docker compose ps
```

Then verify:

```text
/api/health
/api/copilot/health
```

---

## 🔒 Security Architecture

RiskShield follows a defense-in-depth approach.

```text
                    USER
                      │
                      ▼
                 HTTPS / Nginx
                      │
                      ▼
                  Backend API
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Risk Engine              Copilot
                                  │
                                  ▼
                               Ollama
```

### Security Controls

* Environment-based secrets
* HTTPS
* Restricted CORS
* Backend input validation
* Controlled backend tools
* No arbitrary SQL execution by the LLM
* No public Ollama endpoint
* No credentials in frontend
* No secrets committed to Git
* Safe error handling
* Request validation
* Optional authentication integration

---

## 📁 Project Structure

```text
RiskShield/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── copilot/
│   │   │   ├── ollama_client.py
│   │   │   ├── service.py
│   │   │   ├── prompts.py
│   │   │   └── schemas.py
│   │   ├── risk_engine/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── data/
│   ├── datasets/
│   ├── processed/
│   └── indexes/
│
├── scripts/
│
├── docker-compose.yml
├── nginx/
├── .env.example
├── .gitignore
├── DEPLOYMENT.md
└── README.md
```

---

## ⚙️ Configuration

| Variable          | Purpose                     |
| ----------------- | --------------------------- |
| `APP_ENV`         | Application environment     |
| `BACKEND_HOST`    | Backend bind address        |
| `BACKEND_PORT`    | Backend port                |
| `OLLAMA_BASE_URL` | Ollama server address       |
| `OLLAMA_MODEL`    | AI model                    |
| `CORS_ORIGINS`    | Allowed frontend origins    |
| `SECRET_KEY`      | Application security secret |
| `DATABASE_URL`    | Database connection         |

---

## 🔄 Four Supported Execution Modes

### Mode 1 — Existing Local Application

```text
Existing EXE
     ↓
RiskShield
     ↓
Risk Engine
```

### Mode 2 — Local AI Copilot

```text
RiskShield
    │
    ▼
Backend
    │
    ▼
Ollama
    │
    ▼
Zephyr 7B
```

### Mode 3 — Docker

```text
Docker Compose
      │
 ┌────┴────┐
 ▼         ▼
Frontend  Backend
             │
             ▼
           Ollama
```

### Mode 4 — Production VPS

```text
Internet
   │
   ▼
Nginx / HTTPS
   │
   ▼
Docker Frontend
   │
   ▼
Docker Backend
   │
   ▼
Host Ollama
   │
   ▼
Zephyr 7B
```

---

## ⚡ Performance Considerations

Zephyr 7B inference performance depends on:

* CPU
* available RAM
* GPU
* GPU VRAM
* quantization
* concurrent requests
* context size
* transaction workload

The Risk Engine and Copilot remain separated so slow LLM inference does not block core risk analysis.

---

## 📈 Scalability

```text
Frontend
    │
    ▼
Backend API
    │
    ├── Risk Engine
    │
    ├── Data Layer
    │
    └── Copilot
             │
             ▼
           Ollama
```

Components can be scaled or replaced independently.

---

## 🧪 Testing

### Risk Engine

* Transaction processing
* Feature extraction
* Risk scoring
* Rule evaluation
* Anomaly detection

### Copilot

* Valid transaction questions
* Missing evidence
* Invalid transaction IDs
* Ollama unavailable
* Zephyr unavailable
* Timeout handling
* Large context handling

### Security

* Secret isolation
* Input validation
* CORS
* Arbitrary SQL prevention
* LLM prompt protection

### Deployment

```bash
docker compose config
docker compose build
docker compose up
```

---

## 🩺 Health Monitoring

Example:

```text
Backend       → HEALTHY
Risk Engine   → HEALTHY
Ollama        → HEALTHY
Zephyr 7B    → AVAILABLE
Copilot       → AVAILABLE
```

If Ollama fails:

```text
Backend       → HEALTHY
Risk Engine   → HEALTHY
Ollama        → UNAVAILABLE
Copilot       → UNAVAILABLE
```

The core RiskShield platform continues functioning.

---

## 🛠️ Troubleshooting

### Ollama unavailable

```bash
ollama list
```

### Zephyr model missing

```bash
ollama pull zephyr:7b-beta
```

### Check Docker

```bash
docker --version
docker compose version
```

### Check running services

```bash
docker compose ps
```

### View logs

```bash
docker compose logs -f
```

---

## 🎯 Use Cases

* Financial Fraud Detection
* Transaction Investigation
* Analyst Assistance
* Risk Explanation
* Case Summarization
* Risk Operations
* Suspicious Activity Investigation

---

## 🚀 Future Scope

* Advanced behavioral profiling
* Real-time transaction streams
* Graph-based fraud detection
* Entity relationship analysis
* Account takeover detection
* Automated investigation workflows
* Multi-agent investigation orchestration
* Advanced RAG
* Historical case retrieval
* Analyst feedback loops
* Model monitoring
* Risk model drift detection
* Distributed inference
* GPU acceleration
* Enterprise authentication
* Audit trails
* Advanced case management

---

## 🏆 Project Highlights

```text
┌─────────────────────────────────────────────┐
│              RISKSHIELD AI                  │
├─────────────────────────────────────────────┤
│                                             │
│  🔍 Intelligent Risk Detection              │
│  🧠 AI Investigation Copilot               │
│  🤖 Zephyr 7B + Ollama                     │
│  📊 Explainable Risk Analysis              │
│  🛡️ Security-Aware Architecture            │
│  💻 Local AI Capability                     │
│  🐳 Docker Ready                            │
│  ☁️ VPS Deployable                          │
│  🔐 Evidence-Based AI                      │
│  👨‍💼 Human-in-the-Loop Investigation       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📌 Project Status

| Component              | Status              |
| ---------------------- | ------------------- |
| Core Risk Management   | 🟢 Active           |
| AI Copilot             | 🟢 Integrated       |
| Local Ollama / Zephyr  | 🟢 Supported        |
| Existing EXE Execution | 🟢 Preserved        |
| Docker                 | 🟢 Deployment Ready |
| VPS Deployment         | 🟢 Supported        |

---

## 👨‍💻 Contributing

```bash
git clone <repository-url>

git checkout -b feature/<feature-name>

git add .

git commit -m "Add <feature>"

git push origin feature/<feature-name>
```

Create a pull request describing:

* What changed
* Why it changed
* Testing performed
* Deployment implications

---

## ⚠️ Disclaimer

RiskShield AI is an analytical and decision-support system.

Its risk assessments and AI-generated explanations should be reviewed by qualified analysts and should not be treated as an unconditional determination of fraud.

The AI Copilot provides assistance based on evidence supplied by the RiskShield system and should not replace appropriate financial, legal, compliance, or security procedures.

---

## 🧰 Technology Summary

| Layer           | Technology                                   |
| --------------- | -------------------------------------------- |
| Frontend        | Next.js / React                              |
| Styling         | Tailwind CSS                                 |
| Backend         | Python                                       |
| API             | REST                                         |
| Risk Engine     | Machine Learning + Rules + Anomaly Detection |
| AI Copilot      | Zephyr 7B                                    |
| Model Serving   | Ollama                                       |
| Data            | Banking / Financial / Synthetic Datasets     |
| Containers      | Docker                                       |
| Orchestration   | Docker Compose                               |
| Reverse Proxy   | Nginx                                        |
| Production OS   | Ubuntu                                       |
| Deployment      | VPS / Cloud                                  |
| Protocol        | HTTP / HTTPS                                 |
| Version Control | Git                                          |

---

## 🛡️ RiskShield AI

### **Detect. Explain. Investigate. Decide.**

```text
Raw Transaction
      ↓
Risk Detection
      ↓
Risk Evidence
      ↓
AI Explanation
      ↓
Investigation
      ↓
Actionable Decision
```

**RiskShield doesn't just tell you that a transaction is risky — it helps explain why, investigate the evidence, and determine what to examine next.**
