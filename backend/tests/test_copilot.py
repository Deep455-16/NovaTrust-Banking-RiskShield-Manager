"""Tests for the RiskShield AI Copilot integration.

These tests verify:
1. Ollama client returns safe fallbacks when Ollama is unavailable.
2. Service layer builds correct evidence context.
3. Quick-action routing works correctly.
4. Hallucination guard — service never invents data it was not given.

All tests run entirely offline (no Ollama required) by using the sync
path of the client through asyncio.
"""
import asyncio
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.copilot.ollama_client import ZephyrCopilotClient
from app.copilot.service import CopilotService, QUICK_ACTIONS
from app.copilot.prompts import SYSTEM_PROMPT, INVESTIGATE_PROMPT


# ─── Helpers ────────────────────────────────────────────────────────────────

def run(coro):
    """Run an async coroutine synchronously for testing."""
    return asyncio.run(coro)


# ─── ZephyrCopilotClient tests ───────────────────────────────────────────────

class TestZephyrCopilotClientOffline:
    """Verify graceful degradation when Ollama is NOT running."""

    def setup_method(self):
        # Point to a port that will never respond
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:19999"
        self.client = ZephyrCopilotClient()

    def teardown_method(self):
        os.environ.pop("OLLAMA_BASE_URL", None)

    def test_health_returns_safe_dict_when_offline(self):
        result = run(self.client.health())
        assert isinstance(result, dict)
        assert result["ollama"] is False
        assert result["available"] is False
        assert "error" in result or "setup_hint" in result

    def test_chat_returns_fallback_when_offline(self):
        result = run(self.client.chat([
            {"role": "user", "content": "Why is TX-001 risky?"}
        ]))
        assert isinstance(result, dict)
        assert result.get("available") is False
        assert "fallback" in result
        assert "response" not in result or result["response"] is None

    def test_generate_returns_fallback_when_offline(self):
        result = run(self.client.generate("Hello"))
        assert isinstance(result, dict)
        assert result.get("available") is False

    def test_status_returns_safe_dict(self):
        result = run(self.client.status())
        assert isinstance(result, dict)
        assert "model" in result

    def test_no_exception_raised_when_offline(self):
        """The wider application must NEVER crash due to a Copilot failure."""
        try:
            run(self.client.chat([{"role": "user", "content": "test"}]))
            run(self.client.health())
            run(self.client.generate("test"))
        except Exception as exc:
            pytest.fail(f"Client raised exception when it should have returned a fallback: {exc}")


# ─── CopilotService tests ────────────────────────────────────────────────────

class TestCopilotServiceContextBuilder:
    """Verify that the service only surfaces data it was explicitly given."""

    def setup_method(self):
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:19999"
        self.svc = CopilotService(ZephyrCopilotClient())

    def teardown_method(self):
        os.environ.pop("OLLAMA_BASE_URL", None)

    def test_empty_context_returns_no_evidence_available(self):
        ctx = self.svc.build_risk_context()
        assert ctx == "No evidence available."

    def test_transaction_appears_in_context(self):
        txn = {"transaction_id": "TX-001", "amount": 9500, "customer_id": "C123"}
        ctx = self.svc.build_risk_context(transaction=txn)
        assert "TX-001" in ctx
        assert "9500" in ctx
        assert "C123" in ctx

    def test_risk_result_appears_in_context(self):
        risk = {"risk_score": 87, "risk_level": "HIGH", "fraud_probability": 0.87}
        ctx = self.svc.build_risk_context(risk_result=risk)
        assert "87" in ctx
        assert "HIGH" in ctx
        assert "0.87" in ctx

    def test_credentials_stripped_from_context(self):
        """Hallucination guard: secrets must never reach the LLM."""
        txn = {
            "transaction_id": "TX-002",
            "password": "secret123",
            "api_key": "sk-abc",
            "token": "tok_xyz",
        }
        ctx = self.svc.build_risk_context(transaction=txn)
        assert "secret123" not in ctx
        assert "sk-abc" not in ctx
        assert "tok_xyz" not in ctx
        # Transaction ID should still appear
        assert "TX-002" in ctx

    def test_only_supplied_signals_appear(self):
        """Hallucination guard: only NEW_DEVICE was given — context must NOT
        mention location_anomaly or unusual_amount."""
        txn = {"transaction_id": "TX-003", "device": "NEW_DEVICE"}
        ctx = self.svc.build_risk_context(transaction=txn)
        assert "location_anomaly" not in ctx.lower()
        assert "unusual_amount" not in ctx.lower()
        # NEW_DEVICE should appear
        assert "NEW_DEVICE" in ctx

    def test_investigation_history_appears_in_context(self):
        history = [
            {"action": "ESCALATE", "user": "analyst1",
             "timestamp": "2026-09-01T10:00:00Z", "notes": "Possible OTP scam"},
        ]
        ctx = self.svc.build_risk_context(investigation_history=history)
        assert "ESCALATE" in ctx
        assert "OTP scam" in ctx


class TestCopilotServiceQuickActions:
    """Verify quick-action routing and graceful degradation."""

    def setup_method(self):
        os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:19999"
        self.svc = CopilotService(ZephyrCopilotClient())

    def teardown_method(self):
        os.environ.pop("OLLAMA_BASE_URL", None)

    def test_all_quick_actions_defined(self):
        expected = {"explain_risk", "investigate", "risk_factors",
                    "triggered_rules", "recommend", "summarize"}
        assert expected.issubset(set(QUICK_ACTIONS.keys()))

    def test_invalid_action_returns_safe_dict(self):
        result = run(self.svc.quick_action("nonexistent_action"))
        assert result.get("available") is False
        assert "Unknown quick action" in result.get("fallback", "")

    def test_valid_action_offline_returns_fallback(self):
        result = run(self.svc.quick_action("explain_risk"))
        assert isinstance(result, dict)
        # Offline → should have fallback, not crash
        assert "fallback" in result or "response" in result


# ─── Prompt integrity tests ──────────────────────────────────────────────────

class TestPrompts:
    def test_system_prompt_contains_key_rules(self):
        assert "NOT the authoritative fraud detection engine" in SYSTEM_PROMPT
        assert "NEVER invent" in SYSTEM_PROMPT
        assert "Never change or override" in SYSTEM_PROMPT

    def test_investigate_prompt_has_placeholders(self):
        filled = INVESTIGATE_PROMPT.format(
            transaction_id="TX-999",
            risk_score=75,
            risk_level="HIGH",
            evidence="some evidence",
        )
        assert "TX-999" in filled
        assert "75" in filled
        assert "some evidence" in filled
