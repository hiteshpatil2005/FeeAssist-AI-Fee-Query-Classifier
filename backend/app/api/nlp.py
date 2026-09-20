"""
FeeAssist AI — NLP API Endpoints

Provides REST endpoints for natural language intent classification.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import nlp_service

router = APIRouter()


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Student fee query in English, Hindi, or Marathi")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "How much fee do I have left?"
            }
        }
    }


class ClassifyResponse(BaseModel):
    intent: str = Field(..., description="Predicted fee intent")
    confidence: float = Field(..., description="Calibrated confidence score between 0.0 and 1.0")


@router.post("/classify", response_model=ClassifyResponse, summary="Classify fee query intent")
async def classify_query(request: ClassifyRequest):
    """
    Classify a student query into one of the 10 FeeAssist AI fee intents:
    - FEE_STRUCTURE
    - PENDING_FEE
    - PAYMENT_STATUS
    - PAYMENT_HISTORY
    - DUE_DATE
    - INSTALLMENT
    - SCHOLARSHIP
    - REFUND
    - RECEIPT
    - OTHER_FEE_QUERY
    """
    try:
        result = nlp_service.classify_intent(request.text)
        return ClassifyResponse(
            intent=result["intent"],
            confidence=result["confidence"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP classification failed: {str(e)}")
