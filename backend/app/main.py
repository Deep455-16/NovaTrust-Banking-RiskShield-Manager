"""RiskShield AI Manager - Main FastAPI Application."""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.data.dataset_loader import dataset_loader
from app.data.dataset_registry import get_compatible_datasets, list_datasets, DATASETS
from app.data.schema_mapper import normalize_dataset, get_schema_info
from app.data.data_validator import DataValidator
from app.data.preprocessor import TransactionPreprocessor
from app.ml.models import ModelManager
from app.ml.anomaly import AnomalyDetector
from app.ml.shap_explainer import SHAPExplainer
from app.ml.graph_risk import TransactionGraph
from app.ml.drift import DriftMonitor
from app.ml.local_llm import HuggingFaceCopilotClient          # kept as fallback
from app.copilot import ZephyrCopilotClient, CopilotService
from app.risk.risk_engine import RiskEngine, RiskSignals
from app.risk.policy_engine import PolicyEngine
from app.risk.scoring import calculate_customer_risk_profile, calculate_merchant_risk_profile
from app.security.auth import (
    authenticate_user, create_access_token, decode_token,
    has_permission, check_role_access, Token, User, UserInDB
)
from app.core.investigation import InvestigationManager
from app.simulation.simulator import TransactionSimulator, SyntheticDataGenerator

app_state = {
    "models": ModelManager(),
    "preprocessor": TransactionPreprocessor(),
    "anomaly_detector": AnomalyDetector(),
    "risk_engine": RiskEngine(),
    "policy_engine": PolicyEngine(),
    "investigation_manager": InvestigationManager(),
    "simulator": TransactionSimulator(),
    "synthetic_generator": SyntheticDataGenerator(),
    "transaction_graph": TransactionGraph(),
    "drift_monitor": DriftMonitor(),
    "local_llm": ZephyrCopilotClient(),        # Zephyr-7B via Ollama (optional)
    "copilot_service": None,                    # initialised in lifespan below
    "shap_explainer": None,
    "feature_names": [],
    "training_fraud_rate": 0.0,
    "active_connections": set(),
    "simulation_task": None
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


class LoginRequest(BaseModel):
    username: str
    password: str


class SimulationControl(BaseModel):
    action: str
    dataset: Optional[str] = "banksim"
    speed: Optional[float] = 1.0
    scenario: Optional[str] = "NORMAL"


class InvestigationAction(BaseModel):
    case_id: str
    action: str
    notes: Optional[str] = ""


class PolicyUpdate(BaseModel):
    name: str
    condition: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None


class DatasetSelection(BaseModel):
    dataset: str


class CopilotChatRequest(BaseModel):
    prompt: str


class BankAccountLinkRequest(BaseModel):
    account_name: str
    account_number: str
    ifsc_code: str
    pnr_number: Optional[str] = None
    bank_name: str
    account_type: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    token_data = decode_token(token)
    if token_data is None or token_data.username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    from app.security.auth import get_user
    user = get_user(token_data.username)
    if user is None or user.disabled:
        raise HTTPException(status_code=401, detail="User not found or disabled")
    return User(username=user.username, role=user.role, disabled=user.disabled)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Zero blocking work at startup — server is ready in under 3 seconds.
    # Models train on-demand when user clicks Train in the UI.
    print("[RiskShield] Server ready.")
    app_state["copilot_service"] = CopilotService(app_state["local_llm"])
    yield
    print("[RiskShield] Shutting down...")
    if app_state["simulation_task"]:
        app_state["simulation_task"].cancel()


app = FastAPI(
    title="RiskShield AI Manager",
    description="AI-powered financial transaction risk management platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}


@app.get("/api/v1/datasets")
async def list_all_datasets(current_user: User = Depends(get_current_user)):
    return {"datasets": list_datasets()}


@app.get("/api/v1/datasets/{dataset_name}")
async def get_dataset(dataset_name: str, current_user: User = Depends(get_current_user)):
    info = dataset_loader.get_dataset_profile(dataset_name)
    if info is None:
        return {"error": "Dataset not available"}
    validation = dataset_loader.validate_dataset(dataset_name)
    fraud_dist = dataset_loader.get_fraud_distribution(dataset_name)
    return {"name": dataset_name, "info": info, "validation": validation, "fraud_distribution": fraud_dist}


@app.get("/api/v1/datasets/{dataset_name}/preview")
async def preview_dataset(dataset_name: str, rows: int = 100, current_user: User = Depends(get_current_user)):
    df = dataset_loader.load_dataset(dataset_name, normalize=False)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not available")
    return {"preview": df.head(rows).to_dict("records"), "total_rows": len(df)}


@app.get("/api/v1/datasets/{dataset_name}/profile")
async def profile_dataset(dataset_name: str, current_user: User = Depends(get_current_user)):
    profile = dataset_loader.get_dataset_profile(dataset_name)
    if profile is None:
        raise HTTPException(status_code=404, detail="Dataset not available")
    return profile


@app.post("/api/v1/models/train")
async def train_model(dataset_selection: DatasetSelection, model_name: str = Query("weighted_lightgbm"), current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role, "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    df = dataset_loader.load_dataset(dataset_selection.dataset, normalize=True)
    if df is None:
        return {"error": "Dataset not available"}
    processed_df, features = app_state["preprocessor"].prepare_features(df, fit=True)
    app_state["feature_names"] = features
    if "step" in processed_df.columns and processed_df["step"].max() > 600:
        train_df = processed_df[processed_df["step"] <= 600]
        test_df = processed_df[processed_df["step"] > 600]
    else:
        from sklearn.model_selection import train_test_split
        train_df, test_df = train_test_split(processed_df, test_size=0.2, stratify=processed_df["fraud_label"], random_state=42)
    X_train = app_state["preprocessor"].get_feature_matrix(train_df)
    y_train = train_df["fraud_label"].values
    X_test = app_state["preprocessor"].get_feature_matrix(test_df)
    y_test = test_df["fraud_label"].values
    result = app_state["models"].train_model(model_name, X_train, y_train)
    if "error" in result:
        return result
    metrics = app_state["models"].evaluate_model(model_name, X_test, y_test)
    app_state["anomaly_detector"].fit(X_train)
    app_state["drift_monitor"].fit(processed_df, features)
    app_state["training_fraud_rate"] = float(y_train.mean())
    if model_name in app_state["models"].models:
        model = app_state["models"].models[model_name].artifact.model
        app_state["shap_explainer"] = SHAPExplainer(model, features)
        app_state["shap_explainer"].fit(X_train)
    return {"status": "success", "model": model_name, "metrics": metrics}


@app.get("/api/v1/models/metrics")
async def get_model_metrics(current_user: User = Depends(get_current_user)):
    return app_state["models"].get_all_metrics()


@app.get("/api/v1/models/comparison")
async def compare_models(current_user: User = Depends(get_current_user)):
    metrics = app_state["models"].get_all_metrics()
    comparison = []
    for name, m in metrics.items():
        if isinstance(m, dict) and "roc_auc" in m:
            comparison.append({"model": name, "roc_auc": m.get("roc_auc", 0), "pr_auc": m.get("pr_auc", 0), "precision": m.get("precision", 0), "recall": m.get("recall", 0), "f1": m.get("f1", 0)})
    return {"comparison": comparison}


@app.post("/api/v1/risk/score")
async def score_transaction(transaction: Dict[str, Any], current_user: User = Depends(get_current_user)):
    try:
        # Extract raw risk signals BEFORE preprocessing (preprocessor strips custom fields)
        raw_velocity = float(transaction.get("transaction_velocity", 0) or 0)
        raw_amount_dev = float(transaction.get("amount_deviation", 0) or 0)
        raw_is_first_time = bool(transaction.get("is_first_time_pair", False))
        raw_patterns = list(transaction.get("suspicious_patterns", []) or [])

        # Inject safe defaults so preprocessor never crashes on missing timestamp / columns
        safe_txn = {
            "transaction_id": transaction.get("transaction_id", "manual-001"),
            "timestamp": transaction.get("timestamp", pd.Timestamp.now().isoformat()),
            "customer_id": str(transaction.get("customer_id", "C0000")),
            "merchant_id": str(transaction.get("merchant_id", "M0000")),
            "amount": float(transaction.get("amount", 0) or 0),
            "category": str(transaction.get("category", "UNKNOWN")),
            "step": int(transaction.get("step", 0) or 0),
            "fraud_label": int(transaction.get("fraud_label", 0) or 0),
            "location": str(transaction.get("location", "UNKNOWN")),
            "device": str(transaction.get("device", "UNKNOWN")),
            "customer_gender": str(transaction.get("customer_gender", "UNKNOWN")),
        }

        fraud_prob = 0.0
        anomaly_score = 0.0
        X = None
        try:
            df = pd.DataFrame([safe_txn])
            processed_df, _ = app_state["preprocessor"].prepare_features(df, fit=False)
            X = app_state["preprocessor"].get_feature_matrix(processed_df)
            if X is not None and len(X) > 0:
                if "weighted_lightgbm" in app_state["models"].models:
                    fraud_prob = float(app_state["models"].predict("weighted_lightgbm", X)[0])
                if app_state["anomaly_detector"].fitted:
                    anomaly_score = float(app_state["anomaly_detector"].predict(X)[0])
        except Exception as model_err:
            print(f"ML scoring skipped (model not ready): {model_err}")

        # Combine ML output with raw manual payload fields for the risk engine
        signals = RiskSignals(
            fraud_probability=fraud_prob,
            anomaly_score=anomaly_score,
            transaction_velocity=raw_velocity,
            amount_deviation=raw_amount_dev,
            is_first_time_pair=raw_is_first_time,
            suspicious_patterns=raw_patterns
        )
        risk_result = app_state["risk_engine"].calculate_risk_score(signals)
        policy_result = app_state["policy_engine"].evaluate(
            risk_result["risk_score"], risk_result["risk_level"], risk_result["risk_factors"]
        )
        shap_factors = []
        try:
            if app_state["shap_explainer"] is not None and X is not None and len(X) > 0:
                shap_factors = app_state["shap_explainer"].explain(X[0])
        except Exception:
            pass
        return {
            "transaction_id": transaction.get("transaction_id"),
            "fraud_probability": round(fraud_prob, 4),
            "anomaly_score": round(anomaly_score, 4),
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "risk_factors": risk_result["risk_factors"],
            "decision": policy_result["decision"],
            "policy_name": policy_result["policy_name"],
            "shap_explanation": shap_factors,
            "component_scores": risk_result["component_scores"]
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/v1/simulation/control")
async def control_simulation(control: SimulationControl, current_user: User = Depends(get_current_user)):
    simulator = app_state["simulator"]
    if control.action == "start":
        if simulator.running:
            return {"status": "already_running"}
        df = dataset_loader.load_dataset(control.dataset, normalize=True)
        if df is None:
            return {"error": f"Dataset {control.dataset} not available"}
        simulator.load_dataset(df)
        simulator.speed_multiplier = control.speed
        simulator.set_scenario(control.scenario)
        app_state["simulation_task"] = asyncio.create_task(simulator.start())
        return {"status": "started", "dataset": control.dataset, "scenario": control.scenario}
    elif control.action == "pause":
        simulator.pause()
        return {"status": "paused"}
    elif control.action == "resume":
        simulator.resume()
        return {"status": "resumed"}
    elif control.action == "stop":
        simulator.stop()
        if app_state["simulation_task"]:
            app_state["simulation_task"].cancel()
            app_state["simulation_task"] = None
        return {"status": "stopped"}
    return {"error": "Unknown action"}


@app.get("/api/v1/simulation/status")
async def get_simulation_status(current_user: User = Depends(get_current_user)):
    simulator = app_state["simulator"]
    return {"running": simulator.running, "paused": simulator.paused, "current_index": simulator.current_index, "total_rows": len(simulator.df) if simulator.df is not None else 0, "scenario": simulator.scenario, "dataset": simulator.dataset_name}


@app.websocket("/api/v1/transactions/stream")
async def transaction_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing token")
            return
        token_data = decode_token(token)
        if token_data is None:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=4001, reason="Auth error")
        return
    queue = asyncio.Queue()
    app_state["simulator"].add_listener(queue)
    app_state["active_connections"].add(websocket)
    try:
        while True:
            transaction = await asyncio.wait_for(queue.get(), timeout=5.0)
            try:
                df = pd.DataFrame([transaction])
                processed_df, _ = app_state["preprocessor"].prepare_features(df, fit=False)
                X = app_state["preprocessor"].get_feature_matrix(processed_df)
                if "weighted_lightgbm" in app_state["models"].models:
                    transaction["fraud_probability"] = round(float(app_state["models"].predict("weighted_lightgbm", X)[0]), 4)
                if app_state["anomaly_detector"].fitted:
                    transaction["anomaly_score"] = round(float(app_state["anomaly_detector"].predict(X)[0]), 4)
                signals = RiskSignals(fraud_probability=transaction.get("fraud_probability", 0), anomaly_score=transaction.get("anomaly_score", 0), is_first_time_pair=transaction.get("is_first_time_pair", False))
                risk = app_state["risk_engine"].calculate_risk_score(signals)
                transaction["risk_score"] = risk["risk_score"]
                transaction["risk_level"] = risk["risk_level"]
                policy = app_state["policy_engine"].evaluate(risk["risk_score"], risk["risk_level"])
                transaction["decision"] = policy["decision"]
            except Exception as e:
                transaction["error"] = str(e)
            await websocket.send_json(transaction)
    except asyncio.TimeoutError:
        await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        app_state["simulator"].remove_listener(queue)
        app_state["active_connections"].discard(websocket)


@app.get("/api/v1/investigations")
async def list_investigations(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    cases = app_state["investigation_manager"].list_cases(status)
    return {"cases": [{"id": c.id, "transaction_id": c.transaction_id, "status": c.status, "risk_score": c.risk_score, "risk_level": c.risk_level, "created_at": c.created_at, "assigned_to": c.assigned_to} for c in cases]}


@app.post("/api/v1/investigations")
async def create_investigation(transaction_id: str, risk_score: float, risk_level: str, current_user: User = Depends(get_current_user)):
    case = app_state["investigation_manager"].create_case(transaction_id, risk_score, risk_level, assigned_to=current_user.username)
    return {"case_id": case.id, "status": case.status}


@app.post("/api/v1/investigations/action")
async def investigation_action(action: InvestigationAction, current_user: User = Depends(get_current_user)):
    success = app_state["investigation_manager"].perform_action(action.case_id, action.action, current_user.username, action.notes)
    return {"success": success}


@app.get("/api/v1/investigations/stats")
async def investigation_stats(current_user: User = Depends(get_current_user)):
    return app_state["investigation_manager"].get_statistics()


@app.get("/api/v1/audit")
async def get_audit_log(limit: int = 100, current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role, "audit"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return {"audit_log": app_state["investigation_manager"].get_audit_log(limit)}


@app.get("/api/v1/policies")
async def get_policies(current_user: User = Depends(get_current_user)):
    return {"policies": app_state["policy_engine"].get_policies()}


@app.post("/api/v1/policies")
async def update_policy(policy: PolicyUpdate, current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role, "manage_policies"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    from app.risk.policy_engine import PolicyRule
    if policy.condition and policy.action:
        rule = PolicyRule(name=policy.name, condition=policy.condition, action=policy.action, priority=policy.priority or 50)
        app_state["policy_engine"].add_policy(rule)
    else:
        updates = {k: v for k, v in policy.dict().items() if v is not None and k != "name"}
        app_state["policy_engine"].update_policy(policy.name, **updates)
    return {"status": "success"}


@app.get("/api/v1/customers/{customer_id}/risk")
async def customer_risk(customer_id: str, current_user: User = Depends(get_current_user)):
    df = dataset_loader.load_dataset("banksim", normalize=True)
    if df is None:
        return {"error": "Dataset not available"}
    customer_txns = df[df["customer_id"] == customer_id].to_dict("records")
    profile = calculate_customer_risk_profile(customer_txns)
    graph_signals = app_state["transaction_graph"].get_customer_risk_signals(customer_id)
    profile.update(graph_signals)
    return profile


@app.get("/api/v1/merchants/{merchant_id}/risk")
async def merchant_risk(merchant_id: str, current_user: User = Depends(get_current_user)):
    df = dataset_loader.load_dataset("banksim", normalize=True)
    if df is None:
        return {"error": "Dataset not available"}
    merchant_txns = df[df["merchant_id"] == merchant_id].to_dict("records")
    profile = calculate_merchant_risk_profile(merchant_txns)
    graph_signals = app_state["transaction_graph"].get_merchant_risk_signals(merchant_id)
    profile.update(graph_signals)
    return profile


@app.get("/api/v1/graph/stats")
async def graph_stats(current_user: User = Depends(get_current_user)):
    raw = app_state["transaction_graph"].get_graph_stats()
    # Normalise field names so frontend and backend agree
    return {
        "nodes": raw.get("total_nodes", 0),
        "edges": raw.get("total_edges", 0),
        "node_count": raw.get("total_nodes", 0),
        "edge_count": raw.get("total_edges", 0),
        "customers": raw.get("customers", 0),
        "merchants": raw.get("merchants", 0),
        "density": raw.get("density", 0),
        "connected_components": 1 if raw.get("is_connected") else max(raw.get("total_nodes", 1) - raw.get("total_edges", 0), 1),
        "is_connected": raw.get("is_connected", False),
    }


@app.get("/api/v1/graph/clusters")
async def graph_clusters(current_user: User = Depends(get_current_user)):
    raw_clusters = app_state["transaction_graph"].find_suspicious_clusters()
    enriched = []
    for c in raw_clusters:
        avg_fraud = c.get("avg_fraud_rate", 0)
        risk_level = "CRITICAL" if avg_fraud > 0.5 else "HIGH" if avg_fraud > 0.25 else "MEDIUM"
        enriched.append({
            "size": c.get("size", 0),
            "node_count": c.get("size", 0),
            "merchants": c.get("merchants", []),
            "avg_fraud_rate": avg_fraud,
            "risk_level": risk_level,
            "reason": f"Avg fraud rate {avg_fraud:.1%} across {c.get('size', 0)} linked merchants",
            "pattern": "Shared customer fraud ring",
        })
    return {"clusters": enriched}


@app.get("/api/v1/drift/status")
async def drift_status(current_user: User = Depends(get_current_user)):
    df = dataset_loader.load_dataset("banksim", normalize=True)
    if df is None:
        return {"error": "Dataset not available"}
    processed_df, _ = app_state["preprocessor"].prepare_features(df, fit=False)
    reports = app_state["drift_monitor"].check_drift(processed_df, app_state["feature_names"])
    current_fraud_rate = float(df["fraud_label"].mean())
    fraud_drift = app_state["drift_monitor"].get_fraud_rate_drift(app_state["training_fraud_rate"], current_fraud_rate)
    return {
        "overall_status": app_state["drift_monitor"].get_overall_status(reports),
        "feature_reports": [{"feature": r.feature, "status": r.status, "p_value": r.p_value, "training_mean": r.training_mean, "streaming_mean": r.streaming_mean} for r in reports],
        "fraud_rate_drift": fraud_drift
    }


@app.post("/api/v1/copilot/explain")
async def copilot_explain(transaction: Dict[str, Any], current_user: User = Depends(get_current_user)):
    fraud_prob = transaction.get("fraud_probability", 0)
    anomaly_score = transaction.get("anomaly_score", 0)
    risk_score = transaction.get("risk_score", 0)
    risk_level = transaction.get("risk_level", "LOW")
    shap_factors = transaction.get("shap_explanation", [])
    explanation_parts = []
    if fraud_prob > 0.7:
        explanation_parts.append(f"The ML model indicates a very high fraud probability of {fraud_prob:.1%}. This is the primary risk driver.")
    elif fraud_prob > 0.3:
        explanation_parts.append(f"The ML model suggests elevated fraud risk at {fraud_prob:.1%}.")
    else:
        explanation_parts.append(f"The ML model shows low fraud probability at {fraud_prob:.1%}.")
    if anomaly_score > 0.7:
        explanation_parts.append(f"The anomaly detector flags this as highly unusual (score: {anomaly_score:.2f}).")
    elif anomaly_score > 0.3:
        explanation_parts.append(f"The anomaly detector notes some unusual patterns (score: {anomaly_score:.2f}).")
    if shap_factors:
        top_factors = [f"{f['feature']} ({f['shap_value']:+.3f})" for f in shap_factors[:3]]
        explanation_parts.append(f"Key contributing factors: {', '.join(top_factors)}.")
    investigation_summary = f"""
    Risk Assessment Summary:
    - Overall Risk Score: {risk_score}/100 ({risk_level})
    - Fraud Probability: {fraud_prob:.2%}
    - Anomaly Score: {anomaly_score:.4f}
    - Recommended Action: {transaction.get('decision', 'ALLOW')}
    """
    questions = []
    if transaction.get("is_first_time_pair"):
        questions.append("Is this first-time merchant interaction expected for this customer?")
    if fraud_prob > 0.5:
        questions.append("Has the customer reported any lost or stolen cards?")
    if anomaly_score > 0.5:
        questions.append("Does the transaction pattern match the customer's historical behavior?")
    if transaction.get("amount", 0) > 10000:
        questions.append("Is this large amount consistent with the customer's typical spending?")
    return {
        "explanation": " ".join(explanation_parts),
        "investigation_summary": investigation_summary,
        "analyst_questions": questions,
        "risk_summary": f"Risk Level: {risk_level} | Score: {risk_score}/100 | Decision: {transaction.get('decision', 'ALLOW')}",
        "disclaimer": "This explanation is generated from actual ML model outputs and risk signals. It does not override the deterministic policy engine."
    }


@app.get("/api/v1/copilot/status")
async def copilot_status(current_user: User = Depends(get_current_user)):
    """Backward-compat: existing UI uses this route."""
    return await app_state["local_llm"].status()


@app.post("/api/v1/copilot/chat")
async def copilot_chat(request: CopilotChatRequest, current_user: User = Depends(get_current_user)):
    """Backward-compat simple chat (prompt field). Kept for existing UI."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    return await app_state["local_llm"].generate(request.prompt.strip())


# ─── NEW ZEPHYR COPILOT ENDPOINTS ────────────────────────────────────────────

@app.get("/api/v1/copilot/health")
async def copilot_health(current_user: User = Depends(get_current_user)):
    """Detailed health — Ollama running? Model pulled? Includes setup hints."""
    return await app_state["local_llm"].health()


@app.post("/api/v1/copilot/message")
async def copilot_message(request: dict, current_user: User = Depends(get_current_user)):
    """Rich chat endpoint with conversation history and optional transaction context.
    Body: { message, transaction_id?, history?, history_window? }
    """
    svc: CopilotService = app_state["copilot_service"]
    message = request.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    transaction_id = request.get("transaction_id")
    history = request.get("history", [])
    history_window = int(request.get("history_window", 6))

    # Build evidence context from transaction data if an ID is supplied
    evidence = ""
    risk_score = None
    risk_level = None

    if transaction_id:
        df = dataset_loader.load_dataset("banksim", normalize=True)
        txn_data = None
        if df is not None and not df.empty:
            matches = df[df["transaction_id"].astype(str) == str(transaction_id)]
            if not matches.empty:
                txn_data = matches.iloc[0].to_dict()

        risk_result = None
        if txn_data:
            risk_score = txn_data.get("risk_score")
            risk_level = txn_data.get("risk_level")
            risk_result = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "fraud_probability": txn_data.get("fraud_probability"),
                "decision": txn_data.get("decision"),
            }
        evidence = svc.build_risk_context(transaction=txn_data, risk_result=risk_result)

    result = await svc.chat(
        user_message=message,
        evidence_context=evidence,
        history=history,
        history_window=history_window,
    )
    return {
        "success": result.get("available", False),
        "transaction_id": transaction_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "response": result.get("response"),
        "fallback": result.get("fallback"),
        "model": result.get("model"),
        "provider": result.get("provider"),
        "available": result.get("available", False),
    }


@app.post("/api/v1/copilot/investigate")
async def copilot_investigate(request: dict, current_user: User = Depends(get_current_user)):
    """Structured investigation summary for a transaction ID.
    Body: { transaction_id }
    """
    svc: CopilotService = app_state["copilot_service"]
    transaction_id = request.get("transaction_id", "").strip()
    if not transaction_id:
        raise HTTPException(status_code=400, detail="transaction_id is required")

    # Fetch transaction row from any available dataset
    txn_data = None
    for ds_name in ["banksim", "sfindset", "global_bank", "synthetic"]:
        df = dataset_loader.load_dataset(ds_name, normalize=True)
        if df is None or df.empty:
            continue
        if "transaction_id" not in df.columns:
            continue
        matches = df[df["transaction_id"].astype(str) == str(transaction_id)]
        if not matches.empty:
            txn_data = matches.iloc[0].to_dict()
            break

    # Fetch investigation case history if available
    case_history: list = []
    im: InvestigationManager = app_state["investigation_manager"]
    all_cases = im.list_cases()
    for case in all_cases:
        if case.transaction_id == transaction_id:
            case_history = case.actions or []
            break

    risk_result = None
    risk_score = None
    risk_level = None
    if txn_data:
        risk_score = txn_data.get("risk_score")
        risk_level = txn_data.get("risk_level")
        risk_result = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_probability": txn_data.get("fraud_probability"),
            "decision": txn_data.get("decision"),
        }

    result = await svc.investigate(
        transaction_id=transaction_id,
        transaction=txn_data,
        risk_result=risk_result,
        case_history=case_history if case_history else None,
    )
    return {
        "success": result.get("available", False),
        "transaction_id": transaction_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "response": result.get("response"),
        "fallback": result.get("fallback"),
        "model": result.get("model"),
        "provider": result.get("provider"),
        "available": result.get("available", False),
    }


@app.post("/api/v1/copilot/quick_action")
async def copilot_quick_action(request: dict, current_user: User = Depends(get_current_user)):
    """Pre-defined quick actions: explain_risk | investigate | risk_factors |
    triggered_rules | recommend | summarize
    Body: { action, transaction_id? }
    """
    from app.copilot.service import QUICK_ACTIONS

    svc: CopilotService = app_state["copilot_service"]
    action = request.get("action", "").strip()
    if action not in QUICK_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action. Valid: {list(QUICK_ACTIONS.keys())}",
        )

    transaction_id = request.get("transaction_id")
    evidence = ""
    if transaction_id:
        df = dataset_loader.load_dataset("banksim", normalize=True)
        txn_data = None
        if df is not None and not df.empty and "transaction_id" in df.columns:
            matches = df[df["transaction_id"].astype(str) == str(transaction_id)]
            if not matches.empty:
                txn_data = matches.iloc[0].to_dict()
        if txn_data:
            evidence = svc.build_risk_context(transaction=txn_data)

    result = await svc.quick_action(action_key=action, evidence_context=evidence)
    return {
        "success": result.get("available", False),
        "action": action,
        "transaction_id": transaction_id,
        "response": result.get("response"),
        "fallback": result.get("fallback"),
        "available": result.get("available", False),
    }


@app.post("/api/v1/bank-account/link")
async def link_bank_account(request: BankAccountLinkRequest, current_user: User = Depends(get_current_user)):
    # Simulated linking - always succeeds and returns mock account details
    return {
        "status": "linked",
        "account": {
            "account_name": request.account_name,
            "account_number_masked": "XXXX-XXXX-" + request.account_number[-4:] if len(request.account_number) >= 4 else "XXXX",
            "bank_name": request.bank_name,
            "status": "Active",
            "balance": round(np.random.uniform(1000, 50000), 2)
        }
    }


@app.get("/api/v1/bank-account/transactions")
async def bank_account_transactions(account_number: str, limit: int = 20, current_user: User = Depends(get_current_user)):
    # Simulate fetching transactions for the linked account from datasets
    df = dataset_loader.load_dataset("banksim", normalize=True)
    if df is None or df.empty:
        return {"transactions": []}
    
    # Just take a random sample to simulate account history
    sample = df.sample(min(limit, len(df)))
    transactions = sample.to_dict("records")
    return {"transactions": transactions}


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "models_loaded": list(app_state["models"].models.keys()),
        "datasets_available": dataset_loader.list_available_datasets(),
        "simulation_running": app_state["simulator"].running
    }


@app.get("/")
async def root():
    return {
        "name": "RiskShield AI Manager",
        "version": "1.0.0",
        "description": "AI-powered financial transaction risk management platform",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
