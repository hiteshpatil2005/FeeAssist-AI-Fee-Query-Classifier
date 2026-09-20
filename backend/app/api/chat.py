"""
FeeAssist AI — Chat API Router (Placeholder)

This module will handle incoming chat messages, run them through
the NLP intent classification pipeline, query the fee database,
and return structured responses.

Gemini API will be used as a fallback for complex or low-confidence queries.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/message")
async def send_message():
    # TODO: Implement NLP pipeline → fee service → response generation
    return {"message": "Chat endpoint — not yet implemented"}


@router.get("/history")
async def get_history():
    # TODO: Return conversation history for the authenticated user
    return {"message": "History endpoint — not yet implemented"}
