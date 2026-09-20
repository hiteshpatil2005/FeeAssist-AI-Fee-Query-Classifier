"""
FeeAssist AI — Database Seed Script

Populates the database with demo users, fee records, and payment history.
Safe to run multiple times (idempotent).
"""

import sys
from datetime import date
from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.user import User
from app.models.fee import StudentFee
from app.models.payment import Payment
from app.security.auth import hash_password


def seed():
    db = SessionLocal()
    try:
        print("🌱 Seeding FeeAssist AI database...")

        demo_email = "demo@feeassist.ai"

        # Check if user already exists
        user = db.query(User).filter(User.email == demo_email).first()

        # If old demo user with .local exists, remove it
        old_user = db.query(User).filter(User.email == "demo@feeassist.local").first()
        if old_user:
            db.delete(old_user)
            db.commit()
            print("  🧹 Cleaned up legacy demo user")

        if not user:
            user = User(
                name="Aarav Sharma",
                email=demo_email,
                password_hash=hash_password("Password123!"),
                preferred_language="English",
                course="B.Tech Computer Science",
                year=3,
                semester=5,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"  ✅ Created demo user: {user.email} (Password: Password123!)")
        else:
            print(f"  ℹ️  Demo user already exists: {user.email}")

        # 2. Add Fees for Demo User
        existing_fees = db.query(StudentFee).filter(StudentFee.user_id == user.id).count()
        if existing_fees == 0:
            fee_sem4 = StudentFee(
                user_id=user.id,
                academic_year="2024-25",
                semester=4,
                total_fee=Decimal("70000.00"),
                paid_amount=Decimal("70000.00"),
                pending_amount=Decimal("0.00"),
                scholarship_amount=Decimal("15000.00"),
                due_date=date(2025, 4, 30),
            )
            fee_sem5 = StudentFee(
                user_id=user.id,
                academic_year="2025-26",
                semester=5,
                total_fee=Decimal("75000.00"),
                paid_amount=Decimal("50000.00"),
                pending_amount=Decimal("25000.00"),
                scholarship_amount=Decimal("10000.00"),
                due_date=date(2026, 11, 15),
            )
            db.add_all([fee_sem4, fee_sem5])
            print("  ✅ Added student fee records (Semester 4 & 5)")
        else:
            print("  ℹ️  Student fee records already exist")

        # 3. Add Payments for Demo User
        existing_payments = db.query(Payment).filter(Payment.user_id == user.id).count()
        if existing_payments == 0:
            payment1 = Payment(
                user_id=user.id,
                amount=Decimal("70000.00"),
                payment_date=date(2025, 1, 15),
                fee_type="Tuition & Exam Fee",
                payment_method="Net Banking",
                transaction_id="TXN984210482",
                status="completed",
            )
            payment2 = Payment(
                user_id=user.id,
                amount=Decimal("50000.00"),
                payment_date=date(2025, 8, 20),
                fee_type="Tuition Fee (Installment 1)",
                payment_method="UPI",
                transaction_id="TXN192847192",
                status="completed",
            )
            db.add_all([payment1, payment2])
            print("  ✅ Added payment history records")
        else:
            print("  ℹ️  Payment history records already exist")

        db.commit()
        print("✨ Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
