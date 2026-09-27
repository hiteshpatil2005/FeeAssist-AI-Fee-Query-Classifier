"""FeeAssist AI — Payment Schemas"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount must be greater than zero")
    payment_date: Optional[date] = Field(default=None, description="Date payment was made")
    fee_type: str = Field(default="Tuition", description="Fee category")
    payment_method: str = Field(default="UPI", description="Payment channel (UPI, Net Banking, Card, Cash)")
    transaction_id: Optional[str] = Field(default=None, description="External transaction reference ID")
    status: str = Field(default="completed", description="Payment status (completed, pending, failed)")
    notes: Optional[str] = Field(default=None, description="Payment remarks, installment reference, or confirmation notes")


class PaymentOut(BaseModel):
    id: int
    amount: float
    payment_date: date
    fee_type: str
    payment_method: str
    transaction_id: Optional[str]
    status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

