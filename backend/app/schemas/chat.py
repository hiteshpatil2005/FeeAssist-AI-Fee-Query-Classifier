"""FeeAssist AI — Chat Schemas"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's natural language query")
    session_id: Optional[str] = Field(default=None, description="Optional persistent session identifier")
    language: Optional[str] = Field(default="en", description="Interaction language (en, hi, mr)")


class MessageOut(BaseModel):
    id: int
    role: str
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    detected_language: str = "en"
    fallback_used: bool = False
    source: str = "ml"
    entities: Dict[str, Any]
    session_id: str
    needs_clarification: bool = False
    options: Optional[List[Dict[str, Any]]] = None
    fee_data: Optional[Dict[str, Any]] = None
