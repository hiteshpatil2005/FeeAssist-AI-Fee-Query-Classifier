"""
FeeAssist AI — Fees API Router

All endpoints require authentication.
Users can only access their own fee records (enforced by JWT, not by request param).

Endpoints:
  GET /api/fees         — All fee records for current user
  GET /api/fees/summary — Aggregated fee summary for current user
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.fee import StudentFee
from app.schemas.fee import FeeOut, FeeSummaryOut
from app.security.auth import get_current_user

router = APIRouter()


@router.get(
    "/summary",
    response_model=FeeSummaryOut,
    summary="Get fee summary for the current user",
)
def get_fee_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Returns aggregated fee data for the latest fee record.
    If no record exists, returns zeros.
    """
    # Get the most recent fee record for this user
    fee = (
        db.query(StudentFee)
        .filter(StudentFee.user_id == current_user.id)
        .order_by(StudentFee.created_at.desc())
        .first()
    )

    if fee is None:
        return FeeSummaryOut(
            total_fee=0,
            paid_amount=0,
            pending_amount=0,
            scholarship_amount=0,
            due_date=None,
            academic_year=None,
            semester=None,
        )

    return FeeSummaryOut(
        total_fee=float(fee.total_fee),
        paid_amount=float(fee.paid_amount),
        pending_amount=float(fee.pending_amount),
        scholarship_amount=float(fee.scholarship_amount),
        due_date=fee.due_date,
        academic_year=fee.academic_year,
        semester=fee.semester,
    )


@router.get(
    "",
    response_model=list[FeeOut],
    summary="Get all fee records for the current user",
)
def get_fees(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Returns all fee records belonging to the authenticated user only.
    user_id is taken from the JWT — NOT from the request.
    """
    fees = (
        db.query(StudentFee)
        .filter(StudentFee.user_id == current_user.id)
        .order_by(StudentFee.created_at.desc())
        .all()
    )
    return fees
