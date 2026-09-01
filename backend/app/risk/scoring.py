"""Scoring utilities for risk calculations."""
import numpy as np
from typing import Dict, List, Optional, Any


def calculate_customer_risk_profile(transactions: List[Dict]) -> Dict[str, Any]:
    if not transactions:
        return {"transaction_count": 0, "average_amount": 0.0, "velocity": 0.0, "fraud_history": 0, "merchant_diversity": 0, "risk_trend": "UNKNOWN"}
    amounts = [t.get("amount", 0) for t in transactions]
    fraud_count = sum(1 for t in transactions if t.get("fraud_label", 0) == 1)
    merchants = set(t.get("merchant_id", "") for t in transactions)
    timestamps = [t.get("timestamp") for t in transactions if t.get("timestamp")]
    if len(timestamps) > 1:
        from datetime import datetime
        try:
            times = [datetime.fromisoformat(str(t).replace("Z", "+00:00")) for t in timestamps]
            time_span = max(times) - min(times)
            velocity = len(transactions) / max(time_span.total_seconds() / 86400, 1)
        except Exception:
            velocity = 0.0
    else:
        velocity = 0.0
    recent_fraud_rate = fraud_count / max(len(transactions), 1)
    if recent_fraud_rate > 0.1:
        trend = "INCREASING"
    elif recent_fraud_rate > 0:
        trend = "STABLE_ELEVATED"
    else:
        trend = "STABLE_LOW"
    return {
        "transaction_count": len(transactions),
        "average_amount": round(float(np.mean(amounts)), 2),
        "velocity": round(velocity, 2),
        "fraud_history": fraud_count,
        "merchant_diversity": len(merchants),
        "risk_trend": trend
    }


def calculate_merchant_risk_profile(transactions: List[Dict]) -> Dict[str, Any]:
    if not transactions:
        return {"transaction_volume": 0, "fraud_rate": 0.0, "average_amount": 0.0, "customer_diversity": 0, "risk_trend": "UNKNOWN"}
    amounts = [t.get("amount", 0) for t in transactions]
    fraud_count = sum(1 for t in transactions if t.get("fraud_label", 0) == 1)
    customers = set(t.get("customer_id", "") for t in transactions)
    fraud_rate = fraud_count / max(len(transactions), 1)
    if fraud_rate > 0.1:
        trend = "HIGH_RISK"
    elif fraud_rate > 0.05:
        trend = "ELEVATED"
    elif fraud_rate > 0:
        trend = "MODERATE"
    else:
        trend = "LOW_RISK"
    return {
        "transaction_volume": len(transactions),
        "fraud_rate": round(fraud_rate, 4),
        "average_amount": round(float(np.mean(amounts)), 2),
        "customer_diversity": len(customers),
        "risk_trend": trend
    }
