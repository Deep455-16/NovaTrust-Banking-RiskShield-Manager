<div align="center">

# 🛡️ RiskShield AI

### AI-Powered Fraud-Risk Detection, Financial Intelligence & Investigation Copilot

[🚀 Features](#-key-features) •
[🏗️ Architecture](#️-system-architecture) •
[🤖 AI Copilot](#-ai-investigation-copilot) •
[📊 Dashboard](#-dashboard) •
[⚙️ Installation](#️-installation) •
[🛠️ Tech Stack](#️-technology-stack)

</div>

> **RiskShield AI** is an AI-powered financial fraud-risk platform that detects suspicious transactions using machine learning, behavioral signals, anomaly detection, and risk rules — then uses an evidence-grounded AI Copilot to explain the risk, assist investigations, and recommend what analysts should examine next.

<p align="center">

**Detect → Explain → Investigate → Decide**

</p>

---
##      Demo Video Link:
###     https://drive.google.com/file/d/1Bk52ISzRWrvtl91k2djySw37CgwIS7KI/view?usp=sharing  

## ⚡ Quick Install

> **No coding required.** The installer automatically sets up Python, Node.js, Ollama, and the Zephyr AI model — completely silently.

### 👉 [Download RiskShieldSetup.exe](https://github.com/Deep455-16/NovaTrust-Banking-RiskShield-Manager/releases/latest/download/RiskShieldSetup.exe)

1. Click the link above to download `RiskShieldSetup.exe`
2. Double-click the downloaded file to run it
3. Watch the progress bar as everything installs automatically in the background:
   - ✅ Python 3.11
   - ✅ Node.js
   - ✅ Ollama AI Runtime
   - ✅ Zephyr 7B AI Model
   - ✅ All backend & frontend dependencies
4. Click **Finish** — the app opens in your browser automatically!

> **For developers** who want to run from source code:
> ```bash
> git clone https://github.com/Deep455-16/NovaTrust-Banking-RiskShield-Manager.git
> cd NovaTrust-Banking-RiskShield-Manager
> install.bat       # auto-installs all dependencies
> start_app.bat     # launches the app
> ```

---

## 🎯 Problem

Financial fraud creates direct losses for merchants, banks, fintech platforms, and payment ecosystems.

Traditional systems often face two problems:

* 🚨 Suspicious transactions need to be detected quickly.
* 🔎 Analysts need to understand **why** a transaction was flagged.

RiskShield addresses both problems by separating **fraud detection** from **AI-assisted investigation**.

The core Risk Engine makes the risk assessment.

The AI Copilot helps the analyst understand and investigate that assessment.

---

## 💡 Solution

RiskShield is built around a simple architecture:

```text
                         TRANSACTION
                              │
                              ▼
                    ┌─────────────────────┐
                    │  FRAUD-RISK DETECTOR│
                    │                     │
                    │ ML Models           │
                    │ Risk Rules          │
                    │ Anomaly Detection   │
                    │ Behavioral Signals  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   RISK ASSESSMENT   │
                    │                     │
                    │ Risk Score          │
                    │ Fraud Probability   │
                    │ Risk Level          │
                    └──────────┬──────────┘
                               │
                               ▼
                       RISK EVIDENCE
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             RISK DASHBOARD         AI COPILOT
                                          │
                                          ▼
                                     ZEPHYR 7B
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                     Explain         Investigate      Recommend
                         │                │                │
                         └────────────────┼────────────────┘
                                          ▼
                                   HUMAN ANALYST
                                          │
                                          ▼
                                  FINAL DECISION
```

### Core principle

> **The Risk Engine detects. The AI Copilot explains. The analyst decides.**

Zephyr is **not** the authoritative fraud detector and cannot override the Risk Engine.

---

## 🚀 Key Features

## 🔍 1. AI-Powered Fraud-Risk Detection

RiskShield analyzes financial transactions using multiple complementary signals:

* Machine-learning predictions
* Transaction risk scoring
* Fraud probability estimation
* Rule-based risk detection
* Behavioral indicators
* Anomaly detection
* Transaction velocity
* Historical activity
* Device signals
* Geographic signals
* Transaction timing
* Amount-based anomalies

The result is a structured risk assessment.

Example:

```text
Risk Score:        87 / 100
Risk Level:        HIGH
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
• STEP-UP AUTHENTICATION
```

---

## 🧠 2. AI Investigation Copilot

RiskShield includes an optional AI Copilot powered by:

```text
HuggingFaceH4/zephyr-7b-beta
              │
              ▼
           Ollama
              │
              ▼
      RiskShield Copilot
```

The Copilot converts structured Risk Engine evidence into natural-language investigation assistance.

### Example questions

```text
Why is this transaction high risk?

What are the strongest risk indicators?

Which rules were triggered?

What should I investigate next?

Summarize this transaction.

Investigate this transaction.

What evidence supports this risk score?
```

---

## 🔎 3. Explainable Risk Analysis

RiskShield does not simply return:

```text
HIGH RISK
```

Instead, it provides the evidence behind the assessment.

```text
Transaction
     │
     ▼
Risk Score
     │
     ├── Fraud Probability
     ├── Risk Level
     ├── Risk Factors
     ├── Anomalies
     ├── Triggered Rules
     └── Recommended Action
```

This makes the system more useful for human analysts and investigation workflows.

---

## 📊 4. Risk Evidence Generation

Every analyzed transaction can produce structured evidence containing:

| Evidence             | Description                            |
| -------------------- | -------------------------------------- |
| Risk Score           | Overall transaction risk score         |
| Fraud Probability    | Estimated fraud likelihood             |
| Risk Level           | Low / Medium / High                    |
| Risk Factors         | Signals contributing to the assessment |
| Anomalies            | Detected behavioral abnormalities      |
| Triggered Rules      | Rules responsible for risk signals     |
| Transaction Features | Features used during analysis          |
| Recommended Action   | Suggested defensive response           |

---

## 📈 5. Fraud Detection Evaluation

RiskShield is designed around **measurable fraud detection performance**, rather than relying only on qualitative demonstrations.

The fraud detector should be evaluated using a **held-out test set** that is not used for model training or tuning.

### Evaluation Metrics

```text
                 HELD-OUT TEST SET
                         │
                         ▼
                 FRAUD DETECTOR
                         │
                         ▼
              ┌────────────────────┐
              │ Evaluation Metrics │
              └─────────┬──────────┘
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
   Precision          Recall             F1
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
                False Positive Rate
                        │
                        ▼
                 False Positive Cost
```

### Metrics

* **Precision** — proportion of flagged transactions that are actually fraudulent.
* **Recall** — proportion of fraudulent transactions successfully detected.
* **F1 Score** — balance between precision and recall.
* **False Positive Rate** — proportion of legitimate transactions incorrectly flagged.
* **False Positive Cost** — estimated business cost associated with legitimate transactions being incorrectly flagged.

### False Positive Cost

A configurable business-impact calculation can be represented as:

```text
False Positive Cost
=
False Positives
×
Estimated Cost per False Positive
```

This helps measure not only detection capability but also the operational impact of incorrectly flagging legitimate customers.

> **Important:** Evaluation numbers should represent actual experiments performed on the held-out dataset. RiskShield does not claim fabricated benchmark results.

---

## 🛡️ 6. Defense-First Architecture

RiskShield is designed as a **defensive financial-security system**.

Its purpose is to:

* Detect suspicious activity
* Identify fraud-risk signals
* Assist financial investigations
* Explain risk decisions
* Reduce financial losses
* Support analysts

The system does not provide offensive capabilities.

---

## 🤖 AI Safety Architecture

Zephyr 7B is deliberately separated from the authoritative risk decision.

```text
                         TRANSACTION
                              │
                              ▼
                       ┌─────────────┐
                       │ RISK ENGINE │
                       └──────┬──────┘
                              │
                              ▼
                    AUTHORITATIVE EVIDENCE
                              │
                              ▼
                       ┌─────────────┐
                       │  ZEPHYR 7B  │
                       └──────┬──────┘
                              │
                              ▼
                       INTERPRETATION
                              │
                              ▼
                           ANALYST
```

### Copilot restrictions

The Copilot:

* ❌ Cannot modify the risk score
* ❌ Cannot override the Risk Engine
* ❌ Cannot invent transaction information
* ❌ Cannot fabricate evidence
* ❌ Cannot arbitrarily execute SQL
* ❌ Cannot access application secrets
* ❌ Cannot independently approve or reject transactions

The Copilot:

* ✅ Receives structured evidence
* ✅ Explains observed signals
* ✅ Assists investigations
* ✅ Provides evidence-based recommendations
* ✅ States when information is unavailable
* ✅ Keeps the human analyst in the decision loop

---

## 🏗️ Complete System Architecture

```text
                           ┌─────────────────────┐
                           │       ANALYST       │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │ RISKSHIELD FRONTEND │
                           │                     │
                           │ Dashboard           │
                           │ Transactions        │
                           │ Risk Analysis       │
                           │ AI Copilot          │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │     BACKEND API     │
                           │                     │
                           │ Transaction API     │
                           │ Risk API            │
                           │ Copilot API         │
                           │ Authentication      │
                           └──────────┬──────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
        │ RISK ENGINE  │      │ DATA LAYER   │      │ AI COPILOT   │
        │              │      │              │      │              │
        │ ML Models    │      │ Transactions │      │ Context      │
        │ Rules        │      │ Datasets     │      │ Builder      │
        │ Features     │      │ History      │      │ Prompting    │
        │ Anomalies    │      │              │      │              │
        └──────┬───────┘      └──────────────┘      └──────┬───────┘
               │                                           │
               ▼                                           ▼
        ┌──────────────┐                             ┌──────────────┐
        │ Risk Score   │                             │    Ollama    │
        │ Risk Level   │                             └──────┬───────┘
        │ Fraud Prob.  │                                    │
        │ Risk Signals │                                    ▼
        └──────────────┘                             ┌──────────────┐
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
4. ML fraud-risk prediction
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
8. Risk evidence generation
              │
              ▼
9. Evidence displayed on dashboard
              │
              ▼
10. Analyst opens Copilot
              │
              ▼
11. Structured evidence supplied
              │
              ▼
12. Zephyr interprets evidence
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
                 FINANCIAL DATA
                       │
                       ▼
              Feature Engineering
                       │
                       ▼
             Fraud-Risk Detector
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
       ML Prediction         Rule Engine
            │                     │
            └──────────┬──────────┘
                       ▼
                 Anomaly Detection
                       │
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

The Risk Engine is the **authoritative fraud-risk detection component**.

### Responsibilities

* Transaction preprocessing
* Feature engineering
* Fraud-risk scoring
* Fraud probability estimation
* Rule evaluation
* Anomaly identification
* Behavioral analysis
* Risk classification
* Evidence generation

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

RiskShield can operate using banking and financial datasets for:

* Model development
* Testing
* Evaluation
* Demonstration
* Edge-case generation
* Experimentation

### Supported data sources

```text
Fraud Transaction Data
        │
Banking Transaction Data
        │
Financial Crime Data
        │
Synthetic Transactions
        │
Historical Risk Cases
        │
        ▼
    RiskShield
```

### Synthetic Data

Synthetic financial records can be used to reproduce transaction patterns without exposing actual customer information.

---

## 🛡️ Fraud & Risk Intelligence

RiskShield can combine multiple signals:

```text
Transaction Amount
        │
Transaction Frequency
        │
Location
        │
Device
        │
User Behaviour
        │
Historical Activity
        │
Transaction Timing
        │
Velocity
        │
Anomaly Score
        │
Rule Violations
        │
        ▼
COMPREHENSIVE RISK ASSESSMENT
```

---

## 💻 Technology Stack

## Frontend

```text
Next.js
React
JavaScript / TypeScript
Tailwind CSS
HTML5
CSS3
```

## Backend

```text
Python
FastAPI / Existing Python Backend Architecture
Uvicorn / Gunicorn
REST APIs
```

## Risk Intelligence

```text
Machine Learning
Feature Engineering
Rule-Based Detection
Anomaly Detection
Fraud-Risk Scoring
```

## AI Copilot

```text
HuggingFaceH4/zephyr-7b-beta
            ↓
         Ollama
            ↓
    RiskShield Copilot
```

## Infrastructure

```text
Docker
Docker Compose
Nginx
Ubuntu VPS
HTTPS
Git
```

---

# 🔌 API Architecture

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

> Exact endpoints should follow the project's current API conventions.

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
Evidence-Based Answer
   │
   ▼
Frontend
   │
   ▼
Analyst
```

---

## 🖥️ Local Application Architecture

RiskShield preserves the existing local application workflow.

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
               ┌──────┴──────┐
               ▼             ▼
           Frontend       Backend
                              │
                              ▼
                         Risk Engine
```

### Existing workflow

* Existing `.exe` launchers remain preserved.
* Existing startup scripts remain preserved.
* Existing risk engine remains preserved.
* Existing datasets remain preserved.
* Existing APIs remain preserved.
* Existing ports remain preserved.
* Existing application continues to work without the AI Copilot.

### Optional AI

The Zephyr/Ollama layer is an **optional capability**.

If Ollama is unavailable:

```text
Backend       → HEALTHY
Risk Engine   → HEALTHY
Ollama        → UNAVAILABLE
Copilot       → UNAVAILABLE
```

The core RiskShield platform continues functioning.

---

## 🐳 Docker Architecture

```text
                    Docker Compose
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          Frontend               Backend
                                    │
                                    ▼
                                  Ollama
                                    │
                                    ▼
                                Zephyr 7B
```

For production, Ollama can also run directly on the host while Frontend and Backend run inside Docker.

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
                 ┌──────────┴──────────┐
                 ▼                     ▼
             FRONTEND              BACKEND API
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

> Ollama's port `11434` should **never be exposed publicly**.

---

## 🚀 Deployment

## 1. Clone Repository

```bash
git clone <repository-url>
cd riskshield-ai
```

## 2. Configure Environment

Create:

```text
.env
```

based on:

```text
.env.example
```

## 3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 4. Download Zephyr

```bash
ollama pull zephyr:7b-beta
```

## 5. Build Containers

```bash
docker compose build
```

## 6. Start RiskShield

```bash
docker compose up -d
```

## 7. Verify

```bash
docker compose ps
```

Then verify:

```text
/api/health
/api/copilot/health
```

---

## 🔐 Security Architecture

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
              ┌────────┴────────┐
              ▼                 ▼
         Risk Engine         Copilot
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

# ⚙️ Configuration

| Variable          | Purpose                                                     |
| ----------------- | ----------------------------------------------------------- |
| `APP_ENV`         | Application environment                                     |
| `BACKEND_HOST`    | Backend bind address                                        |
| `BACKEND_PORT`    | Backend port                                                |
| `OLLAMA_BASE_URL` | Ollama server address                                       |
| `OLLAMA_MODEL`    | AI model                                                    |
| `CORS_ORIGINS`    | Allowed frontend origins                                    |
| `SECRET_KEY`      | Application security secret                                 |
| `DATABASE_URL`    | Database connection if supported by the existing deployment |

---

## 🔄 Four Supported Execution Modes

RiskShield supports four coexisting deployment modes.

## Mode 1 — Existing Local Application

```text
Existing EXE
     ↓
RiskShield
     ↓
Risk Engine
```

The existing application remains the primary local workflow.

---

## Mode 2 — Local AI Copilot

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

The Copilot runs locally and can operate without sending transaction context to an external LLM service.

---

## Mode 3 — Docker

```text
Docker Compose
      │
 ┌────┴────┐
 ▼         ▼
Frontend  Backend
             │
             ▼
           Ollama
             │
             ▼
          Zephyr 7B
```

---

## Mode 4 — Production VPS

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
* Available RAM
* GPU
* GPU VRAM
* Quantization
* Concurrent requests
* Context size
* Transaction workload

The Risk Engine and Copilot remain logically separated so slow LLM inference does not block core risk analysis.

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

Each component can be scaled or replaced independently.

Possible future scaling architecture:

```text
                 Load Balancer
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Backend   Backend   Backend
             │         │         │
             └─────────┼─────────┘
                       ▼
                 Risk Services
                       │
                       ▼
                AI Inference Layer
```

---

## 🧪 Testing Strategy

## Risk Engine

Test:

* Transaction processing
* Feature extraction
* Risk scoring
* Fraud probability
* Rule evaluation
* Anomaly detection

## Fraud Detector Evaluation

Test using a held-out dataset:

* Precision
* Recall
* F1
* False Positive Rate
* False Positive Cost

## Copilot

Test:

* Valid transaction questions
* Missing evidence
* Invalid transaction IDs
* Ollama unavailable
* Zephyr unavailable
* Timeout handling
* Large context handling
* Unsupported questions

## Security

Test:

* Secret isolation
* Input validation
* CORS
* Arbitrary SQL prevention
* Prompt injection resistance
* LLM tool restrictions

## Deployment

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

The core fraud-risk detection system continues functioning independently.

---

## 🛠️ Troubleshooting

### Check Ollama

```bash
ollama list
```

### Download Zephyr

```bash
ollama pull zephyr:7b-beta
```

### Check Docker

```bash
docker --version
docker compose version
```

### Check services

```bash
docker compose ps
```

### View logs

```bash
docker compose logs -f
```

---

## 🎯 Primary Use Case

## Financial Fraud Detection

RiskShield's primary objective is identifying **fraudulent and suspicious financial transactions**.

```text
Transaction
     ↓
Risk Detection
     ↓
Fraud Probability
     ↓
Risk Score
     ↓
Evidence
     ↓
Analyst Investigation
     ↓
Defensive Action
```

### Additional use cases

* Transaction Investigation
* Analyst Assistance
* Risk Explanation
* Case Summarization
* Suspicious Activity Investigation
* Risk Operations
* Financial Crime Analysis

---

## 🏆 Hackathon Track Alignment

RiskShield directly aligns with an **AI Risk Manager** objective focused on reducing merchant losses caused by fraudulent transactions.

| Track Requirement        | RiskShield                             |
| ------------------------ | -------------------------------------- |
| Working detector         | ✅ Fraud-Risk Detection Engine          |
| One class of loss        | ✅ Fraudulent / suspicious transactions |
| AI/ML component          | ✅ ML + anomaly detection + rules       |
| Measurable performance   | ✅ Precision / Recall / F1              |
| Held-out evaluation      | ✅ Required evaluation methodology      |
| False-positive impact    | ✅ False Positive Cost                  |
| Investigation assistance | ✅ Zephyr AI Copilot                    |
| Human verification       | ✅ Human-in-the-loop                    |
| Defense-focused          | ✅ Defensive fraud detection            |
| Production deployment    | ✅ Docker / VPS                         |
| Local execution          | ✅ Existing EXE workflow                |
| Optional AI layer        | ✅ Ollama + Zephyr                      |

### The core hackathon story

```text
                 FINANCIAL LOSS
                       │
                       ▼
                    FRAUD
                       │
                       ▼
              AI FRAUD DETECTOR
                       │
                       ▼
                RISK SCORE
                       │
                       ▼
              RISK + EVIDENCE
                       │
                       ▼
                AI COPILOT
                       │
                       ▼
                INVESTIGATION
                       │
                       ▼
                HUMAN ANALYST
                       │
                       ▼
              DEFENSIVE ACTION
```

---

## 🔮 Future Scope

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

## 🌟 Project Highlights

```text
┌──────────────────────────────────────────────┐
│                RISKSHIELD AI                  │
├──────────────────────────────────────────────┤
│                                              │
│  🔍 AI Fraud-Risk Detection                 │
│  📊 Measurable Fraud Evaluation             │
│  🧠 AI Investigation Copilot               │
│  🤖 Zephyr 7B + Ollama                     │
│  🔎 Explainable Risk Analysis              │
│  🛡️ Defense-First Architecture             │
│  👨‍💼 Human-in-the-Loop Investigation        │
│  💻 Local AI Capability                     │
│  🐳 Docker Ready                            │
│  ☁️ VPS Deployable                          │
│  🔐 Evidence-Grounded AI                   │
│  ⚡ Modular Architecture                    │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 📌 Project Status

| Component                | Status                                                  |
| ------------------------ | ------------------------------------------------------- |
| Core Risk Management     | 🟢 Active                                               |
| Fraud-Risk Detection     | 🟢 Active                                               |
| Risk Evidence Generation | 🟢 Active                                               |
| AI Copilot               | 🟢 Integrated                                           |
| Local Ollama / Zephyr    | 🟢 Supported                                            |
| Existing EXE Execution   | 🟢 Preserved                                            |
| Docker                   | 🟢 Deployment Ready                                     |
| VPS Deployment           | 🟢 Supported                                            |
| Evaluation Framework     | 🟡 Metrics to be populated with actual held-out results |

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
* Evaluation performed
* Deployment implications

---

## ⚠️ Disclaimer

RiskShield AI is an analytical and decision-support system.

Its risk assessments and AI-generated explanations should be reviewed by qualified analysts and should not be treated as an unconditional determination of fraud.

The AI Copilot provides assistance based on evidence supplied by the RiskShield system and should not replace appropriate financial, legal, compliance, or security procedures.

---

## 🧰 Technology Summary

| Layer           | Technology                               |
| --------------- | ---------------------------------------- |
| Frontend        | Next.js / React                          |
| Styling         | Tailwind CSS                             |
| Backend         | Python                                   |
| API             | REST                                     |
| Risk Engine     | ML + Rules + Anomaly Detection           |
| Fraud Detection | Machine Learning + Behavioral Signals    |
| AI Copilot      | Zephyr 7B                                |
| Model Serving   | Ollama                                   |
| Data            | Banking / Financial / Synthetic Datasets |
| Containers      | Docker                                   |
| Orchestration   | Docker Compose                           |
| Reverse Proxy   | Nginx                                    |
| Production OS   | Ubuntu                                   |
| Deployment      | VPS / Cloud                              |
| Protocol        | HTTP / HTTPS                             |
| Version Control | Git                                      |

---

## 🛡️ RiskShield AI

### **Detect. Explain. Investigate. Decide.**

```text
                  RAW TRANSACTION
                         │
                         ▼
                  FRAUD DETECTION
                         │
                         ▼
                    RISK SCORE
                         │
                         ▼
                   RISK EVIDENCE
                         │
                         ▼
                  AI EXPLANATION
                         │
                         ▼
                    INVESTIGATION
                         │
                         ▼
                  HUMAN DECISION
                         │
                         ▼
                  DEFENSIVE ACTION
```

> **RiskShield doesn't just identify that a transaction is risky — it provides measurable fraud detection, exposes the evidence behind the assessment, and gives analysts an AI-powered investigation layer to understand what to examine next.**
