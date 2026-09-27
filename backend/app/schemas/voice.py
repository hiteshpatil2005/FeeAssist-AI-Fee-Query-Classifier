"""
FeeAssist AI — Voice Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    language: Optional[str] = Field(default="en", description="Target language ('en', 'hi', 'mr')")


class SupportedLanguagesResponse(BaseModel):
    supported_languages: Dict[str, Dict[str, str]]
