"""
FeeAssist AI — Conversation Service

Manages multi-turn conversation sessions, context resolution, and history persistence
in PostgreSQL for authenticated students.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.conversation import Conversation
from app.models.message import Message
from app.services.entity_service import extract_entities


class ConversationService:
    @staticmethod
    def get_or_create_conversation(
        db: Session,
        user_id: int,
        session_id: str,
        language: str = "en",
    ) -> Conversation:
        """Retrieve existing active conversation or initialize a new session."""
        conv = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id, Conversation.session_id == session_id)
            .first()
        )
        if not conv:
            conv = Conversation(
                user_id=user_id,
                session_id=session_id,
                language=language,
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
        return conv

    @staticmethod
    def save_message(
        db: Session,
        conversation_id: int,
        role: str,
        message: str,
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> Message:
        """Persist a user or assistant message to PostgreSQL."""
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            message=message,
            intent=intent,
            confidence=confidence,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_recent_messages(
        db: Session,
        conversation_id: int,
        limit: int = 10,
    ) -> List[Message]:
        """Fetch the most recent messages in chronological order."""
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at), desc(Message.id))
            .limit(limit)
            .all()
        )
        # Reverse to chronological order (oldest -> newest)
        return list(reversed(messages))

    @staticmethod
    def infer_context_entities(messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze recent conversation history to extract persistent contextual cues:
        - Recently referenced semester (e.g. "semester 2")
        - Recently referenced academic year (e.g. "2026-27")
        - Recently referenced fee type (e.g. "Hostel")
        - Last discussed intent
        """
        context: Dict[str, Any] = {
            "semester": None,
            "academic_year": None,
            "fee_type": None,
            "last_intent": None,
        }

        # Inspect messages in reverse (most recent first)
        for msg in reversed(messages):
            if msg.role == "user" and not context["last_intent"] and msg.intent:
                context["last_intent"] = msg.intent

            # Extract entities from previous turn if not yet found
            past_entities = extract_entities(msg.message)
            if context["semester"] is None and past_entities.get("semester") is not None:
                context["semester"] = past_entities["semester"]
            if context["academic_year"] is None and past_entities.get("academic_year") is not None:
                context["academic_year"] = past_entities["academic_year"]
            if context["fee_type"] is None and past_entities.get("fee_type") is not None:
                context["fee_type"] = past_entities["fee_type"]

            # Stop once we have semester and year
            if context["semester"] is not None and context["academic_year"] is not None:
                break

        return context
