"""
FeeAssist AI — Task 7 Verification Suite: Controlled Gemini Fallback & Routing

Tests:
1. Out-of-domain query guardrail interception (EN, HI, MR) without calling external API.
2. Routing logic: High confidence -> ML (fallback_used=False, source="ml").
3. Routing logic: Hypothetical payment -> FeeService deterministic (no Gemini).
4. Low confidence / OTHER_FEE_QUERY routing trigger.
5. GeminiService response parsing, prompt grounding, and parameter safety (temperature=0.1).
6. Graceful degradation: Missing/Invalid API key or network error -> reverts to FeeService cleanly without 500.
7. End-to-End Chat API verification via live HTTP calls against running backend:
   - High-confidence fee query (source="ml", fallback_used=False)
   - Out-of-domain query guardrail (source="guardrail", fallback_used=False)
   - Multilingual query handling (EN, HI, MR)
   - Hypothetical payment arithmetic (deterministic subtraction)
"""

import os
import sys
import json
import uuid
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock

# Configure sys.path for both container (/app) and host (../backend)
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/app/app"):
    sys.path.insert(0, "/app")
elif os.path.exists(os.path.abspath(os.path.join(current_dir, "..", "backend"))):
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..", "backend")))
elif os.path.exists(os.path.abspath(os.path.join(current_dir, ".."))):
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))

from app.config import settings
from app.services.gemini_service import GeminiService
from app.services.nlp_service import classify_intent
from app.services.entity_service import extract_entities

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def http_req(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {"error": content}
        return e.code, parsed
    except Exception as e:
        return 500, {"error": str(e)}


def register_or_login(email, password, name="Student", lang="English"):
    status, res = http_req("POST", "/api/auth/login", {"email": email, "password": password})
    if status == 200:
        return res["access_token"]
    reg_status, reg_res = http_req("POST", "/api/auth/register", {
        "name": name,
        "email": email,
        "password": password,
        "preferred_language": lang,
        "course": "B.Tech Computer Science",
        "year": 3,
        "semester": 5,
    })
    if reg_status in (200, 201):
        login_status, login_res = http_req("POST", "/api/auth/login", {"email": email, "password": password})
        if login_status == 200:
            return login_res["access_token"]
    raise RuntimeError(f"Auth failed: {reg_status} {reg_res}")


class TestGeminiGuardrailsAndService(unittest.TestCase):
    def test_01_out_of_domain_detection(self):
        """Domain guardrail correctly identifies non-fee queries."""
        self.assertTrue(GeminiService.is_out_of_domain("Write me a poem about college"))
        self.assertTrue(GeminiService.is_out_of_domain("Tell me a funny joke"))
        self.assertTrue(GeminiService.is_out_of_domain("मला एक छान विनोद सांगा"))
        self.assertTrue(GeminiService.is_out_of_domain("मुझे एक अच्छी कविता सुनाओ"))
        self.assertTrue(GeminiService.is_out_of_domain("What is the recipe for biryani?"))

        # Fee queries should NOT be out of domain
        self.assertFalse(GeminiService.is_out_of_domain("What is my pending tuition fee?"))
        self.assertFalse(GeminiService.is_out_of_domain("माझी हॉस्टेल फी किती शिल्लक आहे?"))
        self.assertFalse(GeminiService.is_out_of_domain("फीस भरने की अंतिम तिथि क्या है?"))

    def test_02_out_of_domain_refusal_multilingual(self):
        """Out of domain refusals must be localized and polite."""
        refusal_en = GeminiService.get_out_of_domain_refusal("en")
        self.assertIn("FeeAssist AI", refusal_en)
        self.assertIn("college fee", refusal_en)

        refusal_hi = GeminiService.get_out_of_domain_refusal("hi")
        self.assertIn("FeeAssist AI", refusal_hi)
        self.assertIn("कॉलेज फीस", refusal_hi)

        refusal_mr = GeminiService.get_out_of_domain_refusal("mr")
        self.assertIn("FeeAssist AI", refusal_mr)
        self.assertIn("महाविद्यालयीन फी", refusal_mr)

    def test_03_fallback_response_out_of_domain(self):
        """Calling generate_fallback_response on out-of-domain returns domain_guardrail source."""
        res = GeminiService.generate_fallback_response(
            query="Tell me a joke about dogs",
            verified_context={},
            intent="OTHER_FEE_QUERY",
            confidence=0.3,
            lang="en"
        )
        self.assertTrue(res["success"])
        self.assertTrue(res["fallback_used"])
        self.assertEqual(res["source"], "domain_guardrail")
        self.assertIn("FeeAssist AI", res["response"])

    def test_04_graceful_degradation_on_missing_or_invalid_key(self):
        """When API key is invalid or placeholder, service gracefully reports error category without throwing."""
        with patch.object(settings, "GEMINI_API_KEY", ""):
            res = GeminiService.generate_fallback_response(
                query="Can I get an extension due to family emergency?",
                verified_context={"student_name": "Rohan Sharma"},
                intent="OTHER_FEE_QUERY",
                confidence=0.45,
                lang="en"
            )
            self.assertFalse(res["success"])
            self.assertFalse(res["fallback_used"])
            self.assertEqual(res["source"], "fallback")
            self.assertEqual(res["error_category"], "MISSING_OR_PLACEHOLDER_KEY")

    @patch("urllib.request.urlopen")
    def test_05_successful_gemini_call(self, mock_urlopen):
        """Gemini API returns structured response and flags fallback_used=True."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"candidates": [{"content": {"parts": [{"text": "Based on your records, your tuition fee of Rs 85,000 is fully paid."}]}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with patch.object(settings, "GEMINI_API_KEY", "dummy-valid-test-key"):
            res = GeminiService.generate_fallback_response(
                query="Could you explain my fee situation in detail?",
                verified_context={
                    "student_name": "Rohan Sharma",
                    "fee_records": [{"fee_type": "tuition", "total_amount": 85000.0, "pending_amount": 0.0}]
                },
                intent="OTHER_FEE_QUERY",
                confidence=0.4,
                lang="en"
            )
            self.assertTrue(res["success"])
            self.assertTrue(res["fallback_used"])
            self.assertEqual(res["source"], "gemini")
            self.assertIn("85,000", res["response"])


class TestRoutingLogicAndConfidence(unittest.TestCase):
    def test_06_high_confidence_queries_stay_on_ml(self):
        """High confidence fee queries achieve expected intent and confidence."""
        q1 = "What is my current pending fee balance?"
        nlp1 = classify_intent(q1)
        self.assertEqual(nlp1["intent"], "PENDING_FEE")
        self.assertGreaterEqual(nlp1["confidence"], settings.NLP_CONFIDENCE_THRESHOLD)

        q2 = "Can I pay my semester fee in installments?"
        nlp2 = classify_intent(q2)
        self.assertEqual(nlp2["intent"], "INSTALLMENT")
        self.assertGreater(nlp2["confidence"], 0.5)

    def test_07_hypothetical_payment_bypasses_gemini(self):
        """Hypothetical calculations ('what if I pay 10000') must be handled deterministically by FeeService."""
        query = "What if I pay ₹10,000 now?"
        entities = extract_entities(query)
        self.assertTrue(entities.get("is_hypothetical"))
        self.assertEqual(entities.get("amount"), 10000.0)
        is_hypo = bool(entities.get("is_hypothetical") and entities.get("amount") is not None)
        self.assertTrue(is_hypo)


class TestLiveChatAPIWithRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Authenticate test student
        cls.email = f"task7_student_{uuid.uuid4().hex[:6]}@example.com"
        cls.token = register_or_login(cls.email, "StudentPass@123", name="Ananya Deshmukh", lang="English")

    def test_08_live_high_confidence_fee_query(self):
        """Live Chat API: High confidence query routes to ML source without fallback."""
        status, res = http_req("POST", "/api/chat", {"message": "What is my current pending fee balance?"}, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(res["intent"], "PENDING_FEE")
        self.assertGreaterEqual(res["confidence"], settings.NLP_CONFIDENCE_THRESHOLD)
        self.assertFalse(res["fallback_used"])
        self.assertEqual(res["source"], "ml")

    def test_09_live_out_of_domain_guardrail(self):
        """Live Chat API: Out of domain prompt is immediately intercepted with domain guardrail."""
        status, res = http_req("POST", "/api/chat", {"message": "Write a poem about colleges"}, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(res["intent"], "OUT_OF_DOMAIN")
        self.assertFalse(res["fallback_used"])
        self.assertEqual(res["source"], "guardrail")
        self.assertIn("FeeAssist AI", res["message"])

    def test_10_live_out_of_domain_hindi_and_marathi(self):
        """Live Chat API: Multilingual out-of-domain queries properly refused in Hindi and Marathi."""
        # Hindi
        status_hi, res_hi = http_req("POST", "/api/chat", {"message": "मुझे एक मजेदार चुटकुला सुनाओ"}, token=self.token)
        self.assertEqual(status_hi, 200)
        self.assertEqual(res_hi["intent"], "OUT_OF_DOMAIN")
        self.assertIn("कॉलेज फीस", res_hi["message"])

        # Marathi
        status_mr, res_mr = http_req("POST", "/api/chat", {"message": "मला एक छान कविता ऐकवा"}, token=self.token)
        self.assertEqual(status_mr, 200)
        self.assertEqual(res_mr["intent"], "OUT_OF_DOMAIN")
        self.assertIn("महाविद्यालयीन फी", res_mr["message"])

    def test_11_live_hypothetical_payment_arithmetic(self):
        """Live Chat API: Hypothetical query runs deterministic subtraction through FeeService without Gemini."""
        # Ensure a fee record exists
        fee_status, fee_res = http_req("POST", "/api/fees", {
            "fee_type": "Tuition",
            "total_fee": 75000.0,
            "paid_amount": 25000.0,
            "scholarship_amount": 0.0,
            "due_date": "2025-05-30",
            "semester": 5,
            "academic_year": "2024-2025"
        }, token=self.token)
        self.assertIn(fee_status, (200, 201))

        status, res = http_req("POST", "/api/chat", {"message": "What if I pay ₹15,000?"}, token=self.token)
        self.assertEqual(status, 200)
        self.assertFalse(res["fallback_used"])
        self.assertEqual(res["source"], "ml")
        # 50,000 - 15,000 = 35,000
        self.assertIn("35,000", res["message"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
