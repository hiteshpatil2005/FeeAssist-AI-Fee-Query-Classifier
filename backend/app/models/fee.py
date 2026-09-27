"""FeeAssist AI — StudentFee Model"""

from datetime import datetime, date
from sqlalchemy import Integer, Numeric, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StudentFee(Base):
    __tablename__ = "student_fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)   # e.g. "2026-27"
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    total_fee: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    pending_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    scholarship_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    course: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fee_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default="Tuition")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="fees")

    def __repr__(self) -> str:
        return f"<StudentFee id={self.id} user_id={self.user_id} semester={self.semester}>"
