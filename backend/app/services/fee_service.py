"""
FeeAssist AI — Personalized Multilingual Fee Service

Handles all deterministic financial operations, database retrievals, and
rule-based financial calculations for authenticated students in English ('en'),
Hindi ('hi'), and Marathi ('mr').

Strict separation of concerns:
- NLP classifies the intent.
- Entity extraction provides parameters (amount, semester, year, etc.).
- FeeService queries PostgreSQL and performs all deterministic math:
    Remaining Fee = Total Fee - Paid Amount - Scholarship Amount
- ML NEVER generates or guesses numerical fee balances.
- Natural, localized responses are produced for English, Hindi, and Marathi.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import date, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.fee import StudentFee
from app.models.payment import Payment


# Localized month names for clear date representation
MONTH_NAMES = {
    "en": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "hi": ["", "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"],
    "mr": ["", "जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून", "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर"],
}


def format_localized_date(d: Optional[date], lang: str = "en") -> str:
    """Format date naturally in the target language."""
    if not d:
        return ""
    months = MONTH_NAMES.get(lang, MONTH_NAMES["en"])
    m_name = months[d.month]
    if lang == "hi":
        return f"{d.day} {m_name} {d.year}"
    elif lang == "mr":
        return f"{d.day} {m_name} {d.year}"
    return f"{m_name} {d.day}, {d.year}"


class FeeService:
    @staticmethod
    def get_student_fees(
        db: Session,
        user_id: int,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None,
        fee_type: Optional[str] = None,
    ) -> List[StudentFee]:
        """Fetch fee records for the student with optional filtering."""
        query = db.query(StudentFee).filter(StudentFee.user_id == user_id)
        if semester is not None:
            query = query.filter(StudentFee.semester == semester)
        if academic_year:
            query = query.filter(StudentFee.academic_year.ilike(f"%{academic_year}%"))
        if fee_type:
            query = query.filter(StudentFee.fee_type.ilike(f"%{fee_type}%"))

        return query.order_by(desc(StudentFee.academic_year), desc(StudentFee.semester)).all()

    @staticmethod
    def get_payments(db: Session, user_id: int, limit: int = 10) -> List[Payment]:
        """Fetch payment transaction history for the student."""
        return (
            db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(desc(Payment.payment_date), desc(Payment.id))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_student_payments(db: Session, user_id: int, limit: int = 10) -> List[Payment]:
        """Alias for get_payments."""
        return FeeService.get_payments(db, user_id, limit=limit)

    @staticmethod
    def resolve_target_fee(
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        context_fee_id: Optional[int] = None,
        lang: str = "en",
    ) -> Tuple[Optional[StudentFee], Optional[str], Optional[List[Dict[str, Any]]]]:
        """
        Determines the target StudentFee record based on query entities, session context, or defaults.
        Returns:
            (selected_fee, disambiguation_prompt, options_list)
        If ambiguous, returns (None, localized_disambiguation_prompt, options_list).
        If no records exist, returns (None, localized_no_records_prompt, None).
        """
        req_sem = entities.get("semester")
        req_year = entities.get("academic_year")
        req_type = entities.get("fee_type")

        # 1. If explicit semester or year provided in entities, query strictly
        if req_sem is not None or req_year or req_type:
            matching = FeeService.get_student_fees(
                db, user_id, semester=req_sem, academic_year=req_year, fee_type=req_type
            )
            if matching:
                return matching[0], None, None

            # If specified semester/year has no record:
            all_records = FeeService.get_student_fees(db, user_id)
            if not all_records:
                if lang == "mr":
                    msg = "तुमच्या खात्यासाठी कोणतीही फी नोंद आढळली नाही. कृपया 'My Fees' विभागात फी जोडा किंवा महाविद्यालय प्रशासनाशी संपर्क साधा."
                elif lang == "hi":
                    msg = "आपके खाते के लिए कोई फीस रिकॉर्ड नहीं मिला। कृपया 'My Fees' अनुभाग में अपना विवरण जोड़ें या कॉलेज प्रशासन से संपर्क करें।"
                else:
                    msg = "You do not have any fee records registered in the system yet. Please contact the college accounts desk or add a record in the My Fees tab."
                return None, msg, None

            if lang == "mr":
                avail = ", ".join([f"सत्र {f.semester} ({f.academic_year})" for f in all_records])
                msg = f"विचारलेल्या निकषांनुसार फी नोंद आढळली नाही. तुमच्या उपलब्ध नोंदी: {avail}."
            elif lang == "hi":
                avail = ", ".join([f"सेमेस्टर {f.semester} ({f.academic_year})" for f in all_records])
                msg = f"अनुरोधित मापदंडों के लिए कोई फीस रिकॉर्ड नहीं मिला। आपके उपलब्ध रिकॉर्ड हैं: {avail}।"
            else:
                avail = ", ".join([f"Semester {f.semester} ({f.academic_year})" for f in all_records])
                msg = f"No fee record was found for the requested criteria. Your available fee records are: {avail}."
            return None, msg, None

        # 2. If session context has an active fee record
        if context_fee_id:
            fee = db.query(StudentFee).filter(StudentFee.id == context_fee_id, StudentFee.user_id == user_id).first()
            if fee:
                return fee, None, None

        # 3. Retrieve all records for this student
        all_records = FeeService.get_student_fees(db, user_id)
        if not all_records:
            if lang == "mr":
                msg = "तुमच्या खात्यासाठी कोणतीही फी नोंद आढळली नाही. कृपया 'My Fees' विभागात फी तपशील जोडा किंवा प्रशासनाशी संपर्क साधा."
            elif lang == "hi":
                msg = "आपके खाते के लिए कोई फीस रिकॉर्ड नहीं मिला। कृपया 'My Fees' अनुभाग में अपना विवरण जोड़ें या कॉलेज प्रशासन से संपर्क करें।"
            else:
                msg = "No fee records found for your account. Please add your fee details in the My Fees section or contact the administration."
            return None, msg, None

        # If exactly one record exists, automatically use it
        if len(all_records) == 1:
            return all_records[0], None, None

        # If multiple records exist and user didn't specify which one, prompt for clarification!
        options = [
            {
                "id": f.id,
                "semester": f.semester,
                "academic_year": f.academic_year,
                "fee_type": f.fee_type or "Tuition",
                "pending_amount": float(f.pending_amount),
            }
            for f in all_records
        ]

        if lang == "mr":
            opts_text = " किंवा ".join([f"सत्र {f.semester} ({f.academic_year})" for f in all_records])
            prompt = f"तुमच्या खात्यावर एकापेक्षा जास्त फी नोंदी उपलब्ध आहेत. तुम्हाला कोणत्या सत्राची माहिती हवी आहे? ({opts_text})"
        elif lang == "hi":
            opts_text = " या ".join([f"सेमेस्टर {f.semester} ({f.academic_year})" for f in all_records])
            prompt = f"आपके पास कई फीस रिकॉर्ड उपलब्ध हैं। आप किस सेमेस्टर की जांच करना चाहते हैं? ({opts_text})"
        else:
            opts_text = " or ".join([f"Semester {f.semester} ({f.academic_year})" for f in all_records])
            prompt = f"You have multiple fee records on file. Which one would you like to check? ({opts_text})"

        return None, prompt, options

    # ─────────────────────────────────────────────────────────────────────────
    # Intent-Specific Handlers with Full Multilingual Templates
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def handle_pending_fee(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Calculates and explains the remaining fee balance in English, Hindi, or Marathi."""
        # Hypothetical Payment Simulation: "What if I pay ₹10,000?"
        if entities.get("is_hypothetical") and entities.get("amount") is not None:
            hypo_amount = float(entities["amount"])
            current_pending = float(fee.pending_amount)
            new_pending = max(0.0, round(current_pending - hypo_amount, 2))

            if lang == "mr":
                message = (
                    f"**सत्र {fee.semester} ({fee.academic_year})** साठी, तुमची चालू शिल्लक फी **₹{current_pending:,.2f}** आहे.\n\n"
                    f"• जर तुम्ही संभाव्य रक्कम भरली: **₹{hypo_amount:,.2f}**\n"
                    f"• तर तुमची नवीन शिल्लक फी असेल: **₹{new_pending:,.2f}**\n\n"
                    f"*(टीप: ही फक्त एक काल्पनिक गणना आहे. कोणताही प्रत्यक्ष व्यवहार झालेला नाही.)*"
                )
            elif lang == "hi":
                message = (
                    f"**सेमेस्टर {fee.semester} ({fee.academic_year})** के लिए, आपकी वर्तमान शेष फीस **₹{current_pending:,.2f}** है।\n\n"
                    f"• यदि आप संभावित भुगतान करते हैं: **₹{hypo_amount:,.2f}**\n"
                    f"• तो आपकी नई शेष फीस होगी: **₹{new_pending:,.2f}**\n\n"
                    f"*(सूचना: यह केवल एक सांकेतिक गणना है। कोई वास्तविक भुगतान दर्ज नहीं हुआ है।)*"
                )
            else:
                message = (
                    f"For **Semester {fee.semester} ({fee.academic_year})**, your current remaining fee is **₹{current_pending:,.2f}**.\n\n"
                    f"• If you make a hypothetical payment of: **₹{hypo_amount:,.2f}**\n"
                    f"• Your new remaining balance would be: **₹{new_pending:,.2f}**\n\n"
                    f"*(Note: This is a simulated calculation. No payment has been processed.)*"
                )

            return {
                "message": message,
                "fee_id": fee.id,
                "semester": fee.semester,
                "academic_year": fee.academic_year,
                "current_pending": current_pending,
                "hypothetical_payment": hypo_amount,
                "projected_remaining": new_pending,
                "is_simulation": True,
            }

        # Deterministic math directly from database
        pending = float(fee.pending_amount)
        total = float(fee.total_fee)
        paid = float(fee.paid_amount)
        scholarship = float(fee.scholarship_amount)
        due_str = format_localized_date(fee.due_date, lang)

        if lang == "mr":
            if pending <= 0:
                status_desc = "तुमची सर्व फी **पूर्णपणे भरलेली** आहे! कोणतीही शिल्लक बाकी नाही."
            else:
                due_info = f" (अंतिम देय दिनांक: **{due_str}**)" if fee.due_date else ""
                status_desc = f"तुमची शिल्लक फी **₹{pending:,.2f}** आहे{due_info}."

            breakdown = (
                f"{status_desc}\n\n"
                f"**फी तपशील (सत्र {fee.semester}, शैक्षणिक वर्ष {fee.academic_year})**:\n"
                f"• एकूण लागू फी: ₹{total:,.2f}\n"
                f"• भरलेली रक्कम: ₹{paid:,.2f}\n"
                f"• शिष्यवृत्ती / सूट: ₹{scholarship:,.2f}\n"
                f"• **एकूण शिल्लक फी: ₹{pending:,.2f}**"
            )
        elif lang == "hi":
            if pending <= 0:
                status_desc = "आपकी फीस **पूर्णतः चुकता** है! आपका कोई बकाया नहीं है।"
            else:
                due_info = f" (अंतिम तिथि: **{due_str}**)" if fee.due_date else ""
                status_desc = f"आपकी बकाया फीस **₹{pending:,.2f}** है{due_info}।"

            breakdown = (
                f"{status_desc}\n\n"
                f"**फीस विवरण (सेमेस्टर {fee.semester}, शैक्षणिक वर्ष {fee.academic_year})**:\n"
                f"• कुल लागू फीस: ₹{total:,.2f}\n"
                f"• जमा की गई राशि: ₹{paid:,.2f}\n"
                f"• छात्रवृत्ति / छूट: ₹{scholarship:,.2f}\n"
                f"• **कुल बकाया राशि: ₹{pending:,.2f}**"
            )
        else:
            if pending <= 0:
                status_desc = "Your fees are **fully settled**! You have no outstanding balance."
            else:
                due_info = f" due by **{due_str}**" if fee.due_date else ""
                status_desc = f"Your outstanding fee balance is **₹{pending:,.2f}**{due_info}."

            breakdown = (
                f"{status_desc}\n\n"
                f"**Fee Breakdown (Semester {fee.semester}, AY {fee.academic_year})**:\n"
                f"• Total Applicable Fee: ₹{total:,.2f}\n"
                f"• Paid Amount: ₹{paid:,.2f}\n"
                f"• Scholarship / Concession: ₹{scholarship:,.2f}\n"
                f"• **Remaining Balance: ₹{pending:,.2f}**"
            )

        return {
            "message": breakdown,
            "fee_id": fee.id,
            "semester": fee.semester,
            "academic_year": fee.academic_year,
            "total_fee": total,
            "paid_amount": paid,
            "scholarship_amount": scholarship,
            "pending_amount": pending,
            "due_date": fee.due_date.isoformat() if fee.due_date else None,
        }

    @classmethod
    def handle_fee_structure(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Provides the full fee structure in the requested language."""
        total = float(fee.total_fee)
        paid = float(fee.paid_amount)
        scholarship = float(fee.scholarship_amount)
        pending = float(fee.pending_amount)

        if lang == "mr":
            course_str = f" (**{fee.course}**)" if fee.course else ""
            fee_type_str = f" [{fee.fee_type}]" if fee.fee_type else ""
            message = (
                f"**सत्र {fee.semester} ({fee.academic_year})**{course_str}{fee_type_str} ची अधिकृत फी रचना:\n\n"
                f"• **एकूण फी**: ₹{total:,.2f}\n"
                f"• **शिष्यवृत्ती / सूट**: ₹{scholarship:,.2f}\n"
                f"• **निव्वळ देय फी**: ₹{(total - scholarship):,.2f}\n"
                f"• **भरलेली रक्कम**: ₹{paid:,.2f}\n"
                f"• **बाकी शिल्लक**: ₹{pending:,.2f}"
            )
            if fee.notes:
                message += f"\n*टीप: {fee.notes}*"
        elif lang == "hi":
            course_str = f" (**{fee.course}**)" if fee.course else ""
            fee_type_str = f" [{fee.fee_type}]" if fee.fee_type else ""
            message = (
                f"**सेमेस्टर {fee.semester} ({fee.academic_year})**{course_str}{fee_type_str} का आधिकारिक फीस ढांचा:\n\n"
                f"• **कुल फीस**: ₹{total:,.2f}\n"
                f"• **छात्रवृत्ति / छूट**: ₹{scholarship:,.2f}\n"
                f"• **शुद्ध देय राशि**: ₹{(total - scholarship):,.2f}\n"
                f"• **जमा की गई राशि**: ₹{paid:,.2f}\n"
                f"• **बकाया राशि**: ₹{pending:,.2f}"
            )
            if fee.notes:
                message += f"\n*टिप्पणी: {fee.notes}*"
        else:
            course_str = f" for **{fee.course}**" if fee.course else ""
            fee_type_str = f" ({fee.fee_type})" if fee.fee_type else ""
            message = (
                f"Here is your official fee structure{course_str} for **Semester {fee.semester} ({fee.academic_year})**{fee_type_str}:\n\n"
                f"• **Total Fee**: ₹{total:,.2f}\n"
                f"• **Scholarship / Waiver**: ₹{scholarship:,.2f}\n"
                f"• **Net Payable**: ₹{(total - scholarship):,.2f}\n"
                f"• **Amount Paid**: ₹{paid:,.2f}\n"
                f"• **Outstanding Balance**: ₹{pending:,.2f}\n"
            )
            if fee.notes:
                message += f"\n*Notes: {fee.notes}*"

        return {
            "message": message,
            "fee_id": fee.id,
            "semester": fee.semester,
            "academic_year": fee.academic_year,
            "total_fee": total,
            "course": fee.course,
            "fee_type": fee.fee_type,
            "pending_amount": pending,
        }

    @classmethod
    def handle_payment_status(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Returns the clear status of payments (Paid / Partial / Unpaid) in target language."""
        pending = float(fee.pending_amount)
        paid = float(fee.paid_amount)
        total = float(fee.total_fee)

        if pending <= 0:
            status = "PAID"
            if lang == "mr":
                summary = "तुमची फी **पूर्णपणे भरलेली (Paid)** आहे."
            elif lang == "hi":
                summary = "आपकी फीस **पूर्णतः जमा (Paid in Full)** है।"
            else:
                summary = "Your fee payment is **COMPLETE** (Paid in Full)."
        elif paid > 0:
            status = "PARTIALLY_PAID"
            if lang == "mr":
                summary = f"तुमची फी **अंशतः भरलेली (Partially Paid)** आहे. तुम्ही ₹{paid:,.2f} भरले असून, ₹{pending:,.2f} शिल्लक आहे."
            elif lang == "hi":
                summary = f"आपकी फीस का दर्जा **आंशिक भुगतान (Partially Paid)** है। आपने ₹{paid:,.2f} जमा किए हैं, और ₹{pending:,.2f} बकाया है।"
            else:
                summary = f"Your fee status is **PARTIALLY PAID**. You have paid ₹{paid:,.2f}, leaving ₹{pending:,.2f} pending."
        else:
            status = "UNPAID"
            if lang == "mr":
                summary = f"तुमची फी **थकीत (Unpaid)** आहे. एकूण ₹{total:,.2f} रक्कम अद्याप शिल्लक आहे."
            elif lang == "hi":
                summary = f"आपकी फीस का दर्जा **अदत्त (Unpaid)** है। कुल ₹{total:,.2f} की राशि अभी बकाया है।"
            else:
                summary = f"Your fee status is **UNPAID**. Total amount of ₹{total:,.2f} is currently pending."

        if lang == "mr":
            message = (
                f"**सत्र {fee.semester} ({fee.academic_year}) साठी फी स्थिती**:\n\n"
                f"{summary}\n\n"
                f"• एकूण फी: ₹{total:,.2f}\n"
                f"• भरलेली रक्कम: ₹{paid:,.2f}\n"
                f"• बाकी शिल्लक: ₹{pending:,.2f}"
            )
        elif lang == "hi":
            message = (
                f"**सेमेस्टर {fee.semester} ({fee.academic_year}) के लिए भुगतान स्थिति**:\n\n"
                f"{summary}\n\n"
                f"• कुल फीस: ₹{total:,.2f}\n"
                f"• जमा राशि: ₹{paid:,.2f}\n"
                f"• बकाया राशि: ₹{pending:,.2f}"
            )
        else:
            message = (
                f"**Payment Status for Semester {fee.semester} ({fee.academic_year})**:\n\n"
                f"{summary}\n\n"
                f"• Total Fee: ₹{total:,.2f}\n"
                f"• Paid: ₹{paid:,.2f}\n"
                f"• Balance Remaining: ₹{pending:,.2f}"
            )

        return {
            "message": message,
            "status": status,
            "fee_id": fee.id,
            "paid_amount": paid,
            "pending_amount": pending,
        }

    @classmethod
    def handle_payment_history(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Retrieves verified payment transactions recorded for the student."""
        payments = FeeService.get_payments(db, user_id)
        if not payments:
            if lang == "mr":
                msg = "तुमच्या खात्यावर कोणतेही व्यवहार आढळले नाहीत. जर तुम्ही नुकताच भरणा केला असेल तर पडताळणीसाठी २४-४८ तास लागू शकतात."
            elif lang == "hi":
                msg = "आपके खाते में कोई भुगतान लेनदेन नहीं मिला। यदि आपने हाल ही में भुगतान किया है, तो समाधान में २४-४८ घंटे लग सकते हैं।"
            else:
                msg = "No payment transactions were found in your transaction history. If you recently made a payment, it may take 24–48 hours to reconcile."
            return {"message": msg, "payments": []}

        if lang == "mr":
            lines = ["**तुमचा अलीकडील पेमेंट इतिहास:**\n"]
        elif lang == "hi":
            lines = ["**आपका हालिया भुगतान इतिहास:**\n"]
        else:
            lines = ["**Your Recent Payment History:**\n"]

        total_recorded = 0.0
        for p in payments:
            amt = float(p.amount)
            total_recorded += amt
            dt_str = format_localized_date(p.payment_date, lang)
            txn = f" (Txn ID: `{p.transaction_id}`)" if p.transaction_id else ""
            lines.append(f"• **₹{amt:,.2f}** on {dt_str} via {p.payment_method} — *{p.fee_type}* [{p.status.upper()}]{txn}")

        if lang == "mr":
            lines.append(f"\n**एकूण नोंदवलेला भरणा:** ₹{total_recorded:,.2f}")
        elif lang == "hi":
            lines.append(f"\n**कुल दर्ज भुगतान:** ₹{total_recorded:,.2f}")
        else:
            lines.append(f"\n**Total Recorded Payments:** ₹{total_recorded:,.2f}")

        return {
            "message": "\n".join(lines),
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "date": p.payment_date.isoformat(),
                    "fee_type": p.fee_type,
                    "method": p.payment_method,
                    "transaction_id": p.transaction_id,
                    "status": p.status,
                }
                for p in payments
            ],
        }

    @classmethod
    def handle_due_date(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Reports the official due date and overdue warnings in target language."""
        if not fee.due_date:
            if lang == "mr":
                msg = f"सत्र {fee.semester} ({fee.academic_year}) साठी कोणतीही निश्चित मुदत तारीख नोंदवलेली नाही."
            elif lang == "hi":
                msg = f"सेमेस्टर {fee.semester} ({fee.academic_year}) के लिए कोई अंतिम तिथि निर्धारित नहीं है।"
            else:
                msg = f"There is no explicit due date scheduled for Semester {fee.semester} ({fee.academic_year})."
            return {"message": msg, "due_date": None}

        today = date.today()
        due = fee.due_date
        due_formatted = format_localized_date(due, lang)
        days_diff = (due - today).days
        pending = float(fee.pending_amount)

        if lang == "mr":
            if pending <= 0:
                message = f"सत्र {fee.semester} ची अंतिम देय तारीख **{due_formatted}** होती, परंतु तुमची फी आधीच **पूर्णपणे भरलेली** आहे!"
            elif days_diff < 0:
                message = (
                    f"⚠️ **महत्त्वाची सूचना: मुदत संपली आहे!**\n\n"
                    f"**सत्र {fee.semester} ({fee.academic_year})** ची फी भरण्याची अंतिम तारीख **{due_formatted}** होती "
                    f"({abs(days_diff)} दिवसांपूर्वी). शिल्लक **₹{pending:,.2f}** थकीत आहे.\n"
                    f"दंड किंवा परीक्षा अडथळा टाळण्यासाठी कृपया लवकरात लवकर भरणा करा."
                )
            elif days_diff == 0:
                message = (
                    f"⚠️ **आज फी भरण्याची शेवटची तारीख आहे!**\n\n"
                    f"**सत्र {fee.semester}** ची शिल्लक फी **₹{pending:,.2f}** आज (**{due_formatted}**) पर्यंत भरणे आवश्यक आहे."
                )
            else:
                message = (
                    f"**सत्र {fee.semester} ({fee.academic_year})** ची फी भरण्याची अंतिम मुदत तारीख **{due_formatted}** आहे "
                    f"({days_diff} दिवस शिल्लक).\n"
                    f"शिल्लक फी: **₹{pending:,.2f}**."
                )
        elif lang == "hi":
            if pending <= 0:
                message = f"सेमेस्टर {fee.semester} की अंतिम तारीख **{due_formatted}** थी, लेकिन आपकी फीस पहले से ही **पूर्णतः जमा** है!"
            elif days_diff < 0:
                message = (
                    f"⚠️ **ध्यान दें: समय सीमा समाप्त!**\n\n"
                    f"**सेमेस्टर {fee.semester} ({fee.academic_year})** के लिए फीस की अंतिम तिथि **{due_formatted}** थी "
                    f"({abs(days_diff)} दिन पहले)। बकाया **₹{pending:,.2f}** अतिदेय है।\n"
                    f"विलंब शुल्क से बचने के लिए कृपया इसे तुरंत जमा करें।"
                )
            elif days_diff == 0:
                message = (
                    f"⚠️ **आज अंतिम तिथि है!**\n\n"
                    f"**सेमेस्टर {fee.semester}** की **₹{pending:,.2f}** फीस आज (**{due_formatted}**) तक जमा करनी अनिवार्य है।"
                )
            else:
                message = (
                    f"**सेमेस्टर {fee.semester} ({fee.academic_year})** के लिए फीस जमा करने की अंतिम तिथि **{due_formatted}** है "
                    f"({days_diff} दिन शेष)।\n"
                    f"बकाया राशि: **₹{pending:,.2f}**।"
                )
        else:
            if pending <= 0:
                message = f"The due date for Semester {fee.semester} was **{due_formatted}**, but your fees are already **fully paid**!"
            elif days_diff < 0:
                message = (
                    f"⚠️ **Attention: Overdue!**\n\n"
                    f"The fee payment deadline for **Semester {fee.semester} ({fee.academic_year})** was **{due_formatted}** "
                    f"({abs(days_diff)} days ago). A remaining balance of **₹{pending:,.2f}** is overdue.\n"
                    f"Please clear this immediately to avoid late fees or registration hold."
                )
            elif days_diff == 0:
                message = (
                    f"⚠️ **Today is the deadline!**\n\n"
                    f"The fee payment of **₹{pending:,.2f}** for **Semester {fee.semester}** is due **today ({due_formatted})**."
                )
            else:
                message = (
                    f"The fee due date for **Semester {fee.semester} ({fee.academic_year})** is **{due_formatted}** "
                    f"({days_diff} days remaining).\n"
                    f"Pending balance: **₹{pending:,.2f}**."
                )

        return {
            "message": message,
            "due_date": due.isoformat(),
            "days_remaining": days_diff,
            "pending_amount": pending,
        }

    @classmethod
    def handle_scholarship(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Provides scholarship deduction details and application guidance."""
        sch_amt = float(fee.scholarship_amount)
        total = float(fee.total_fee)
        pending = float(fee.pending_amount)

        if lang == "mr":
            if sch_amt > 0:
                message = (
                    f"**शिष्यवृत्ती तपशील (सत्र {fee.semester}, शैक्षणिक वर्ष {fee.academic_year})**:\n\n"
                    f"• तुमच्या खात्यावर **₹{sch_amt:,.2f}** शिष्यवृत्ती/सूट रक्कम समायोजित केली गेली आहे.\n"
                    f"• एकूण मूळ फी: ₹{total:,.2f}\n"
                    f"• शिष्यवृत्तीनंतर निव्वळ देय फी: ₹{(total - sch_amt):,.2f}\n"
                    f"• चालू शिल्लक बाकी: ₹{pending:,.2f}\n\n"
                    f"जर तुम्ही शासकीय महाडीबीटी (MahaDBT) किंवा केंद्र सरकारच्या शिष्यवृत्तीची वाट पाहत असाल, "
                    f"तर ती रक्कम कॉलेजकडे जमा झाल्यावर आपोआप समायोजित होईल."
                )
            else:
                message = (
                    f"सत्र {fee.semester} ({fee.academic_year}) साठी सध्या कोणतीही शिष्यवृत्ती लागू केलेली नाही.\n\n"
                    f"पात्र विद्यार्थी महाडीबीटी (MahaDBT), ईबीसी (EBC), किंवा टीएफडब्ल्यूएस (TFWS) शिष्यवृत्तीसाठी अर्ज करू शकतात. "
                    f"मंजूर अर्जाची प्रत कॉलेजच्या शिष्यवृत्ती कक्षात जमा करावी."
                )
        elif lang == "hi":
            if sch_amt > 0:
                message = (
                    f"**छात्रवृत्ति विवरण (सेमेस्टर {fee.semester}, शैक्षणिक वर्ष {fee.academic_year})**:\n\n"
                    f"• आपके खाते में **₹{sch_amt:,.2f}** की छात्रवृत्ति/छूट राशि समायोजित कर दी गई है।\n"
                    f"• सकल कुल फीस: ₹{total:,.2f}\n"
                    f"• छात्रवृत्ति के बाद देय राशि: ₹{(total - sch_amt):,.2f}\n"
                    f"• वर्तमान बकाया राशि: ₹{pending:,.2f}\n\n"
                    f"यदि आपको अतिरिक्त सरकारी छात्रवृत्ति (MahaDBT, NSP, EBC) प्राप्त होनी है, "
                    f"तो कॉलेज द्वारा प्राप्त होते ही आपके खाते में जोड़ दी जाएगी।"
                )
            else:
                message = (
                    f"सेमेस्टर {fee.semester} ({fee.academic_year}) के लिए वर्तमान में कोई छात्रवृत्ति कटौती लागू नहीं है।\n\n"
                    f"पात्र छात्र सरकारी पोर्टल (MahaDBT, NSP, EBC) के माध्यम से छात्रवृत्ति के लिए आवेदन कर सकते हैं।"
                )
        else:
            if sch_amt > 0:
                message = (
                    f"**Scholarship / Concession Details (Semester {fee.semester}, AY {fee.academic_year})**:\n\n"
                    f"• An amount of **₹{sch_amt:,.2f}** has been credited as scholarship/waiver to your account.\n"
                    f"• Gross Total Fee: ₹{total:,.2f}\n"
                    f"• Net Payable after Scholarship: ₹{(total - sch_amt):,.2f}\n"
                    f"• Outstanding Balance: ₹{pending:,.2f}\n\n"
                    f"If you are expecting an additional state or central scholarship disbursement (e.g., MahaDBT, NSP, EBC), "
                    f"it will be adjusted against your records once credited by the college authority."
                )
            else:
                message = (
                    f"No scholarship deduction is currently applied to your record for Semester {fee.semester} ({fee.academic_year}).\n\n"
                    f"Eligible students can apply for Government scholarships (MahaDBT, NSP, EBC, TFWS) via the scholarship portal. "
                    f"Submit the approved endorsement form to the college scholarship desk for fee adjustments."
                )

        return {
            "message": message,
            "scholarship_amount": sch_amt,
            "total_fee": total,
            "pending_amount": pending,
        }

    @classmethod
    def handle_record_payment(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """
        Conversational Payment Auto-Recording:
        Detects payment declaration from user, deterministically updates StudentFee in PostgreSQL,
        inserts a completed Payment transaction, appends an audit entry to StudentFee.notes,
        and returns a localized confirmation with updated balances and next-installment guidance.
        """
        if not fee:
            resolved_fee, disambig_prompt, disambig_options = cls.resolve_target_fee(
                db, user_id, entities, lang=lang
            )
            if not resolved_fee:
                return {
                    "message": disambig_prompt or "Please specify the semester for this payment.",
                    "needs_clarification": disambig_options is not None,
                    "options": disambig_options,
                }
            fee = resolved_fee

        amount_to_pay = float(entities.get("amount") or 0.0)
        if amount_to_pay <= 0.0:
            if lang == "mr":
                msg = "कृपया तुम्ही भरलेली अचूक रक्कम नमूद करा (उदा. 'मी ₹१०,००० भरले')."
            elif lang == "hi":
                msg = "कृपया आपके द्वारा भुगतान की गई सही राशि बताएं (उदा. 'मैंने ₹१०,००० जमा किए')।"
            else:
                msg = "Please specify the exact amount you paid (e.g. 'I paid ₹10,000 for semester 5')."
            return {"message": msg, "recorded": False}

        old_paid = float(fee.paid_amount)
        total = float(fee.total_fee)
        sch = float(fee.scholarship_amount)
        new_paid = round(old_paid + amount_to_pay, 2)
        new_pending = max(0.0, round(total - new_paid - sch, 2))

        # Generate unique transaction ID
        txn_id = f"CHAT-{uuid.uuid4().hex[:8].upper()}"
        pay_date = date.today()
        pay_method = entities.get("payment_method") or "UPI / Online"
        fee_cat = fee.fee_type or "Tuition"

        # 1. Create Payment transaction record in PostgreSQL
        payment_notes = (
            f"Auto-recorded via chat: ₹{amount_to_pay:,.2f} for Semester {fee.semester} "
            f"({fee.academic_year}) on {pay_date.isoformat()}."
        )
        new_payment = Payment(
            user_id=user_id,
            amount=amount_to_pay,
            payment_date=pay_date,
            fee_type=fee_cat,
            payment_method=pay_method,
            transaction_id=txn_id,
            status="completed",
            notes=payment_notes,
        )
        db.add(new_payment)

        # 2. Update StudentFee balances and audit trail in notes
        fee.paid_amount = new_paid
        fee.pending_amount = new_pending

        audit_entry = f"[{pay_date.isoformat()}] Paid ₹{amount_to_pay:,.2f} via chat (Txn: {txn_id}). Remaining: ₹{new_pending:,.2f}."
        if fee.notes:
            updated_notes = f"{fee.notes} | {audit_entry}"
        else:
            updated_notes = audit_entry

        # Keep notes safely within VARCHAR(500) limit
        if len(updated_notes) > 480:
            updated_notes = updated_notes[-480:]
        fee.notes = updated_notes

        db.commit()
        db.refresh(fee)

        dt_formatted = format_localized_date(pay_date, lang)

        # 3. Formulate localized response
        if lang == "mr":
            if new_pending <= 0:
                follow_up = "अभिनंदन! या सत्राची तुमची संपूर्ण फी आता **पूर्णपणे चुकता (100% Paid)** झाली आहे."
            else:
                p1 = round(new_pending / 2, 2)
                follow_up = (
                    f"उर्वरित **₹{new_pending:,.2f}** शिल्लक रकमेसाठी, तुम्ही प्रत्येकी **₹{p1:,.2f}** चे "
                    f"२ हप्ते करू शकता."
                )
            message = (
                f"**सत्र {fee.semester} ({fee.academic_year})** साठी **₹{amount_to_pay:,.2f}** चा भरणा यशस्वीरीत्या नोंदवला गेला आहे!\n\n"
                f"• **व्यवहार आयडी (Txn ID):** `{txn_id}`\n"
                f"• **तारीख:** {dt_formatted}\n"
                f"• **माध्यम:** {pay_method}\n"
                f"• **एकूण भरलेली रक्कम:** ₹{new_paid:,.2f}\n"
                f"• **नवीन शिल्लक बाकी:** ₹{new_pending:,.2f}\n"
                f"• **नोंदवलेली टीप (Saved Note):** \"{audit_entry}\"\n\n"
                f"{follow_up}"
            )
        elif lang == "hi":
            if new_pending <= 0:
                follow_up = "बधाई हो! इस सेमेस्टर की आपकी कुल फीस अब **पूर्णतः चुकता (100% Paid)** हो चुकी है।"
            else:
                p1 = round(new_pending / 2, 2)
                follow_up = (
                    f"शेष **₹{new_pending:,.2f}** की बकाया राशि के लिए, आप प्रत्येक **₹{p1:,.2f}** की "
                    f"२ किस्तों में भुगतान कर सकते हैं।"
                )
            message = (
                f"**सेमेस्टर {fee.semester} ({fee.academic_year})** के लिए **₹{amount_to_pay:,.2f}** का भुगतान सफलतापूर्वक दर्ज कर लिया गया है!\n\n"
                f"• **लेनदेन आईडी (Txn ID):** `{txn_id}`\n"
                f"• **दिनांक:** {dt_formatted}\n"
                f"• **माध्यम:** {pay_method}\n"
                f"• **कुल जमा राशि:** ₹{new_paid:,.2f}\n"
                f"• **अद्यतन शेष बकाया:** ₹{new_pending:,.2f}\n"
                f"• **दर्ज टिप्पणी (Saved Note):** \"{audit_entry}\"\n\n"
                f"{follow_up}"
            )
        else:
            if new_pending <= 0:
                follow_up = "Congratulations! Your fee for this semester is now **settled in full (100% Paid)**."
            else:
                p1 = round(new_pending / 2, 2)
                follow_up = (
                    f"For your remaining balance of **₹{new_pending:,.2f}**, a recommended option is "
                    f"2 installments of **₹{p1:,.2f}** each."
                )
            message = (
                f"Payment of **₹{amount_to_pay:,.2f}** has been successfully recorded for "
                f"**Semester {fee.semester} ({fee.academic_year})**!\n\n"
                f"• **Transaction ID:** `{txn_id}`\n"
                f"• **Date:** {dt_formatted}\n"
                f"• **Payment Mode:** {pay_method}\n"
                f"• **Total Paid to Date:** ₹{new_paid:,.2f}\n"
                f"• **Updated Remaining Balance:** ₹{new_pending:,.2f}\n"
                f"• **Audit Note Saved:** \"{audit_entry}\"\n\n"
                f"{follow_up}"
            )

        return {
            "message": message,
            "recorded": True,
            "transaction_id": txn_id,
            "paid_amount": new_paid,
            "pending_amount": new_pending,
            "payment_notes": payment_notes,
            "fee_notes": fee.notes,
        }

    @classmethod
    def handle_installment(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: StudentFee,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """
        Deep Reasoning Installment & Notes Synthesizer:
        1. Reads fee.notes and payment.notes for past installments, agreements, and payment remarks.
        2. Computes count and volume of completed installments.
        3. If balance remains, formulates an intelligent segregation plan with suggested dates.
        4. If notes were empty, explains that standard segregation applies and recommends a schedule.
        """
        pending = float(fee.pending_amount)
        paid = float(fee.paid_amount)
        total = float(fee.total_fee)

        # Retrieve past payment history for context
        all_payments = FeeService.get_payments(db, user_id)
        # Filter payments relevant to this semester or fee type
        payments_done = [p for p in all_payments if p.status == "completed"]
        completed_count = len(payments_done)
        total_installments_paid = sum(float(p.amount) for p in payments_done)

        today = date.today()
        d30 = today + timedelta(days=30)
        d60 = today + timedelta(days=60)
        d90 = today + timedelta(days=90)

        d30_str = format_localized_date(d30, lang)
        d60_str = format_localized_date(d60, lang)
        d90_str = format_localized_date(d90, lang)

        # Check if fee has recorded notes
        has_fee_notes = bool(fee.notes and fee.notes.strip())
        notes_text = fee.notes.strip() if has_fee_notes else ""

        # Check if payments have notes
        pmt_notes_list = [f"• {format_localized_date(p.payment_date, lang)}: ₹{float(p.amount):,.2f} — {p.notes}" for p in payments_done if p.notes]

        if pending <= 0:
            if lang == "mr":
                msg = (
                    f"**सत्र {fee.semester} ({fee.academic_year})** ची संपूर्ण फी आधीच भरलेली आहे!\n\n"
                    f"• एकूण फी: ₹{total:,.2f}\n"
                    f"• भरलेली रक्कम: ₹{paid:,.2f}\n"
                    f"• पूर्ण झालेले हप्ते: {completed_count} व्यवहार (एकूण ₹{total_installments_paid:,.2f})\n\n"
                    f"कोणतीही रक्कम शिल्लक नसल्याने नवीन हप्ता योजनेची आवश्यकता नाही."
                )
            elif lang == "hi":
                msg = (
                    f"**सेमेस्टर {fee.semester} ({fee.academic_year})** की कुल फीस पहले ही पूरी जमा हो चुकी है!\n\n"
                    f"• कुल फीस: ₹{total:,.2f}\n"
                    f"• जमा राशि: ₹{paid:,.2f}\n"
                    f"• पूर्ण किस्तें: {completed_count} लेनदेन (कुल ₹{total_installments_paid:,.2f})\n\n"
                    f"कोई बकाया न होने के कारण नई किस्त योजना की आवश्यकता नहीं है।"
                )
            else:
                msg = (
                    f"Your fees for **Semester {fee.semester} ({fee.academic_year})** are already fully paid!\n\n"
                    f"• Total Fee: ₹{total:,.2f}\n"
                    f"• Amount Paid: ₹{paid:,.2f}\n"
                    f"• Completed Installments: {completed_count} payments (totaling ₹{total_installments_paid:,.2f})\n\n"
                    f"No further installment plan is required since there is zero outstanding balance."
                )
            return {"message": msg, "pending_amount": 0.0, "completed_installments": completed_count}

        # User requested specific count
        requested_count = entities.get("installment_count")

        if lang == "mr":
            sections = []
            sections.append(f"**हप्ता विश्लेषण व विभाजन (सत्र {fee.semester}, {fee.academic_year})**\n")

            # 1. Past Installments & Notes Summary
            if completed_count > 0:
                sections.append(
                    f"**यापूर्वी झालेले हप्ते (Completed Installments):**\n"
                    f"• आतापर्यंत **{completed_count} हप्ते/व्यवहार** नोंदवले गेले आहेत (एकूण भरणा: **₹{total_installments_paid:,.2f}**).\n"
                    f"• सध्या शिल्लक रक्कम: **₹{pending:,.2f}**"
                )
            else:
                sections.append(
                    f"**हप्ता स्थिती:**\n"
                    f"• आतापर्यंत कोणताही हप्ता भरलेला नाही.\n"
                    f"• एकूण शिल्लक देय रक्कम: **₹{pending:,.2f}**"
                )

            if has_fee_notes:
                sections.append(f"**नोंदवलेल्या नोंदी (Your Fee Notes):**\n> *\"{notes_text}\"*")
            if pmt_notes_list:
                sections.append("**व्यवहारांमधील नोंदी (Payment Remarks):**\n" + "\n".join(pmt_notes_list[:3]))

            # 2. Intelligent Segregation Plan
            sections.append("**शिफारस केलेले योग्य विभाजन (Recommended Segregation Plan):**")
            if requested_count and requested_count > 1:
                per_part = round(pending / requested_count, 2)
                plan_lines = []
                for i in range(1, requested_count + 1):
                    due_d = today + timedelta(days=30 * i)
                    plan_lines.append(f"• **हप्ता {i}:** ₹{per_part:,.2f} (अंदाजे तारीख: {format_localized_date(due_d, lang)})")
                sections.append(f"तुमच्या विनंतीनुसार **{requested_count} समान हप्त्यांमध्ये** विभाजन:\n" + "\n".join(plan_lines))
            else:
                p2_1 = round(pending / 2, 2)
                p2_2 = round(pending - p2_1, 2)
                p3_1 = round(pending / 3, 2)
                p3_2 = round(pending / 3, 2)
                p3_3 = round(pending - p3_1 - p3_2, 2)

                sections.append(
                    f"**पर्याय १ — २ भागांमध्ये विभाजन (50% - 50%):**\n"
                    f"  १. पहिला हप्ता: **₹{p2_1:,.2f}** (देय: {d30_str})\n"
                    f"  २. दुसरा हप्ता: **₹{p2_2:,.2f}** (देय: {d60_str})\n\n"
                    f"**पर्याय २ — ३ भागांमध्ये सुलभ मासिक विभाजन:**\n"
                    f"  १. पहिला हप्ता: **₹{p3_1:,.2f}** (देय: {d30_str})\n"
                    f"  २. दुसरा हप्ता: **₹{p3_2:,.2f}** (देय: {d60_str})\n"
                    f"  ३. तिसरा हप्ता: **₹{p3_3:,.2f}** (देय: {d90_str})"
                )

            sections.append("हप्ता सुविधेची अधिकृत मंजुरी मिळवण्यासाठी लेखा विभागात हमीपत्र (undertaking) जमा करा.")
            message = "\n\n".join(sections)

        elif lang == "hi":
            sections = []
            sections.append(f"**किस्त विश्लेषण एवं विभाजन योजना (सेमेस्टर {fee.semester}, {fee.academic_year})**\n")

            if completed_count > 0:
                sections.append(
                    f"**पूर्व में किए गए भुगतान (Completed Installments):**\n"
                    f"• अब तक **{completed_count} किस्तें/लेनदेन** दर्ज हैं (कुल भुगतान: **₹{total_installments_paid:,.2f}**)।\n"
                    f"• वर्तमान शेष बकाया: **₹{pending:,.2f}**"
                )
            else:
                sections.append(
                    f"**किस्त स्थिति:**\n"
                    f"• अभी तक कोई किस्त जमा नहीं हुई है।\n"
                    f"• कुल बकाया राशि: **₹{pending:,.2f}**"
                )

            if has_fee_notes:
                sections.append(f"**आपके खाते में दर्ज टिप्पणियां (Your Fee Notes):**\n> *\"{notes_text}\"*")
            if pmt_notes_list:
                sections.append("**भुगतान लेनदेन की टिप्पणियां (Payment Remarks):**\n" + "\n".join(pmt_notes_list[:3]))

            sections.append("**उचित किस्त विभाजन योजना (Recommended Segregation Plan):**")
            if requested_count and requested_count > 1:
                per_part = round(pending / requested_count, 2)
                plan_lines = []
                for i in range(1, requested_count + 1):
                    due_d = today + timedelta(days=30 * i)
                    plan_lines.append(f"• **किस्त {i}:** ₹{per_part:,.2f} (अनुशंसित तिथि: {format_localized_date(due_d, lang)})")
                sections.append(f"आपके अनुरोध अनुसार **{requested_count} समान किस्तों** में विभाजन:\n" + "\n".join(plan_lines))
            else:
                p2_1 = round(pending / 2, 2)
                p2_2 = round(pending - p2_1, 2)
                p3_1 = round(pending / 3, 2)
                p3_2 = round(pending / 3, 2)
                p3_3 = round(pending - p3_1 - p3_2, 2)

                sections.append(
                    f"**विकल्प १ — २ भागों में विभाजन (50% - 50%):**\n"
                    f"  १. पहली किस्त: **₹{p2_1:,.2f}** (अंतिम तिथि: {d30_str})\n"
                    f"  २. दूसरी किस्त: **₹{p2_2:,.2f}** (अंतिम तिथि: {d60_str})\n\n"
                    f"**विकल्प २ — ३ भागों में सुगम मासिक विभाजन:**\n"
                    f"  १. पहली किस्त: **₹{p3_1:,.2f}** (अंतिम तिथि: {d30_str})\n"
                    f"  २. दूसरी किस्त: **₹{p3_2:,.2f}** (अंतिम तिथि: {d60_str})\n"
                    f"  ३. तीसरी किस्त: **₹{p3_3:,.2f}** (अंतिम तिथि: {d90_str})"
                )

            sections.append("किस्त सुविधा की आधिकारिक अनुमति हेतु कॉलेज के लेखा विभाग में आवेदन जमा करें।")
            message = "\n\n".join(sections)

        else:
            sections = []
            sections.append(f"**Installment Analysis & Segregation Plan (Semester {fee.semester}, {fee.academic_year})**\n")

            if completed_count > 0:
                sections.append(
                    f"**Previous Installments on Record:**\n"
                    f"• **{completed_count} installment payments** completed to date (Total paid: **₹{total_installments_paid:,.2f}**).\n"
                    f"• Remaining outstanding balance: **₹{pending:,.2f}**"
                )
            else:
                sections.append(
                    f"**Installment Status:**\n"
                    f"• No installment payments have been made yet.\n"
                    f"• Total outstanding balance: **₹{pending:,.2f}**"
                )

            if has_fee_notes:
                sections.append(f"**Recorded Fee Notes & Undertakings:**\n> *\"{notes_text}\"*")
            if pmt_notes_list:
                sections.append("**Payment Transaction Remarks:**\n" + "\n".join(pmt_notes_list[:3]))

            sections.append("**Recommended Segregation Schedule:**")
            if requested_count and requested_count > 1:
                per_part = round(pending / requested_count, 2)
                plan_lines = []
                for i in range(1, requested_count + 1):
                    due_d = today + timedelta(days=30 * i)
                    plan_lines.append(f"• **Installment {i}:** ₹{per_part:,.2f} (Target date: {format_localized_date(due_d, lang)})")
                sections.append(f"Custom plan divided into **{requested_count} equal installments**:\n" + "\n".join(plan_lines))
            else:
                p2_1 = round(pending / 2, 2)
                p2_2 = round(pending - p2_1, 2)
                p3_1 = round(pending / 3, 2)
                p3_2 = round(pending / 3, 2)
                p3_3 = round(pending - p3_1 - p3_2, 2)

                sections.append(
                    f"**Option 1 — 2-Part Balanced Segregation (50% / 50%):**\n"
                    f"  1. Installment 1: **₹{p2_1:,.2f}** (Target: {d30_str})\n"
                    f"  2. Installment 2: **₹{p2_2:,.2f}** (Target: {d60_str})\n\n"
                    f"**Option 2 — 3-Part Monthly Segregation:**\n"
                    f"  1. Installment 1: **₹{p3_1:,.2f}** (Target: {d30_str})\n"
                    f"  2. Installment 2: **₹{p3_2:,.2f}** (Target: {d60_str})\n"
                    f"  3. Installment 3: **₹{p3_3:,.2f}** (Target: {d90_str})"
                )

            sections.append("To formally adopt an installment schedule, submit an undertaking form to the college accounts section.")
            message = "\n\n".join(sections)

        return {
            "message": message,
            "pending_amount": pending,
            "completed_installments": completed_count,
            "fee_notes": fee.notes,
            "calculated_installments": {
                "two_parts": round(pending / 2, 2),
                "three_parts": round(pending / 3, 2),
            },
        }

    @classmethod
    def handle_notes_query(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Summarizes all custom notes, promises, and remarks recorded on fees and payments."""
        if not fee:
            fees = FeeService.get_student_fees(db, user_id)
            if not fees:
                msg = "No fee records found on your account."
                return {"message": msg, "notes": []}
            fee = fees[0]

        payments = FeeService.get_payments(db, user_id)
        pmt_notes = [p for p in payments if p.notes]

        has_fee_notes = bool(fee.notes and fee.notes.strip())

        if not has_fee_notes and not pmt_notes:
            if lang == "mr":
                msg = f"सत्र {fee.semester} साठी तुमच्या रेकॉर्डमध्ये सध्या कोणतीही विशेष नोंद (Notes) जतन केलेली नाही."
            elif lang == "hi":
                msg = f"सेमेस्टर {fee.semester} के लिए आपके रिकॉर्ड में वर्तमान में कोई विशेष टिप्पणी (Notes) दर्ज नहीं है।"
            else:
                msg = f"There are currently no custom notes or remarks recorded for Semester {fee.semester}."
            return {"message": msg, "has_notes": False}

        if lang == "mr":
            lines = [f"**सत्र {fee.semester} ({fee.academic_year}) मधील जतन केलेल्या नोंदी (Notes):**\n"]
            if has_fee_notes:
                lines.append(f"• **फी रेकॉर्डमधील नोंद:**\n  > \"{fee.notes}\"\n")
            if pmt_notes:
                lines.append("• **पेमेंट व्यवहारांमधील नोंदी:**")
                for p in pmt_notes[:5]:
                    dt_s = format_localized_date(p.payment_date, lang)
                    lines.append(f"  - [{dt_s}] ₹{float(p.amount):,.2f}: {p.notes}")
        elif lang == "hi":
            lines = [f"**सेमेस्टर {fee.semester} ({fee.academic_year}) में दर्ज टिप्पणियां (Notes):**\n"]
            if has_fee_notes:
                lines.append(f"• **फीस रिकॉर्ड की टिप्पणी:**\n  > \"{fee.notes}\"\n")
            if pmt_notes:
                lines.append("• **भुगतान लेनदेन की टिप्पणियां:**")
                for p in pmt_notes[:5]:
                    dt_s = format_localized_date(p.payment_date, lang)
                    lines.append(f"  - [{dt_s}] ₹{float(p.amount):,.2f}: {p.notes}")
        else:
            lines = [f"**Recorded Notes & Remarks for Semester {fee.semester} ({fee.academic_year}):**\n"]
            if has_fee_notes:
                lines.append(f"• **Fee Record Note:**\n  > \"{fee.notes}\"\n")
            if pmt_notes:
                lines.append("• **Payment Transaction Remarks:**")
                for p in pmt_notes[:5]:
                    dt_s = format_localized_date(p.payment_date, lang)
                    lines.append(f"  - [{dt_s}] ₹{float(p.amount):,.2f}: {p.notes}")

        return {"message": "\n".join(lines), "has_notes": True, "fee_notes": fee.notes}

    @classmethod
    def handle_refund(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Checks for overpayment or provides institutional refund rules."""
        if fee and float(fee.paid_amount) > (float(fee.total_fee) - float(fee.scholarship_amount)):
            overpaid = round(float(fee.paid_amount) - (float(fee.total_fee) - float(fee.scholarship_amount)), 2)
            if lang == "mr":
                message = (
                    f"सत्र {fee.semester} साठी तुमच्या खात्यावर **₹{overpaid:,.2f}** अतिरिक्त जमा रक्कम आहे!\n\n"
                    f"ही अतिरिक्त रक्कम पुढील सत्रात समायोजित केली जाऊ शकते किंवा तुमच्या बँक खात्यात परत दिली जाऊ शकते. "
                    f"परताव्यासाठी बँक तपशिलांसह लेखा विभागात अर्ज करावा."
                )
            elif lang == "hi":
                message = (
                    f"सेमेस्टर {fee.semester} के लिए आपके खाते में **₹{overpaid:,.2f}** का अतिरिक्त भुगतान क्रेडिट है!\n\n"
                    f"यह अतिरिक्त राशि अगले सत्र में समायोजित की जा सकती है या आपके बैंक खाते में वापस की जा सकती है।"
                )
            else:
                message = (
                    f"You have an overpayment credit of **₹{overpaid:,.2f}** for Semester {fee.semester}!\n\n"
                    f"This excess amount can either be adjusted against your next term fees or refunded to your bank account."
                )
            return {"message": message, "refund_eligible": True, "overpaid_amount": overpaid}

        if lang == "mr":
            message = (
                "**महाविद्यालयीन फी परतावा (Refund) धोरण:**\n\n"
                "• फी परतावा यूजीसी/एआयसीटीई (UGC/AICTE) आणि विद्यापीठाच्या नियमांनुसार केला जातो.\n"
                "• दुबार भरणा (duplicate payment) किंवा प्रवेश रद्द झाल्यास १५-२० कामकाजाच्या दिवसांत मूळ बँक खात्यात परतावा जमा होतो.\n"
                "• परतावा अर्जासाठी व्यवहाराच्या पावतीसह लेखा विभागात संपर्क साधावा."
            )
        elif lang == "hi":
            message = (
                "**कॉलेज फीस वापसी (Refund) नीति:**\n\n"
                "• फीस वापसी यूजीसी/एआईसीटीई (UGC/AICTE) संस्थागत दिशा-निर्देशों के अनुसार की जाती है।\n"
                "• दोहरा भुगतान होने या प्रवेश रद्द होने पर १५-२० कार्य दिवसों में राशि मूल स्रोत में वापस कर दी जाती है।\n"
                "• अधिक जानकारी के लिए लेखा विभाग में आवेदन दें।"
            )
        else:
            message = (
                "**College Fee Refund Policy:**\n\n"
                "• Fee refunds are processed according to UGC/AICTE institutional cancellation and refund guidelines.\n"
                "• If you have made a duplicate payment or cancelled admission, refunds are typically credited within 15–20 working days to the original payment source.\n"
                "• For refund requests, submit an application along with your transaction receipt to the accounts department."
            )
        return {"message": message, "refund_eligible": False}

    @classmethod
    def handle_receipt(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Provides verified payment receipts and transaction records."""
        payments = FeeService.get_payments(db, user_id)
        if not payments:
            if lang == "mr":
                msg = "कोणतीही पावती उपलब्ध नाही कारण तुमच्या खात्यावर कोणताही यशस्वी व्यवहार नोंदवलेला नाही."
            elif lang == "hi":
                msg = "कोई रसीद उपलब्ध नहीं है क्योंकि आपके खाते के लिए कोई सफल भुगतान लेनदेन नहीं मिला।"
            else:
                msg = "No payment receipts are currently available because no successful transactions were found for your account."
            return {"message": msg, "receipts": []}

        if lang == "mr":
            lines = ["**डाऊनलोडसाठी उपलब्ध अधिकृत फी पावत्या:**\n"]
        elif lang == "hi":
            lines = ["**डाउनलोड के लिए उपलब्ध आधिकारिक फीस रसीदें:**\n"]
        else:
            lines = ["**Official Fee Receipts Available for Download:**\n"]

        receipts = []
        for p in payments:
            receipt_no = f"REC-{p.payment_date.strftime('%Y%m')}-{p.id:04d}"
            amt = float(p.amount)
            txn = p.transaction_id or "N/A"
            dt = format_localized_date(p.payment_date, lang)
            lines.append(f"• **पावती #{receipt_no}** (Receipt #{receipt_no}): ₹{amt:,.2f} ({p.fee_type}) on {dt} [Txn: `{txn}`]")
            receipts.append({
                "receipt_number": receipt_no,
                "amount": amt,
                "date": dt,
                "fee_type": p.fee_type,
                "transaction_id": txn,
            })

        if lang == "mr":
            lines.append("\nतुम्ही स्टुडंट पोर्टलवरून अधिकृत शिक्का असलेली पावती डाऊनलोड करू शकता किंवा फी काउंटरवरून प्रत मिळवू शकता.")
        elif lang == "hi":
            lines.append("\nआप छात्र पोर्टल से आधिकारिक मुहर लगी रसीद डाउनलोड कर सकते हैं या फीस काउंटर से प्रति प्राप्त कर सकते हैं।")
        else:
            lines.append("\nYou can download official stamped receipts from the student portal or request a duplicate at the fees counter.")

        return {
            "message": "\n".join(lines),
            "receipts": receipts,
        }

    @classmethod
    def handle_other_fee_query(
        cls,
        db: Session,
        user_id: int,
        entities: Dict[str, Any],
        fee: Optional[StudentFee],
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Provides a helpful summary of account status in target language."""
        if fee:
            pending = float(fee.pending_amount)
            total = float(fee.total_fee)
            paid = float(fee.paid_amount)
            if lang == "mr":
                message = (
                    f"**सत्र {fee.semester} ({fee.academic_year})** साठी तुमची चालू फी स्थिती:\n\n"
                    f"• एकूण फी: ₹{total:,.2f}\n"
                    f"• भरलेली रक्कम: ₹{paid:,.2f}\n"
                    f"• शिल्लक फी: ₹{pending:,.2f}\n\n"
                    f"तुम्ही मला खालीलप्रमाणे विचारू शकता:\n"
                    f"- *'माझी किती फी बाकी आहे?'*\n"
                    f"- *'फी भरण्याची शेवटची तारीख कधी आहे?'*\n"
                    f"- *'मी हप्त्यांमध्ये पैसे भरू शकतो का?'*\n"
                    f"- *'माझी पावती दाखवा'*"
                )
            elif lang == "hi":
                message = (
                    f"**सेमेस्टर {fee.semester} ({fee.academic_year})** के लिए आपका वर्तमान फीस विवरण:\n\n"
                    f"• कुल फीस: ₹{total:,.2f}\n"
                    f"• जमा राशि: ₹{paid:,.2f}\n"
                    f"• बकाया राशि: ₹{pending:,.2f}\n\n"
                    f"आप मुझसे पूछ सकते हैं:\n"
                    f"- *'मेरी कितनी फीस बाकी है?'*\n"
                    f"- *'अंतिम तारीख कब है?'*\n"
                    f"- *'क्या मैं किश्तों में भर सकता हूँ?'*\n"
                    f"- *'मेरी भुगतान रसीद दिखाएं'*"
                )
            else:
                message = (
                    f"Here is your current fee overview for **Semester {fee.semester} ({fee.academic_year})**:\n\n"
                    f"• Total Fee: ₹{total:,.2f}\n"
                    f"• Paid: ₹{paid:,.2f}\n"
                    f"• Remaining: ₹{pending:,.2f}\n\n"
                    f"You can ask me specific questions such as:\n"
                    f"- *'How much fee is remaining?'*\n"
                    f"- *'When is the due date?'*\n"
                    f"- *'Can I pay in installments?'*\n"
                    f"- *'Show my payment history or receipts'*"
                )
        else:
            if lang == "mr":
                message = (
                    "FeeAssist AI मध्ये आपले स्वागत आहे! मी तुमची कॉलेज फी, शिल्लक रक्कम, देय तारीख, "
                    "भरणा इतिहास, शिष्यवृत्ती आणि हप्ता योजनेबद्दल मदत करू शकतो.\n\n"
                    "आज मी तुम्हाला कशी मदत करू?"
                )
            elif lang == "hi":
                message = (
                    "FeeAssist AI में आपका स्वागत है! मैं कॉलेज फीस, बकाया राशि, अंतिम तिथि, "
                    "भुगतान इतिहास, छात्रवृत्ति कटौती और किस्त विकल्पों में आपकी सहायता कर सकता हूँ।\n\n"
                    "आज मैं आपकी क्या सहायता कर सकता हूँ?"
                )
            else:
                message = (
                    "Welcome to FeeAssist AI! I can help you with your college fees, remaining balance, due dates, "
                    "payment history, scholarship deductions, and installment options.\n\n"
                    "How may I assist you with your fees today?"
                )
        return {"message": message}
