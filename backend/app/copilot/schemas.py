"""Pydantic schemas for the Copilot API endpoints."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CopilotChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    transaction_id: Optional[str] = None
    history: List[CopilotChatMessage] = Field(default_factory=list)
    # Window: how many prior turns to include
    history_window: int = Field(default=6, ge=0, le=20)


class CopilotInvestigateRequest(BaseModel):
    transaction_id: str
    include_history: bool = True


class CopilotExplainRequest(BaseModel):
    transaction_id: Optional[str] = None
    risk_context: Optional[Dict[str, Any]] = None


class CopilotResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    response: Optional[str] = None
    fallback: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    available: bool = True


class CopilotHealthResponse(BaseModel):
    ollama: bool
    model: str
    model_ready: bool
    available: bool
    provider: str = "ollama"
    installed_models: List[str] = Field(default_factory=list)
    pull_hint: Optional[str] = None
    setup_hint: Optional[str] = None
    error: Optional[str] = None
