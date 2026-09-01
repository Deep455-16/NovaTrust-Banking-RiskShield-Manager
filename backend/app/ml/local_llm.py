"""LLM integration for analyst copilot features using Hugging Face."""
import os
from typing import Any, Dict

import httpx


class HuggingFaceCopilotClient:
    def __init__(self) -> None:
        # We default to Zephyr or Mistral, both excellent 7B instructor models
        self.model = os.environ.get("RISKSHIELD_LLM_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.api_key = os.environ.get("HF_API_KEY", "")
        self.timeout = float(os.environ.get("RISKSHIELD_LLM_TIMEOUT", "45"))

    async def status(self) -> Dict[str, Any]:
        # Quick check if API is reachable
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(self.api_url, headers=headers)
                # It might return 401 if key is invalid, or 200 if model is loaded
                if response.status_code in [200, 401, 403]:
                    return {
                        "available": True,
                        "model": self.model,
                        "provider": "huggingface",
                        "installed_models": [self.model],
                    }
        except Exception as exc:
            pass
            
        return {
            "available": False,
            "model": self.model,
            "provider": "huggingface",
            "error": "Cannot reach Hugging Face API",
            "installed_models": [],
        }

    async def generate(self, prompt: str) -> Dict[str, Any]:
        system_prompt = (
            "You are RiskShield's fraud-risk copilot. Give concise, practical analyst guidance. "
            "Focus on fraud probability, anomaly behavior, attack possibility, bank-account safety, "
            "investigation questions, and clear next actions. Do not claim access to live bank accounts."
        )
        
        # Format prompt for instruct models
        formatted_prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
            if isinstance(data, list) and len(data) > 0:
                answer = data[0].get("generated_text", "").strip()
            else:
                answer = str(data)
                
            return {
                "available": True,
                "model": self.model,
                "provider": "huggingface",
                "response": answer,
            }
        except Exception as exc:
            err_msg = str(exc)
            if hasattr(exc, "response") and exc.response is not None:
                try:
                    err_msg = exc.response.json().get("error", err_msg)
                except:
                    pass
            return {
                "available": False,
                "model": self.model,
                "provider": "huggingface",
                "error": err_msg,
                "fallback": (
                    f"Hugging Face API error: {err_msg}. "
                    "If you are seeing rate limits or authorization errors, please set the HF_API_KEY environment variable with a free Hugging Face token."
                ),
            }
