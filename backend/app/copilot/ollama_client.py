"""RiskShield Copilot — Ollama/Zephyr client with graceful degradation.

Uses the local Ollama REST API (http://localhost:11434) to serve
Zephyr-7B-beta. If Ollama is not running, ALL calls return a safe
fallback dict — the rest of RiskShield continues unaffected.
"""
import os
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ZephyrCopilotClient:
    """Wraps the local Ollama API for Zephyr-7B-beta inference.

    Completely optional — any connection/model error returns a
    structured fallback response so the wider application never crashes.
    """

    def __init__(self) -> None:
        self.base_url: str = os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")
        self.model: str = os.environ.get("OLLAMA_MODEL", "zephyr:7b-beta")
        self.timeout: float = float(os.environ.get("OLLAMA_TIMEOUT", "120"))
        self.temperature: float = float(
            os.environ.get("OLLAMA_TEMPERATURE", "0.2")
        )
        self.max_tokens: int = int(os.environ.get("OLLAMA_MAX_TOKENS", "1024"))

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #

    async def health(self) -> Dict[str, Any]:
        """Check whether Ollama is running AND Zephyr is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                r.raise_for_status()
                data = r.json()

            installed: List[str] = [
                m.get("name", "") for m in data.get("models", [])
            ]
            model_ready = any(
                self.model in name for name in installed
            )
            return {
                "ollama": True,
                "model": self.model,
                "model_ready": model_ready,
                "available": model_ready,
                "provider": "ollama",
                "installed_models": installed,
                "pull_hint": (
                    None
                    if model_ready
                    else f"Run: ollama pull {self.model}"
                ),
            }
        except Exception as exc:
            return {
                "ollama": False,
                "model": self.model,
                "model_ready": False,
                "available": False,
                "provider": "ollama",
                "installed_models": [],
                "error": str(exc),
                "setup_hint": (
                    "Ollama is not running or not installed. "
                    "Install from https://ollama.ai then run: "
                    f"ollama pull {self.model}"
                ),
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a chat message list to Ollama and return a clean result."""
        payload = {
            "model": self.model,
            "stream": False,
            "messages": messages,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.base_url}/api/chat", json=payload
                )
                r.raise_for_status()
                data = r.json()

            content: str = (
                data.get("message", {}).get("content", "").strip()
            )
            return {
                "available": True,
                "model": self.model,
                "provider": "ollama",
                "response": content,
            }
        except httpx.ConnectError:
            return self._unavailable(
                "Ollama is not running. Start it with: ollama serve"
            )
        except httpx.TimeoutException:
            return self._unavailable(
                f"Ollama request timed out after {self.timeout}s. "
                "The model may still be loading."
            )
        except Exception as exc:
            logger.warning("Copilot error: %s", exc)
            return self._unavailable(str(exc))

    # ------------------------------------------------------------------ #
    # Backward-compat aliases used by the existing /copilot/status &
    # /copilot/chat endpoints so they keep working unchanged.
    # ------------------------------------------------------------------ #

    async def status(self) -> Dict[str, Any]:
        return await self.health()

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Simple one-shot generation — used by the existing chat endpoint."""
        from app.copilot.prompts import SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return await self.chat(messages)

    # ------------------------------------------------------------------ #
    # Private
    # ------------------------------------------------------------------ #

    def _unavailable(self, reason: str) -> Dict[str, Any]:
        return {
            "available": False,
            "model": self.model,
            "provider": "ollama",
            "response": None,
            "fallback": (
                "RiskShield Copilot is currently unavailable because "
                f"the local AI service is not configured. {reason}"
            ),
            "error": reason,
        }
