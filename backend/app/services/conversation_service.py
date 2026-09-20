"""
FeeAssist AI — Conversation Service (Placeholder)

This module will manage multi-turn conversation context per user session.

Planned features:
- Store conversation history in PostgreSQL or Redis
- Retrieve recent N turns for context injection
- Handle session expiry and context reset
"""


def get_conversation_context(user_id: int, session_id: str) -> list:
    """
    Retrieve recent conversation turns for a user session.
    TODO: Query conversation history from the database.
    """
    raise NotImplementedError("Conversation service not yet implemented")


def save_message(user_id: int, session_id: str, role: str, content: str):
    """
    Persist a message to conversation history.
    TODO: Save to PostgreSQL conversations table.
    """
    raise NotImplementedError("Conversation service not yet implemented")
