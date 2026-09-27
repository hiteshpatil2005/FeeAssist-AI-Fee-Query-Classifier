"""
FeeAssist AI — Fees API Router

Full CRUD and summary operations for student fee management.
Strict Architecture Rules:
- All endpoints strictly require JWT authentication.
- All operations are isolated to `current_user.id` (users can never access/mutate others' records).
- `pending_amount` is calculated deterministically on the backend:
  Remaining Fee = Total Fee - Paid Amount - Scholarship Amount
- Student cannot manually enter or tamper with `pending_amount`.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.user import User
from app.models.fee import StudentFee
from app.schemas.fee import FeeCreate, FeeUpdate, FeeOut, FeeSummaryOut
from app.security.auth import get_current_user

router = APIRouter()


def calculate_pending_fee(total_fee: float, paid_amount: float, scholarship_amount: float) -> float:
    """Deterministic formula: Remaining Fee = Total Fee - Paid Amount - Scholarship Amount."""
    rem = round(float(total_fee) - float(paid_amount) - float(scholarship_amount), 2)
    return max(0.0, rem)


@router.get(
    "/summary",
    response_model=FeeSummaryOut,
    summary="Get aggregated fee summary for the current user",
)
def get_fee_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Returns aggregated fee totals across all active records belonging to current_user.
    Also finds the nearest upcoming due date.
    """
    fees = (
        db.query(StudentFee)
        .filter(StudentFee.user_id == current_user.id)
        .order_by(StudentFee.created_at.desc())
        .all()
    )

    if not fees:
        return FeeSummaryOut(
            total_fee=0.0,
            paid_amount=0.0,
            pending_amount=0.0,
            scholarship_amount=0.0,
            due_date=None,
            academic_year=None,
            semester=None,
            record_count=0,
        )

    total_fee = sum(float(f.total_fee) for f in fees)
    paid_amount = sum(float(f.paid_amount) for f in fees)
    scholarship_amount = sum(float(f.scholarship_amount) for f in fees)
    pending_amount = sum(float(f.pending_amount) for f in fees)

    # Find earliest upcoming due date among records with pending dues
    pending_fees = [f for f in fees if float(f.pending_amount) > 0 and f.due_date is not None]
    nearest_due_date = min((f.due_date for f in pending_fees), default=None) if pending_fees else (fees[0].due_date if fees else None)

    return FeeSummaryOut(
        total_fee=round(total_fee, 2),
        paid_amount=round(paid_amount, 2),
        pending_amount=round(pending_amount, 2),
        scholarship_amount=round(scholarship_amount, 2),
        due_date=nearest_due_date,
        academic_year=fees[0].academic_year,
        semester=fees[0].semester,
        record_count=len(fees),
    )


@router.get(
    "",
    response_model=List[FeeOut],
    summary="Get all fee records for the current user",
)
def get_fees(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Returns all fee records for the authenticated user only."""
    return (
        db.query(StudentFee)
        .filter(StudentFee.user_id == current_user.id)
        .order_by(StudentFee.academic_year.desc(), StudentFee.semester.desc())
        .all()
    )


@router.post(
    "",
    response_model=FeeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fee record for the current user",
)
def create_fee(
    fee_in: FeeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Creates a new fee record.
    Backend calculates: pending_amount = total_fee - paid_amount - scholarship_amount.
    Student CANNOT enter pending_amount manually.
    """
    pending = calculate_pending_fee(
        fee_in.total_fee, fee_in.paid_amount, fee_in.scholarship_amount
    )

    fee = StudentFee(
        user_id=current_user.id,
        academic_year=fee_in.academic_year,
        semester=fee_in.semester,
        course=fee_in.course or current_user.course,
        total_fee=fee_in.total_fee,
        paid_amount=fee_in.paid_amount,
        scholarship_amount=fee_in.scholarship_amount,
        pending_amount=pending,
        due_date=fee_in.due_date,
        fee_type=fee_in.fee_type or "Tuition",
        notes=fee_in.notes,
    )
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


@router.get(
    "/{fee_id}",
    response_model=FeeOut,
    summary="Get a specific fee record for the current user",
)
def get_fee(
    fee_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Returns fee record if it belongs to current_user; otherwise 404."""
    fee = (
        db.query(StudentFee)
        .filter(StudentFee.id == fee_id, StudentFee.user_id == current_user.id)
        .first()
    )
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found or access denied",
        )
    return fee


@router.put(
    "/{fee_id}",
    response_model=FeeOut,
    summary="Update a fee record for the current user",
)
def update_fee(
    fee_id: int,
    fee_in: FeeUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Updates a fee record and recalculates pending_amount."""
    fee = (
        db.query(StudentFee)
        .filter(StudentFee.id == fee_id, StudentFee.user_id == current_user.id)
        .first()
    )
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found or access denied",
        )

    update_data = fee_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(fee, field, value)

    # Recalculate pending_amount
    fee.pending_amount = calculate_pending_fee(
        fee.total_fee, fee.paid_amount, fee.scholarship_amount
    )

    db.commit()
    db.refresh(fee)
    return fee


@router.delete(
    "/{fee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a fee record for the current user",
)
def delete_fee(
    fee_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Deletes a fee record with strict user isolation check."""
    fee = (
        db.query(StudentFee)
        .filter(StudentFee.id == fee_id, StudentFee.user_id == current_user.id)
        .first()
    )
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found or access denied",
        )

    db.delete(fee)
    db.commit()
    return {"message": "Fee record deleted successfully", "id": fee_id}
