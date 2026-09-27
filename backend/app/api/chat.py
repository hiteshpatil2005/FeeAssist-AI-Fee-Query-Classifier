"""
FeeAssist AI — Conversational Fee Chat API

Orchestrates the entire fee query pipeline:
1. Validates authenticated student identity via JWT.
2. Extracts session context from previous turns.
3. Classifies user intent via trained ML NLP pipeline.
4. Extracts multilingual entities (amounts, dates, semesters, years, fee types).
5. Queries FeeService for student-specific database records and deterministic calculations.
6. Handles multi-record disambiguation when query is ambiguous.
7. Persists multi-turn conversation and message history to PostgreSQL.
"""

import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.security.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, MessageOut
from app.services.nlp_service import classify_intent
from app.services.entity_service import extract_entities
from app.services.language_service import resolve_language
from app.services.conversation_service import ConversationService
from app.services.fee_service import FeeService
from app.services.gemini_service import GeminiService

logger = logging.getLogger("feeassist.chat")

router = APIRouter()


@router.post("", response_model=ChatResponse, summary="Send a fee-related chat query")
@router.post("/message", response_model=ChatResponse, summary="Send a fee-related chat query (alias)")
async def chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main conversational endpoint:
    - User query is preprocessed and classified using the ML intent model.
    - Entities are extracted.
    - FeeService retrieves the authenticated student's fee details from PostgreSQL.
    - If multiple fee records exist and query does not specify which one, asks for clarification.
    - Accurately computes remaining balances, hypothetical payments, installments, and receipts.
    """
    raw_query = payload.message.strip()
    if not raw_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty",
        )

    # 1. Resolve Session ID
    session_id = payload.session_id or f"sess_{current_user.id}_{uuid.uuid4().hex[:8]}"

    # 2. Get or initialize Conversation
    conv = ConversationService.get_or_create_conversation(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        language=payload.language or "en",
    )

    # 2.5 Resolve interaction language (Priority: 1. Query lang -> 2. Session lang -> 3. User preferred lang -> 4. 'en')
    target_lang = resolve_language(
        query_text=raw_query,
        session_lang=conv.language,
        user_pref=getattr(current_user, "preferred_language", None),
    )
    if conv.language != target_lang:
        conv.language = target_lang
        db.commit()

    # 3. Retrieve recent conversation history for multi-turn context
    recent_messages = ConversationService.get_recent_messages(db, conv.id, limit=6)
    context_entities = ConversationService.infer_context_entities(recent_messages)

    # 4. Extract entities from current user query
    query_entities = extract_entities(raw_query)

    # 5. Merge query entities with session context (query overrides context)
    merged_entities = dict(context_entities)
    for k, v in query_entities.items():
        if v is not None:
            merged_entities[k] = v

    # Preserve hypothetical flag and amount specifically from current turn
    merged_entities["is_hypothetical"] = query_entities.get("is_hypothetical", False)
    if query_entities.get("amount") is not None:
        merged_entities["amount"] = query_entities["amount"]

    # 6. NLP Intent Classification
    nlp_result = classify_intent(raw_query)
    predicted_intent = nlp_result["intent"]
    confidence = nlp_result["confidence"]

    # 7. Domain Boundary Guardrail
    if GeminiService.is_out_of_domain(raw_query):
        response_text = GeminiService.get_out_of_domain_refusal(target_lang)
        ConversationService.save_message(
            db=db,
            conversation_id=conv.id,
            role="user",
            message=raw_query,
            intent="OUT_OF_DOMAIN",
            confidence=confidence,
        )
        ConversationService.save_message(
            db=db,
            conversation_id=conv.id,
            role="assistant",
            message=response_text,
            intent="OUT_OF_DOMAIN",
            confidence=confidence,
        )
        return ChatResponse(
            message=response_text,
            intent="OUT_OF_DOMAIN",
            confidence=confidence,
            detected_language=target_lang,
            entities=merged_entities,
            session_id=session_id,
            needs_clarification=False,
            options=None,
            fee_data=None,
            fallback_used=False,
            source="guardrail",
        )

    # Override intent if query is clearly a hypothetical payment calculation: "What if I pay ₹10,000?"
    is_hypo = bool(merged_entities.get("is_hypothetical") and merged_entities.get("amount") is not None)
    if is_hypo:
        predicted_intent = "PENDING_FEE"

    needs_clarification = False
    options = None
    fee_data = None
    response_text = ""
    fallback_used = False
    source = "ml"

    # 8. Controlled Secondary Fallback (Gemini API)
    # Triggered when confidence < NLP_CONFIDENCE_THRESHOLD or intent is OTHER_FEE_QUERY (complex/unclassified)
    # Hypothetical payment calculations are excluded because they require deterministic arithmetic.
    should_fallback = (
        confidence < settings.NLP_CONFIDENCE_THRESHOLD or predicted_intent == "OTHER_FEE_QUERY"
    ) and not is_hypo

    gemini_succeeded = False
    if should_fallback:
        try:
            student_fees = FeeService.get_student_fees(db, current_user.id)
            student_payments = FeeService.get_payments(db, current_user.id)
            verified_context = {
                "student_name": current_user.name,
                "email": current_user.email,
                "course": current_user.course or "General",
                "semester": current_user.semester or 1,
                "academic_year": student_fees[0].academic_year if student_fees else "Current",
                "fee_records": [
                    {
                        "fee_type": f.fee_type or "Tuition",
                        "total_amount": float(f.total_fee),
                        "paid_amount": float(f.paid_amount),
                        "pending_amount": float(f.pending_amount),
                        "due_date": str(f.due_date) if f.due_date else "N/A",
                        "status": "paid" if float(f.pending_amount) <= 0 else "pending",
                        "semester": f.semester,
                        "academic_year": f.academic_year,
                    }
                    for f in student_fees
                ],
                "recent_payments": [
                    {
                        "transaction_id": p.transaction_id or "N/A",
                        "amount": float(p.amount),
                        "payment_mode": p.payment_method,
                        "payment_date": str(p.payment_date),
                        "status": p.status,
                    }
                    for p in student_payments[:5]
                ],
                "extracted_entities": merged_entities,
            }

            gemini_res = GeminiService.generate_fallback_response(
                query=raw_query,
                verified_context=verified_context,
                intent=predicted_intent,
                confidence=confidence,
                lang=target_lang,
            )

            if gemini_res.get("success"):
                response_text = gemini_res["response"]
                fallback_used = True
                source = gemini_res.get("source", "gemini")
                gemini_succeeded = True
        except Exception as e:
            logger.warning(f"Error during Gemini fallback execution: {e}")

    # 9. Deterministic FeeService Resolution (Primary or graceful fallback)
    if not gemini_succeeded:
        requires_fee_record = predicted_intent in [
            "PENDING_FEE",
            "FEE_STRUCTURE",
            "PAYMENT_STATUS",
            "DUE_DATE",
            "SCHOLARSHIP",
            "INSTALLMENT",
        ]

        target_fee, disambig_prompt, disambig_options = FeeService.resolve_target_fee(
            db=db,
            user_id=current_user.id,
            entities=merged_entities,
            lang=target_lang,
        )

        if requires_fee_record and target_fee is None:
            # Either student has no records or multiple ambiguous records
            needs_clarification = disambig_options is not None
            options = disambig_options
            response_text = disambig_prompt
        else:
            # Route to deterministic FeeService handler based on predicted intent
            if predicted_intent == "PENDING_FEE":
                res = FeeService.handle_pending_fee(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "FEE_STRUCTURE":
                res = FeeService.handle_fee_structure(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "PAYMENT_STATUS":
                res = FeeService.handle_payment_status(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "PAYMENT_HISTORY":
                res = FeeService.handle_payment_history(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "DUE_DATE":
                res = FeeService.handle_due_date(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "SCHOLARSHIP":
                res = FeeService.handle_scholarship(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "INSTALLMENT":
                res = FeeService.handle_installment(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "REFUND":
                res = FeeService.handle_refund(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            elif predicted_intent == "RECEIPT":
                res = FeeService.handle_receipt(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

            else:  # OTHER_FEE_QUERY or fallback
                res = FeeService.handle_other_fee_query(db, current_user.id, merged_entities, target_fee, lang=target_lang)
                response_text = res["message"]
                fee_data = res

    # 10. Persist Messages in PostgreSQL
    ConversationService.save_message(
        db=db,
        conversation_id=conv.id,
        role="user",
        message=raw_query,
        intent=predicted_intent,
        confidence=confidence,
    )

    ConversationService.save_message(
        db=db,
        conversation_id=conv.id,
        role="assistant",
        message=response_text,
        intent=predicted_intent,
        confidence=confidence,
    )

    # 11. Return Structured Response
    return ChatResponse(
        message=response_text,
        intent=predicted_intent,
        confidence=confidence,
        detected_language=target_lang,
        entities=merged_entities,
        session_id=session_id,
        needs_clarification=needs_clarification,
        options=options,
        fee_data=fee_data,
        fallback_used=fallback_used,
        source=source,
    )


@router.get("/history", response_model=List[MessageOut], summary="Get chat history for a session")
async def get_chat_history(
    session_id: str = Query(..., description="Session identifier"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve message history for an authenticated student's session."""
    conv = ConversationService.get_or_create_conversation(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
    )
    return ConversationService.get_recent_messages(db, conv.id, limit=50)
