"""FeeAssist AI — Models Package

Import all models here so Alembic and SQLAlchemy can discover them.
"""

from app.models.user import User
from app.models.fee import StudentFee
from app.models.payment import Payment
from app.models.conversation import Conversation
from app.models.message import Message

__all__ = ["User", "StudentFee", "Payment", "Conversation", "Message"]
