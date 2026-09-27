"""
FeeAssist AI — Fee Schemas

Enforces strict separation of concerns:
- Student CANNOT manually specify `pending_amount`
- Backend calculates: `pending_amount = total_fee - paid_amount - scholarship_amount`
- Financial validation prevents negative values and invalid financial states
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FeeCreate(BaseModel):
    """Schema for creating a new fee record. Notice: pending_amount is not accepted."""
    academic_year: str = Field(..., example="2025-26", description="e.g. 2025-26, 2026-27")
    semester: int = Field(..., ge=1, le=12, example=5, description="Semester number (1-12)")
    course: Optional[str] = Field(None, example="B.Tech Computer Science")
    total_fee: float = Field(..., ge=0, example=75000.0, description="Total assessed fee")
    paid_amount: float = Field(default=0.0, ge=0, example=50000.0, description="Amount already paid")
    scholarship_amount: float = Field(default=0.0, ge=0, example=0.0, description="Scholarship deduction")
    due_date: Optional[date] = Field(None, example="2026-11-15")
    fee_type: Optional[str] = Field(default="Tuition", example="Tuition", description="e.g. Tuition, Hostel, Exam, All")
    notes: Optional[str] = Field(None, example="Semester 5 regular fee installment plan")

    @field_validator("academic_year")
    @classmethod
    def validate_year(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Academic year cannot be empty")
        return v


class FeeUpdate(BaseModel):
    """Schema for updating an existing fee record."""
    academic_year: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=12)
    course: Optional[str] = None
    total_fee: Optional[float] = Field(None, ge=0)
    paid_amount: Optional[float] = Field(None, ge=0)
    scholarship_amount: Optional[float] = Field(None, ge=0)
    due_date: Optional[date] = None
    fee_type: Optional[str] = None
    notes: Optional[str] = None


class FeeOut(BaseModel):
    """Schema for returning student fee records to clients."""
    id: int
    user_id: int
    academic_year: str
    semester: int
    course: Optional[str] = None
    total_fee: float
    paid_amount: float
    pending_amount: float
    scholarship_amount: float
    due_date: Optional[date] = None
    fee_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FeeSummaryOut(BaseModel):
    """Aggregated financial summary across all student records."""
    total_fee: float
    paid_amount: float
    pending_amount: float
    scholarship_amount: float
    due_date: Optional[date] = None
    academic_year: Optional[str] = None
    semester: Optional[int] = None
    record_count: int = 1
