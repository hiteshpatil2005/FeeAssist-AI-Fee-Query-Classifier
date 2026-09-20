"""
FeeAssist AI — Payments API Router

All endpoints require authentication.
Users can only access their own payment records.

Endpoints:
  GET /api/payments — All payments for the current user
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import PaymentOut
from app.security.auth import get_current_user

router = APIRouter()


@router.get(
    "",
    response_model=list[PaymentOut],
    summary="Get all payments for the current user",
)
def get_payments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Returns all payment records belonging to the authenticated user only.
    user_id is read from the JWT — never from request parameters.
    """
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.payment_date.desc())
        .all()
    )
    return payments
