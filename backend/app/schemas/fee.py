"""FeeAssist AI — Fee Schemas"""

from datetime import datetime, date
from pydantic import BaseModel


class FeeOut(BaseModel):
    id: int
    academic_year: str
    semester: int
    total_fee: float
    paid_amount: float
    pending_amount: float
    scholarship_amount: float
    due_date: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeeSummaryOut(BaseModel):
    total_fee: float
    paid_amount: float
    pending_amount: float
    scholarship_amount: float
    due_date: date | None
    academic_year: str | None
    semester: int | None
