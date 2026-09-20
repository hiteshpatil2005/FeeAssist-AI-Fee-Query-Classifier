"""FeeAssist AI — User Schemas (safe, no password fields)"""

from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    preferred_language: str
    course: str | None
    year: int | None
    semester: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
