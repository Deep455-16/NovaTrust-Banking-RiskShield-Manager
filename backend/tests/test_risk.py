import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.risk.risk_engine import RiskEngine, RiskSignals
from app.risk.policy_engine import PolicyEngine


def test_risk_scoring():
    engine = RiskEngine()
    signals = RiskSignals(
        fraud_probability=0.8,
        anomaly_score=0.7,
        transaction_velocity=50,
        amount_deviation=2000,
        is_first_time_pair=True
    )
    result = engine.calculate_risk_score(signals)
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert result["risk_score"] >= 60


def test_policy_engine():
    policy = PolicyEngine()
    result = policy.evaluate(85, "CRITICAL")
    assert result["decision"] == "BLOCK"
    result = policy.evaluate(45, "MEDIUM")
    assert result["decision"] == "ALLOW + MONITOR"
    result = policy.evaluate(15, "LOW")
    assert result["decision"] == "ALLOW"


def test_risk_components():
    engine = RiskEngine()
    signals = RiskSignals(fraud_probability=0.5, anomaly_score=0.3)
    result = engine.calculate_risk_score(signals)
    assert "component_scores" in result
    assert "fraud_probability" in result["component_scores"]
