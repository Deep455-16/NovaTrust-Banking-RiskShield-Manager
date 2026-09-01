"""Copilot service layer.

Responsible for:
- Building structured risk context from RiskShield data
- Routing requests to the Zephyr/Ollama client
- Ensuring the LLM only sees curated evidence (hallucination control)
- Returning safe fallbacks when Ollama is unavailable
"""
import json
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from app.copilot.prompts import SYSTEM_PROMPT, INVESTIGATE_PROMPT, EXPLAIN_PROMPT

if TYPE_CHECKING:
    from app.copilot.ollama_client import ZephyrCopilotClient

logger = logging.getLogger(__name__)

# Quick-action button → prompt templates
QUICK_ACTIONS: Dict[str, str] = {
    "explain_risk":
        "Explain why this transaction received its current risk assessment. "
        "Use only the evidence provided above.",
    "investigate":
        "Produce a structured investigation summary for this transaction. "
        "List the key findings, triggered rules, and your recommended next step.",
    "risk_factors":
        "List and rank the most significant risk factors for this transaction "
        "in order of severity. Explain each briefly.",
    "triggered_rules":
        "Describe each triggered rule and explain why it fired for this transaction.",
    "recommend":
        "Based solely on the evidence provided, what is the single most important "
        "action the analyst should take next?",
    "summarize":
        "Produce a concise one-paragraph case summary suitable for a compliance log.",
}


class CopilotService:
    """Orchestrates context-building and LLM interaction for the Copilot."""

    def __init__(self, client: "ZephyrCopilotClient") -> None:
        self.client = client

    # ------------------------------------------------------------------ #
    # Context builders (only supply curated data to the LLM)
    # ------------------------------------------------------------------ #

    def build_risk_context(
        self,
        transaction: Optional[Dict[str, Any]] = None,
        risk_result: Optional[Dict[str, Any]] = None,
        signals: Optional[List[str]] = None,
        investigation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Produce a structured evidence block that goes into the LLM prompt.
        Nothing reaches the LLM that isn't explicitly included here.
        """
        parts: List[str] = []

        if transaction:
            # Strip any internal keys that could leak sensitive info
            safe_txn = {
                k: v for k, v in transaction.items()
                if k not in {"password", "token", "secret", "api_key"}
            }
            parts.append("=== Transaction ===")
            for k, v in safe_txn.items():
                parts.append(f"  {k}: {v}")

        if risk_result:
            parts.append("\n=== Risk Assessment ===")
            parts.append(f"  Risk Score:   {risk_result.get('risk_score', 'N/A')}/100")
            parts.append(f"  Risk Level:   {risk_result.get('risk_level', 'N/A')}")
            parts.append(f"  Fraud Prob:   {risk_result.get('fraud_probability', 'N/A')}")
            parts.append(f"  Decision:     {risk_result.get('decision', 'N/A')}")

            component = risk_result.get("component_scores")
            if component:
                parts.append("  Component Scores:")
                for k, v in component.items():
                    parts.append(f"    {k}: {v}")

            factors = risk_result.get("risk_factors", [])
            if factors:
                parts.append("  Risk Factors:")
                for f in factors:
                    parts.append(f"    - {f}")

        if signals:
            parts.append("\n=== Triggered Rules / Signals ===")
            for s in signals:
                parts.append(f"  - {s}")

        if investigation_history:
            parts.append(f"\n=== Investigation History ({len(investigation_history)} actions) ===")
            for action in investigation_history[-5:]:
                parts.append(
                    f"  [{action.get('timestamp', '?')}] "
                    f"{action.get('action', '?')} "
                    f"by {action.get('user', '?')}: "
                    f"{action.get('notes', '')}"
                )

        if not parts:
            return "No evidence available."

        return "\n".join(parts)

    # ------------------------------------------------------------------ #
    # Main service methods
    # ------------------------------------------------------------------ #

    async def chat(
        self,
        user_message: str,
        evidence_context: str = "",
        history: Optional[List[Dict[str, str]]] = None,
        history_window: int = 6,
    ) -> Dict[str, Any]:
        """Free-form analyst chat with optional evidence context and history."""
        system_content = SYSTEM_PROMPT
        if evidence_context and evidence_context != "No evidence available.":
            system_content += (
                "\n\nThe following RiskShield evidence is available for this session:\n"
                + evidence_context
            )

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]

        # Trim history to the configured window
        if history:
            trimmed = history[-(history_window * 2):]
            messages.extend(trimmed)

        messages.append({"role": "user", "content": user_message})

        return await self.client.chat(messages)

    async def investigate(
        self,
        transaction_id: str,
        transaction: Optional[Dict[str, Any]] = None,
        risk_result: Optional[Dict[str, Any]] = None,
        signals: Optional[List[str]] = None,
        case_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Structured investigation — produces a formal summary."""
        evidence = self.build_risk_context(
            transaction=transaction,
            risk_result=risk_result,
            signals=signals,
            investigation_history=case_history,
        )

        user_prompt = INVESTIGATE_PROMPT.format(
            transaction_id=transaction_id,
            risk_score=risk_result.get("risk_score", "N/A") if risk_result else "N/A",
            risk_level=risk_result.get("risk_level", "N/A") if risk_result else "N/A",
            evidence=evidence,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        return await self.client.chat(messages)

    async def explain(
        self,
        transaction: Optional[Dict[str, Any]] = None,
        risk_result: Optional[Dict[str, Any]] = None,
        signals: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """One-shot risk explanation."""
        evidence = self.build_risk_context(
            transaction=transaction,
            risk_result=risk_result,
            signals=signals,
        )
        user_prompt = EXPLAIN_PROMPT.format(evidence=evidence)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        return await self.client.chat(messages)

    async def quick_action(
        self,
        action_key: str,
        evidence_context: str = "",
    ) -> Dict[str, Any]:
        """Pre-defined quick-action buttons from the frontend."""
        user_prompt = QUICK_ACTIONS.get(action_key)
        if not user_prompt:
            return {
                "available": False,
                "response": None,
                "fallback": f"Unknown quick action: {action_key}",
            }

        system_content = SYSTEM_PROMPT
        if evidence_context:
            system_content += (
                "\n\nRiskShield evidence:\n" + evidence_context
            )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt},
        ]
        return await self.client.chat(messages)
