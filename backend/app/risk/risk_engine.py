"""Risk Engine - Calculates risk scores from multiple signals."""
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class RiskSignals:
    fraud_probability: float = 0.0
    anomaly_score: float = 0.0
    transaction_velocity: float = 0.0
    amount_deviation: float = 0.0
    customer_behavior_score: float = 0.0
    merchant_behavior_score: float = 0.0
    is_first_time_pair: bool = False
    suspicious_patterns: List[str] = None

    def __post_init__(self):
        if self.suspicious_patterns is None:
            self.suspicious_patterns = []


class RiskEngine:
    RISK_LEVELS = {
        "LOW": (0, 29),
        "MEDIUM": (30, 59),
        "HIGH": (60, 79),
        "CRITICAL": (80, 100)
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "fraud_probability": 0.50,
            "anomaly_score": 0.20,
            "transaction_velocity": 0.08,
            "amount_deviation": 0.07,
            "customer_behavior": 0.05,
            "merchant_behavior": 0.05,
            "first_time_pair": 0.05
        }

    def calculate_risk_score(self, signals: RiskSignals) -> Dict[str, Any]:
        fraud_prob = min(max(signals.fraud_probability, 0), 1)
        anomaly = min(max(signals.anomaly_score, 0), 1)
        velocity = min(abs(signals.transaction_velocity) / 50, 1)
        amount_dev = min(abs(signals.amount_deviation) / 2000, 1)
        cust_behavior = min(max(signals.customer_behavior_score, 0), 1)
        merch_behavior = min(max(signals.merchant_behavior_score, 0), 1)
        first_time = 1.0 if signals.is_first_time_pair else 0.0

        score = (
            fraud_prob * self.weights["fraud_probability"] +
            anomaly * self.weights["anomaly_score"] +
            velocity * self.weights["transaction_velocity"] +
            amount_dev * self.weights["amount_deviation"] +
            cust_behavior * self.weights["customer_behavior"] +
            merch_behavior * self.weights["merchant_behavior"] +
            first_time * self.weights["first_time_pair"]
        ) * 100

        score = min(max(score, 0), 100)

        level = "LOW"
        for lvl, (low, high) in self.RISK_LEVELS.items():
            if low <= score <= high:
                level = lvl
                break

        triggered = []
        if fraud_prob > 0.5:
            triggered.append("High fraud probability")
        if anomaly > 0.7:
            triggered.append("Anomalous transaction")
        if velocity > 0.8:
            triggered.append("High velocity")
        if amount_dev > 0.8:
            triggered.append("Unusual amount")
        if first_time > 0.5:
            triggered.append("First-time merchant")
        triggered.extend(signals.suspicious_patterns)

        return {
            "risk_score": round(float(score), 2),
            "risk_level": level,
            "risk_factors": triggered,
            "component_scores": {
                "fraud_probability": round(fraud_prob * 100, 2),
                "anomaly_score": round(anomaly * 100, 2),
                "velocity_score": round(velocity * 100, 2),
                "amount_deviation_score": round(amount_dev * 100, 2),
                "first_time_pair_score": round(first_time * 100, 2)
            }
        }

    def get_risk_level(self, score: float) -> str:
        for lvl, (low, high) in self.RISK_LEVELS.items():
            if low <= score <= high:
                return lvl
        return "LOW"
