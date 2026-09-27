"""
FeeAssist AI — Payments API Router

All endpoints require authentication.
Users can only access their own payment records.

Endpoints:
  GET  /api/payments — All payments for the current user
  POST /api/payments — Record a new payment transaction
"""

from typing import Annotated, List
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import PaymentOut, PaymentCreate
from app.security.auth import get_current_user

router = APIRouter()


@router.get(
    "",
    response_model=List[PaymentOut],
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


@router.post(
    "",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new payment transaction",
)
def create_payment(
    payload: PaymentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Records a payment transaction for the authenticated student.
    Enforces user isolation via JWT current_user.id.
    """
    payment = Payment(
        user_id=current_user.id,
        amount=Decimal(str(payload.amount)),
        payment_date=payload.payment_date or date.today(),
        fee_type=payload.fee_type,
        payment_method=payload.payment_method,
        transaction_id=payload.transaction_id,
        status=payload.status,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
