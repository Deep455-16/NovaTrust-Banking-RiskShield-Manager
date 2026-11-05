# 🏗️ RiskShield AI: System Architecture

> Technical deep-dive into how RiskShield detects fraud, grounds its AI Copilot in evidence, and deploys from a laptop to a production VPS.
> Back to [README](README.md).

---

## 📑 Contents

1. [Design Principles](#-design-principles)
2. [System Context](#-system-context)
3. [Component Overview](#-component-overview)
4. [Risk Engine](#-risk-engine)
5. [Transaction Flow](#-end-to-end-transaction-flow)
6. [AI Copilot](#-ai-copilot)
7. [AI Safety Boundaries](#-ai-safety-boundaries)
8. [Data Layer](#-data-layer)
9. [Deployment Topologies](#-deployment-topologies)
10. [Security Architecture](#-security-architecture)
11. [Health & Failure Modes](#-health--failure-modes)
12. [Performance & Scalability](#-performance--scalability)
13. [Evaluation Methodology](#-evaluation-methodology)
14. [Repository Layout](#-repository-layout)

---

## 🎯 Design Principles

| # | Principle | Consequence |
|---|---|---|
| 1 | **Detection and explanation are separate** | The Risk Engine is authoritative; the LLM only interprets its output |
| 2 | **Evidence-grounded AI** | The Copilot prompt contains structured evidence and nothing it could fabricate from |
| 3 | **Human-in-the-loop** | No automated approve/reject path through the LLM |
| 4 | **Optional intelligence layer** | Core platform works with Ollama off |
| 5 | **Local-first** | Existing `.exe` and scripts keep working; AI can run fully on-device |
| 6 | **Defensive purpose only** | Built for detection and investigation, not offensive capability |
| 7 | **Independently replaceable parts** | Frontend, API, engine, data, and inference scale or swap separately |

---

## 🌐 System Context

```mermaid
flowchart TB
    Analyst([👤 Fraud Analyst])

    subgraph RiskShield[RiskShield AI]
        FE[Frontend<br/>Next.js · React · Tailwind]
        API[Backend API<br/>Python · FastAPI]
        RE[Risk Engine]
        CP[AI Copilot Service]
        DL[(Data Layer)]
    end

    OLL[[Ollama<br/>Zephyr 7B]]

    Analyst --> FE
    FE --> API
    API --> RE
    API --> CP
    RE --> DL
    CP --> RE
    CP --> OLL
```

---

## 🧱 Component Overview

```mermaid
flowchart LR
    subgraph Frontend
        D[Dashboard]
        TX[Transactions]
        RA[Risk Analysis]
        CU[Copilot UI]
    end

    subgraph Backend
        TA[Transaction API]
        RAPI[Risk API]
        CAPI[Copilot API]
        AU[Auth]
    end

    subgraph Engine[Risk Engine]
        FE2[Feature Engineering]
        ML[ML Models]
        RU[Rule Engine]
        AN[Anomaly Detection]
        SC[Score Aggregator]
    end

    subgraph Copilot
        CB[Context Builder]
        PR[Prompt Templates]
        OC[Ollama Client]
    end

    D & TX & RA --> TA & RAPI
    CU --> CAPI
    TA --> FE2
    FE2 --> ML & RU & AN
    ML & RU & AN --> SC
    CAPI --> CB --> PR --> OC
```

| Layer | Responsibility |
|---|---|
| **Frontend** | Dashboard, transaction views, risk analysis, Copilot chat |
| **Backend API** | Transaction, Risk, and Copilot endpoints; authentication; request validation |
| **Risk Engine** | Authoritative scoring and evidence generation |
| **Data Layer** | Transactions, datasets, history, processed features, indexes |
| **Copilot** | Context building, prompting, Ollama communication, response shaping |

---

## 🧩 Risk Engine

The Risk Engine is the **only** component that produces risk decisions.

```mermaid
flowchart TD
    IN[Raw Transaction] --> PRE[Preprocessing]
    PRE --> FEAT[Feature Extraction]
    FEAT --> ML[ML Fraud Prediction]
    FEAT --> RULES[Rule Evaluation]
    FEAT --> ANOM[Anomaly Detection]
    ML --> AGG[Score Aggregation]
    RULES --> AGG
    ANOM --> AGG
    AGG --> OUT[Risk Evidence]
```

### Signals consumed

| Category | Examples |
|---|---|
| **Amount** | Amount outliers vs. history |
| **Behavior** | Frequency, velocity, user behavior patterns |
| **Context** | Device, location, geographic anomalies |
| **Temporal** | Transaction timing |
| **History** | Past activity and prior risk cases |
| **Rules** | Rule violations such as `RULE_HIGH_AMOUNT`, `RULE_NEW_DEVICE` |

### Output contract (evidence)

| Field | Description |
|---|---|
| `risk_score` | Overall score (0–100) |
| `fraud_probability` | Estimated fraud likelihood |
| `risk_level` | Low / Medium / High |
| `signals` | Risk factors with severity |
| `triggered_rules` | Rules that fired |
| `anomalies` | Detected behavioral abnormalities |
| `features` | Features used in the analysis |
| `recommended_action` | Suggested defensive response (e.g. step-up authentication) |

```json
{
  "transaction_id": "TX-102",
  "risk_score": 87,
  "risk_level": "HIGH",
  "fraud_probability": 0.87,
  "signals": [
    { "name": "unusual_amount", "severity": "high" },
    { "name": "new_device", "severity": "medium" }
  ],
  "triggered_rules": ["RULE_HIGH_AMOUNT", "RULE_NEW_DEVICE"]
}
```

---

## 🔄 End-to-End Transaction Flow

```mermaid
flowchart TD
    A[1 · Transaction enters RiskShield] --> B[2 · Preprocessing]
    B --> C[3 · Feature extraction]
    C --> D[4 · ML fraud-risk prediction]
    D --> E[5 · Rule evaluation]
    E --> F[6 · Anomaly detection]
    F --> G[7 · Risk score generation]
    G --> H[8 · Risk evidence generation]
    H --> I[9 · Evidence shown on dashboard]
    I --> J[10 · Analyst opens Copilot]
    J --> K[11 · Structured evidence supplied]
    K --> L[12 · Zephyr interprets evidence]
    L --> M[13 · Explanation / investigation / recommendation]
    M --> N[14 · Analyst makes final decision]
```

Steps 1–9 never depend on the LLM. Steps 10–13 are optional and additive.

---

## 🧠 AI Copilot

### Request flow

```mermaid
sequenceDiagram
    autonumber
    actor An as Analyst
    participant FE as Frontend
    participant API as Backend API
    participant CB as Context Builder
    participant OL as Ollama
    participant Z as Zephyr 7B

    An->>FE: "Why is TX-102 high risk?"
    FE->>API: POST /api/copilot/chat
    API->>CB: Resolve transaction + evidence
    CB-->>API: Structured context
    API->>OL: Evidence-grounded prompt
    OL->>Z: Generate
    Z-->>OL: Interpretation
    OL-->>API: Response
    API-->>FE: Evidence-based answer
    FE-->>An: Explanation + next steps
```

### Copilot module layout

| File | Role |
|---|---|
| `ollama_client.py` | HTTP client for Ollama, with timeouts and error handling |
| `service.py` | Orchestrates context building, prompting, response handling |
| `prompts.py` | System and task prompt templates |
| `schemas.py` | Request/response validation models |

### Supported interactions

`chat` (Q&A over a transaction) and `investigate` (guided analysis). Typical tasks include explaining risk, listing triggered rules, summarizing a transaction, and suggesting next investigative steps.

---

## 🛡️ AI Safety Boundaries

```mermaid
flowchart LR
    TX[Transaction] --> RE[Risk Engine]
    RE -->|authoritative evidence| Z[Zephyr 7B]
    Z -->|interpretation only| AN[Analyst]
    AN --> DEC{{Final Decision}}
    Z -.->|❌ cannot write back| RE
```

| Guardrail | Enforcement |
|---|---|
| Cannot modify risk score | Evidence is passed read-only; no write path from Copilot to engine |
| Cannot fabricate evidence | Prompt restricts answers to supplied fields; unavailable data must be stated as unavailable |
| Cannot execute arbitrary SQL | Copilot has no database tool; backend exposes only controlled lookups |
| Cannot access secrets | Secrets live in environment config and are never placed in prompts |
| Cannot approve/reject | No decision endpoint is reachable from the LLM path |
| Prompt-injection resistance | Transaction fields are treated as data, validated, and tested adversarially |

---

## 📚 Data Layer

```mermaid
flowchart LR
    S1[Fraud transaction data] --> RS
    S2[Banking transaction data] --> RS
    S3[Financial crime data] --> RS
    S4[Synthetic transactions] --> RS
    S5[Historical risk cases] --> RS
    RS[(RiskShield data layer)]
    RS --> M[Model development]
    RS --> T[Testing & evaluation]
    RS --> DM[Demonstration]
```

Synthetic records reproduce realistic transaction patterns without exposing real customer information. Data is organized under `data/datasets`, `data/processed`, and `data/indexes`.

---

## 🚢 Deployment Topologies

RiskShield supports four coexisting modes.

### Mode 1 · Existing local application

```mermaid
flowchart LR
    EXE[Existing EXE] --> DEP[Dependency verification] --> ENV[Environment setup] --> APP[App server]
    APP --> FE[Frontend :3000]
    APP --> BE[Backend] --> RE[Risk Engine]
```

Launchers, startup scripts, datasets, APIs, and ports are preserved. Works without the Copilot.

### Mode 2 · Local AI Copilot

```mermaid
flowchart LR
    RS[RiskShield] --> BE[Backend] --> OL[Ollama] --> Z[Zephyr 7B]
```

Inference runs on-device, so transaction context need not go to an external LLM service.

### Mode 3 · Docker Compose

```mermaid
flowchart TB
    DC[Docker Compose] --> FE[Frontend]
    DC --> BE[Backend]
    BE --> OL[Ollama] --> Z[Zephyr 7B]
```

### Mode 4 · Production VPS

```mermaid
flowchart TB
    NET((Internet)) --> NG[Nginx · HTTPS · Domain]
    NG --> FE[Frontend container]
    NG --> BE[Backend container]
    BE --> OL[Host Ollama<br/>localhost only]
    OL --> Z[Zephyr 7B]
```

```text
Ubuntu VPS
├── Nginx            (TLS termination, reverse proxy)
├── Docker
│   ├── RiskShield Frontend
│   └── RiskShield Backend
└── Ollama           (host-level, bound to localhost)
    └── Zephyr 7B
```

> 🔒 **Ollama port `11434` must never be exposed publicly.** Bind to localhost or a private network only.

### Deploy checklist

```bash
cp .env.example .env                          # configure secrets and URLs
curl -fsSL https://ollama.com/install.sh | sh # install Ollama
ollama pull zephyr:7b-beta                    # fetch the model
docker compose build
docker compose up -d
docker compose ps
# verify: /api/health and /api/copilot/health
```

---

## 🔐 Security Architecture

```mermaid
flowchart TB
    U[User] --> NG[HTTPS / Nginx]
    NG --> API[Backend API<br/>validation · CORS · auth]
    API --> RE[Risk Engine]
    API --> CP[Copilot]
    CP --> OL[Ollama · private]
```

| Control | Purpose |
|---|---|
| Environment-based secrets | No credentials in code or frontend |
| Nothing secret committed to Git | `.env` ignored; `.env.example` documents keys |
| HTTPS everywhere in production | Transport security |
| Restricted CORS | Only approved frontend origins |
| Request validation | Pydantic-style schemas on all inputs |
| Controlled backend tools | No arbitrary SQL from the LLM |
| Private Ollama endpoint | No public model access |
| Safe error handling | No internal details leaked to clients |
| Optional authentication integration | Plug into existing identity systems |

---

## 🩺 Health & Failure Modes

| Scenario | Backend | Risk Engine | Ollama | Copilot |
|---|---|---|---|---|
| All healthy | 🟢 | 🟢 | 🟢 | 🟢 Available |
| Ollama stopped or model missing | 🟢 | 🟢 | 🔴 | 🔴 Unavailable |
| Slow inference or timeout | 🟢 | 🟢 | 🟡 | 🟡 Degraded, with timeout handling |

**Isolation guarantee:** LLM latency or failure cannot block or alter core risk analysis. Probe with `GET /api/health` and `GET /api/copilot/health`.

---

## ⚡ Performance & Scalability

Zephyr 7B latency depends on CPU, RAM, GPU/VRAM, quantization, concurrency, and context size. Because the Risk Engine and Copilot are logically separate, slow inference never blocks scoring.

```mermaid
flowchart TB
    LB[Load balancer] --> B1[Backend] & B2[Backend] & B3[Backend]
    B1 & B2 & B3 --> RS[Risk services]
    B1 & B2 & B3 --> AI[AI inference layer]
```

Planned scaling: stateless backend replicas, a shared risk-services tier, and a dedicated (optionally GPU-backed, distributed) inference layer.

---

## 📈 Evaluation Methodology

```mermaid
flowchart LR
    DS[Dataset] --> SP{Split}
    SP -->|train / tune| TR[Model development]
    SP -->|held-out test| HT[Test set]
    TR --> DET[Fraud detector]
    HT --> DET
    DET --> MET[Precision · Recall · F1 · FPR]
    MET --> FPC[False Positive Cost]
```

- The test set is **never** used for training or tuning.
- `False Positive Cost = False Positives × Estimated Cost per False Positive`, with the unit cost configurable to the business.
- Only results from real experiments are reported. No benchmark numbers are asserted in the documentation until they exist.

---

## 📁 Repository Layout

```text
RiskShield/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── copilot/        # ollama_client · service · prompts · schemas
│   │   ├── risk_engine/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/ · components/ · services/ · public/
│   ├── package.json
│   └── Dockerfile
├── data/                   # datasets · processed · indexes
├── scripts/
├── nginx/
├── docker-compose.yml
├── .env.example
├── DEPLOYMENT.md
├── ARCHITECTURE.md
└── README.md
```

---

<div align="center">

**The Risk Engine detects. The AI Copilot explains. The analyst decides.**

</div>
