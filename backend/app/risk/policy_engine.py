"""Policy Engine - Makes final decisions based on risk scores."""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

POLICY_FILE = Path("data/runtime/policies.json")


class PolicyAction(Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"
    MONITOR = "MONITOR"


@dataclass
class PolicyRule:
    name: str
    condition: str
    action: str
    priority: int = 0
    enabled: bool = True


class PolicyEngine:
    DEFAULT_POLICIES = [
        PolicyRule("critical_block", "risk_level == 'CRITICAL'", "BLOCK", priority=100),
        PolicyRule("high_review", "risk_level == 'HIGH'", "REVIEW", priority=90),
        PolicyRule("medium_monitor", "risk_level == 'MEDIUM'", "ALLOW + MONITOR", priority=80),
        PolicyRule("low_allow", "risk_level == 'LOW'", "ALLOW", priority=70),
    ]

    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.load_policies()

    def load_policies(self):
        if POLICY_FILE.exists():
            try:
                with open(POLICY_FILE, "r") as f:
                    data = json.load(f)
                self.policies = [PolicyRule(**p) for p in data]
                return
            except Exception:
                pass
        self.policies = self.DEFAULT_POLICIES.copy()
        self.save_policies()

    def save_policies(self):
        POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(POLICY_FILE, "w") as f:
            json.dump([{"name": p.name, "condition": p.condition, "action": p.action, "priority": p.priority, "enabled": p.enabled} for p in self.policies], f, indent=2)

    def evaluate(self, risk_score: float, risk_level: str, triggered_rules: List[str] = None) -> Dict[str, Any]:
        triggered = triggered_rules or []
        sorted_policies = sorted([p for p in self.policies if p.enabled], key=lambda p: p.priority, reverse=True)
        for policy in sorted_policies:
            if self._evaluate_condition(policy.condition, risk_score, risk_level):
                return {"decision": policy.action, "policy_name": policy.name, "policy_condition": policy.condition, "risk_score": risk_score, "risk_level": risk_level, "triggered_rules": triggered}
        return {"decision": "ALLOW", "policy_name": "default", "policy_condition": "default", "risk_score": risk_score, "risk_level": risk_level, "triggered_rules": triggered}

    def _evaluate_condition(self, condition: str, risk_score: float, risk_level: str) -> bool:
        try:
            if "risk_level == 'CRITICAL'" in condition:
                return risk_level == "CRITICAL"
            elif "risk_level == 'HIGH'" in condition:
                return risk_level == "HIGH"
            elif "risk_level == 'MEDIUM'" in condition:
                return risk_level == "MEDIUM"
            elif "risk_level == 'LOW'" in condition:
                return risk_level == "LOW"
            elif "risk_score >=" in condition:
                threshold = float(condition.split(">=")[1].strip())
                return risk_score >= threshold
            return False
        except Exception:
            return False

    def add_policy(self, rule: PolicyRule):
        self.policies.append(rule)
        self.save_policies()

    def remove_policy(self, name: str):
        self.policies = [p for p in self.policies if p.name != name]
        self.save_policies()

    def update_policy(self, name: str, **kwargs):
        for policy in self.policies:
            if policy.name == name:
                for key, value in kwargs.items():
                    if hasattr(policy, key):
                        setattr(policy, key, value)
        self.save_policies()

    def get_policies(self) -> List[Dict]:
        return [{"name": p.name, "condition": p.condition, "action": p.action, "priority": p.priority, "enabled": p.enabled} for p in self.policies]
