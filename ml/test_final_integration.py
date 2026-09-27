"""
FeeAssist AI — Master Integration, Security, Financial, and Workflow Verification Suite

Covers Tasks 1 through 9:
1. Authentication & JWT Security (Register, Login, Password Hashing, Signature Tampering, Protected Endpoints)
2. Strict User Isolation & Authorization (Student A vs Student B data protection, no arbitrary user_id)
3. Input Validation & Safe Error Responses (Invalid formats, negative amounts, structured JSON errors)
4. Gemini API Key Confidentiality (Key never exposed to client/responses)
5. Deterministic Fee Calculations (Remaining Fee = Total - Paid - Scholarship across edge cases, payments, & summaries)
6. Multilingual Intent Classification (EN, HI, MR across fee intents)
7. Entity Extraction & Contextual Multi-Turn Conversation
8. Controlled Gemini Fallback & Domain Guardrails (Out-of-domain refusals in EN, HI, MR)
9. Multilingual Voice Interaction (STT schemas, TTS synthesis in EN, HI, MR)
"""

import os
import sys
import json
import uuid
import unittest
import urllib.request
import urllib.error

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8001")


def http_req(method: str, path: str, data: dict = None, token: str = None):
    url = f"{API_BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8")), resp.headers
            return resp.status, raw, resp.headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode("utf-8")), e.headers
        except Exception:
            return e.code, raw.decode("utf-8", errors="replace"), e.headers


class TestCompleteWorkflowAndSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.student_a_email = f"student_a_{uuid.uuid4().hex[:6]}@feeassist.ai"
        cls.student_b_email = f"student_b_{uuid.uuid4().hex[:6]}@feeassist.ai"
        cls.password = "SecurePass@2026"

        # Register Student A
        status_a, res_a, _ = http_req("POST", "/api/auth/register", {
            "email": cls.student_a_email,
            "password": cls.password,
            "name": "Aarav Sharma",
            "preferred_language": "English"
        })
        assert status_a == 201, f"Failed to register Student A: {res_a}"
        cls.user_a_id = res_a["id"]

        # Login Student A
        status_la, res_la, _ = http_req("POST", "/api/auth/login", {
            "email": cls.student_a_email,
            "password": cls.password
        })
        assert status_la == 200, f"Failed to login Student A: {res_la}"
        cls.token_a = res_la["access_token"]

        # Register Student B
        status_b, res_b, _ = http_req("POST", "/api/auth/register", {
            "email": cls.student_b_email,
            "password": cls.password,
            "name": "Priya Patil",
            "preferred_language": "Marathi"
        })
        assert status_b == 201, f"Failed to register Student B: {res_b}"
        cls.user_b_id = res_b["id"]

        # Login Student B
        status_lb, res_lb, _ = http_req("POST", "/api/auth/login", {
            "email": cls.student_b_email,
            "password": cls.password
        })
        assert status_lb == 200, f"Failed to login Student B: {res_lb}"
        cls.token_b = res_lb["access_token"]

    # ──────────────────────────────────────────────────────────────────────────
    # 1. SECURITY & AUTHENTICATION TESTING
    # ──────────────────────────────────────────────────────────────────────────

    def test_01_login_jwt_authentication(self):
        """User can login and receive a valid JWT token."""
        status, res, _ = http_req("POST", "/api/auth/login", {
            "email": self.student_a_email,
            "password": self.password
        })
        self.assertEqual(status, 200)
        self.assertIn("access_token", res)
        self.assertEqual(res["token_type"], "bearer")

        # Verify token against /api/auth/me
        status_me, me, _ = http_req("GET", "/api/auth/me", token=res["access_token"])
        self.assertEqual(status_me, 200)
        self.assertEqual(me["email"], self.student_a_email)

    def test_02_login_invalid_password(self):
        """Invalid credentials return 401 Unauthorized without exposing server details."""
        status, res, _ = http_req("POST", "/api/auth/login", {
            "email": self.student_a_email,
            "password": "WrongPassword123"
        })
        self.assertEqual(status, 401)
        self.assertIn("detail", res)

    def test_03_protected_endpoints_reject_unauthenticated(self):
        """Protected APIs strictly reject unauthenticated requests with 401."""
        protected_endpoints = [
            ("GET", "/api/fees"),
            ("POST", "/api/fees"),
            ("GET", "/api/payments"),
            ("POST", "/api/payments"),
            ("POST", "/api/chat"),
            ("GET", "/api/chat/history"),
            ("GET", "/api/auth/me")
        ]
        for method, endpoint in protected_endpoints:
            status, _, _ = http_req(method, endpoint)
            self.assertEqual(status, 401, f"Endpoint {endpoint} allowed unauthenticated access!")

    def test_04_tampered_jwt_rejected(self):
        """Altered or forged JWT tokens are rejected with 401."""
        tampered_token = self.token_a[:-5] + "XXXXX"
        status, _, _ = http_req("GET", "/api/fees", token=tampered_token)
        self.assertEqual(status, 401)

    def test_05_gemini_api_key_protection(self):
        """Gemini API key is NEVER exposed in any client-facing API responses."""
        endpoints_to_inspect = [
            ("GET", "/api/auth/me", self.token_a),
            ("GET", "/api/fees", self.token_a),
            ("GET", "/api/voice/languages", None),
            ("POST", "/api/chat", self.token_a, {"message": "Hello", "language": "en"}),
        ]
        forbidden_keywords = ["AQ.Ab8RN6JC", "GEMINI_API_KEY", "feeassist_secret_pass"]
        for item in endpoints_to_inspect:
            method, ep, tok = item[0], item[1], item[2]
            body = item[3] if len(item) > 3 else None
            status, res, _ = http_req(method, ep, data=body, token=tok)
            res_str = json.dumps(res) if isinstance(res, (dict, list)) else str(res)
            for kw in forbidden_keywords:
                self.assertNotIn(kw, res_str, f"Secret keyword {kw} leaked in {ep} response!")

    def test_06_student_data_isolation(self):
        """Student A CANNOT access, update, or delete Student B's fee or payment records."""
        # Create a fee record under Student B
        status, fee_b, _ = http_req("POST", "/api/fees", {
            "fee_type": "Exam Fee",
            "total_fee": 5000.0,
            "paid_amount": 5000.0,
            "scholarship_amount": 0.0,
            "due_date": "2025-12-01",
            "semester": 4,
            "academic_year": "2024-2025"
        }, token=self.token_b)
        self.assertEqual(status, 201)
        fee_b_id = fee_b["id"]

        # Student A attempts to GET Student B's fee
        status_get, _, _ = http_req("GET", f"/api/fees/{fee_b_id}", token=self.token_a)
        self.assertIn(status_get, (403, 404), "Student A accessed Student B's fee record!")

        # Student A attempts to UPDATE Student B's fee
        status_put, _, _ = http_req("PUT", f"/api/fees/{fee_b_id}", {
            "total_fee": 99999.0
        }, token=self.token_a)
        self.assertIn(status_put, (403, 404), "Student A modified Student B's fee record!")

        # Student A attempts to DELETE Student B's fee
        status_del, _, _ = http_req("DELETE", f"/api/fees/{fee_b_id}", token=self.token_a)
        self.assertIn(status_del, (403, 404), "Student A deleted Student B's fee record!")

    def test_07_input_validation_and_safe_errors(self):
        """Input validation enforces schemas and returns clean 422 JSON errors."""
        # Invalid email format
        status, res, _ = http_req("POST", "/api/auth/register", {
            "email": "not-an-email",
            "password": "ValidPassword123",
            "name": "Tester"
        })
        self.assertEqual(status, 422)

        # Empty chat message
        status_chat, _, _ = http_req("POST", "/api/chat", {"message": "", "language": "en"}, token=self.token_a)
        self.assertIn(status_chat, (400, 422))

    # ──────────────────────────────────────────────────────────────────────────
    # 2. DETERMINISTIC FEE CALCULATIONS & SUMMARY TESTING
    # ──────────────────────────────────────────────────────────────────────────

    def test_08_fee_calculation_formula_combinations(self):
        """
        Verify: Remaining Fee = Total Fee - Paid Amount - Scholarship Amount
        Tested combinations:
        - Case 1: Partial payment + Scholarship (100,000 - 40,000 - 10,000 = 50,000)
        - Case 2: Zero scholarship (80,000 - 30,000 - 0 = 50,000)
        - Case 3: Fully paid (50,000 - 50,000 - 0 = 0)
        - Case 4: 100% Scholarship (60,000 - 0 - 60,000 = 0)
        """
        cases = [
            ("Tuition Sem 5", 100000.0, 40000.0, 10000.0, 50000.0, 5),
            ("Tuition Sem 6", 80000.0, 30000.0, 0.0, 50000.0, 6),
            ("Hostel Fee", 50000.0, 50000.0, 0.0, 0.0, 5),
            ("Merit Scholarship", 60000.0, 0.0, 60000.0, 0.0, 6),
        ]

        created_fee_ids = []
        for name, total, paid, schol, expected_pending, sem in cases:
            status, fee, _ = http_req("POST", "/api/fees", {
                "fee_type": name,
                "total_fee": total,
                "paid_amount": paid,
                "scholarship_amount": schol,
                "due_date": "2025-11-30",
                "semester": sem,
                "academic_year": "2025-2026"
            }, token=self.token_a)
            self.assertEqual(status, 201)
            self.assertEqual(fee["pending_amount"], expected_pending)
            created_fee_ids.append(fee["id"])

        # Check Aggregated Summary Endpoint
        status_sum, summary, _ = http_req("GET", "/api/fees/summary", token=self.token_a)
        self.assertEqual(status_sum, 200)
        self.assertEqual(summary["total_fee"], 290000.0)
        self.assertEqual(summary["paid_amount"], 120000.0)
        self.assertEqual(summary["scholarship_amount"], 70000.0)
        self.assertEqual(summary["pending_amount"], 100000.0)

    def test_09_payment_record_updates_remaining_balance(self):
        """Posting a new payment updates the fee record and reduces remaining balance deterministically."""
        # Create a single fee record
        status, fee, _ = http_req("POST", "/api/fees", {
            "fee_type": "Lab Fee",
            "total_fee": 20000.0,
            "paid_amount": 0.0,
            "scholarship_amount": 0.0,
            "due_date": "2025-12-15",
            "semester": 7,
            "academic_year": "2025-2026"
        }, token=self.token_b)
        self.assertEqual(status, 201)
        fee_id = fee["id"]
        self.assertEqual(fee["pending_amount"], 20000.0)

        # Post payment transaction of 12,000
        status_pay, payment, _ = http_req("POST", "/api/payments", {
            "amount": 12000.0,
            "payment_method": "UPI",
            "fee_type": "Lab Fee",
            "status": "COMPLETED",
            "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}"
        }, token=self.token_b)
        self.assertEqual(status_pay, 201)

        # Update fee record with new paid amount (backend recalculates pending_amount)
        status_update, updated_fee, _ = http_req("PUT", f"/api/fees/{fee_id}", {
            "paid_amount": 12000.0
        }, token=self.token_b)
        self.assertEqual(status_update, 200)
        self.assertEqual(updated_fee["paid_amount"], 12000.0)
        self.assertEqual(updated_fee["pending_amount"], 8000.0)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. MULTILINGUAL INTENT CLASSIFICATION & CHAT TESTING
    # ──────────────────────────────────────────────────────────────────────────

    def test_10_multilingual_intent_classification(self):
        """English, Hindi, and Marathi queries consistently map to fee intents."""
        queries = [
            ("How much fee is pending?", "en", "PENDING_FEE"),
            ("माझी किती फी बाकी आहे?", "mr", "PENDING_FEE"),
            ("मेरी कुल कितनी फीस बाकी है?", "hi", "PENDING_FEE"),
            ("When is the fee due date?", "en", "DUE_DATE"),
            ("फी भरण्याची शेवटची तारीख काय आहे?", "mr", "DUE_DATE"),
            ("फीस भरने की अंतिम तिथि क्या है?", "hi", "DUE_DATE"),
            ("Can I pay fee in installments?", "en", "INSTALLMENT"),
            ("मी हप्त्यांमध्ये फी भरू शकतो का?", "mr", "INSTALLMENT"),
            ("Show my previous fee payment history", "en", "PAYMENT_HISTORY"),
            ("मला माझे मागील पेमेंट रेकॉर्ड दाखवा", "mr", "PAYMENT_HISTORY"),
        ]

        for text, lang, expected_intent in queries:
            status, res, _ = http_req("POST", "/api/chat", {"message": text, "language": lang}, token=self.token_a)
            self.assertEqual(status, 200)
            self.assertEqual(res["intent"], expected_intent, f"Query '{text}' failed expected intent {expected_intent}")
            self.assertIn("message", res)

    def test_11_entity_extraction_and_multi_turn_context(self):
        """Entity extraction identifies semester/amount and preserves multi-turn context."""
        # Query mentioning Semester 5
        status_1, res_1, _ = http_req("POST", "/api/chat", {
            "message": "What is the fee for Semester 5?",
            "language": "en"
        }, token=self.token_a)
        self.assertEqual(status_1, 200)
        self.assertIn("Semester 5", res_1["message"])

        # Follow-up query: "When is it due?" (Implicit context: Semester 5)
        status_2, res_2, _ = http_req("POST", "/api/chat", {
            "message": "When is it due?",
            "language": "en"
        }, token=self.token_a)
        self.assertEqual(status_2, 200)
        self.assertEqual(res_2["intent"], "DUE_DATE")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. CONTROLLED GEMINI FALLBACK & DOMAIN GUARDRAILS
    # ──────────────────────────────────────────────────────────────────────────

    def test_12_domain_guardrail_out_of_domain_refusal(self):
        """Out-of-domain queries (weather, jokes, coding) are politely refused in EN, HI, MR."""
        ood_queries = [
            ("What is the weather today in Pune?", "en", "feeassist ai"),
            ("मुझे एक मजेदार चुटकुला सुनाओ", "hi", "कॉलेज फीस"),
            ("मला एखादी छान कविता सांगा", "mr", "फी"),
        ]
        for query, lang, refusal_keyword in ood_queries:
            status, res, _ = http_req("POST", "/api/chat", {"message": query, "language": lang}, token=self.token_a)
            self.assertEqual(status, 200)
            self.assertIn(res["source"], ("guardrail", "domain_guardrail"))
            self.assertIn(refusal_keyword.lower(), res["message"].lower())

    def test_13_hypothetical_payment_arithmetic_stays_on_fee_service(self):
        """Hypothetical calculations ('what if I pay 10000') stay deterministic and bypass generative drift."""
        status, res, _ = http_req("POST", "/api/chat", {
            "message": "If I pay 20000 for Semester 5 now how much fee will remain?",
            "language": "en"
        }, token=self.token_a)
        self.assertEqual(status, 200)
        self.assertFalse(res["fallback_used"])
        self.assertIn("30,000", res["message"])  # Current 50,000 - 20,000 = 30,000

    # ──────────────────────────────────────────────────────────────────────────
    # 5. VOICE INTERACTION & SPEECH SYNTHESIS TESTING
    # ──────────────────────────────────────────────────────────────────────────

    def test_14_voice_languages_and_tts_synthesis(self):
        """Voice endpoints provide supported language metadata and stream MP3 bytes for EN, HI, MR."""
        # 1. Supported languages
        status_lang, res_lang, _ = http_req("GET", "/api/voice/languages")
        self.assertEqual(status_lang, 200)
        self.assertIn("en", res_lang["supported_languages"])
        self.assertIn("hi", res_lang["supported_languages"])
        self.assertIn("mr", res_lang["supported_languages"])

        # 2. TTS synthesis English
        status_tts_en, audio_en, hdrs_en = http_req("POST", "/api/voice/tts", {
            "text": "Your pending fee is 50,000 Rupees.",
            "language": "en"
        })
        self.assertEqual(status_tts_en, 200)
        self.assertEqual(hdrs_en.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio_en), 1000)

        # 3. TTS synthesis Hindi
        status_tts_hi, audio_hi, hdrs_hi = http_req("POST", "/api/voice/tts", {
            "text": "आपकी बकाया फीस पचास हजार रुपये है।",
            "language": "hi"
        })
        self.assertEqual(status_tts_hi, 200)
        self.assertEqual(hdrs_hi.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio_hi), 1000)

        # 4. TTS synthesis Marathi
        status_tts_mr, audio_mr, hdrs_mr = http_req("POST", "/api/voice/tts", {
            "text": "तुमची उर्वरित फी पन्नास हजार रुपये आहे.",
            "language": "mr"
        })
        self.assertEqual(status_tts_mr, 200)
        self.assertEqual(hdrs_mr.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio_mr), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
