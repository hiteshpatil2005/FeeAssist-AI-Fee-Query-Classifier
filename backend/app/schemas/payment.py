"""FeeAssist AI — Payment Schemas"""

from datetime import datetime, date
from pydantic import BaseModel


class PaymentOut(BaseModel):
    id: int
    amount: float
    payment_date: date
    fee_type: str
    payment_method: str
    transaction_id: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
