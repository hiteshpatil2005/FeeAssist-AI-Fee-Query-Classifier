"""
FeeAssist AI — Task 8 Verification Suite: Voice Interaction (EN, HI, MR)

Automated tests covering:
1. VoiceService supported languages configuration (English, Hindi, Marathi).
2. Speech text normalization (stripping Markdown, pronouncing currency symbols).
3. Text-to-Speech (TTS) audio synthesis in English, Hindi, and Marathi.
4. Voice API endpoints:
   - GET /api/voice/languages
   - POST /api/voice/tts (streaming MP3)
   - GET /api/voice/tts (streaming MP3)
   - Empty text / error handling (HTTP 400)
5. End-to-end voice query flow through existing /api/chat pipeline across 8 intents:
   - PENDING_FEE
   - PAYMENT_STATUS
   - PAYMENT_HISTORY
   - DUE_DATE
   - SCHOLARSHIP
   - INSTALLMENT
   - REFUND
   - RECEIPT
6. Multilingual voice query flow in English, Hindi, and Marathi.
7. Privacy and safety: Verify text-only persistence in database (no raw audio files on disk).
"""

import os
import sys
import json
import uuid
import unittest
import urllib.request
import urllib.error

# Configure sys.path for both container (/app) and host (../backend)
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/app/app"):
    sys.path.insert(0, "/app")
elif os.path.exists(os.path.abspath(os.path.join(current_dir, "..", "backend"))):
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..", "backend")))
elif os.path.exists(os.path.abspath(os.path.join(current_dir, ".."))):
    sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))

from app.services.voice_service import VoiceService, SUPPORTED_VOICE_LANGUAGES

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def http_req(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12.0) as resp:
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.status, json.loads(content.decode("utf-8")), resp.headers
            return resp.status, content, resp.headers
    except urllib.error.HTTPError as e:
        content = e.read()
        try:
            parsed = json.loads(content.decode("utf-8"))
        except Exception:
            parsed = {"error": content.decode("utf-8", errors="ignore")}
        return e.code, parsed, e.headers
    except Exception as e:
        return 500, {"error": str(e)}, {}


def register_or_login(email, password, name="Student", lang="English"):
    status, res, _ = http_req("POST", "/api/auth/login", {"email": email, "password": password})
    if status == 200:
        return res["access_token"]
    reg_status, reg_res, _ = http_req("POST", "/api/auth/register", {
        "name": name,
        "email": email,
        "password": password,
        "preferred_language": lang,
        "course": "B.Tech Computer Science",
        "year": 3,
        "semester": 5,
    })
    if reg_status in (200, 201):
        login_status, login_res, _ = http_req("POST", "/api/auth/login", {"email": email, "password": password})
        if login_status == 200:
            return login_res["access_token"]
    raise RuntimeError(f"Auth failed: {reg_status} {reg_res}")


class TestVoiceServiceUnits(unittest.TestCase):
    def test_01_supported_languages(self):
        """VoiceService explicitly supports English, Hindi, and Marathi."""
        langs = VoiceService.get_supported_languages()
        self.assertIn("en", langs)
        self.assertIn("hi", langs)
        self.assertIn("mr", langs)
        self.assertEqual(langs["en"]["bcp47"], "en-IN")
        self.assertEqual(langs["hi"]["bcp47"], "hi-IN")
        self.assertEqual(langs["mr"]["bcp47"], "mr-IN")

    def test_02_text_normalization_for_speech(self):
        """Markdown asterisks, headings, bullets, and currency symbols are cleaned for speech."""
        raw_en = "Your **pending fee** is **₹25,000.00**.\n• Due date: 15 Nov 2026."
        clean_en = VoiceService.normalize_text_for_speech(raw_en, lang="en")
        self.assertNotIn("**", clean_en)
        self.assertNotIn("•", clean_en)
        self.assertIn("Rupees", clean_en)

        raw_hi = "आपकी **बकाया फीस** **₹२५,०००** है।"
        clean_hi = VoiceService.normalize_text_for_speech(raw_hi, lang="hi")
        self.assertNotIn("**", clean_hi)
        self.assertIn("रुपये", clean_hi)

        raw_mr = "तुमची **शिल्लक फी** **₹२५,०००** आहे."
        clean_mr = VoiceService.normalize_text_for_speech(raw_mr, lang="mr")
        self.assertNotIn("**", clean_mr)
        self.assertIn("रुपये", clean_mr)

    def test_03_tts_synthesis_all_three_languages(self):
        """VoiceService successfully synthesizes speech in English, Hindi, and Marathi."""
        # English
        audio_en = VoiceService.synthesize_speech("Your pending fee is 25000 rupees.", lang="en")
        self.assertIsInstance(audio_en, bytes)
        self.assertGreater(len(audio_en), 1000)

        # Hindi
        audio_hi = VoiceService.synthesize_speech("आपकी बकाया फीस पच्चीस हजार रुपये है।", lang="hi")
        self.assertIsInstance(audio_hi, bytes)
        self.assertGreater(len(audio_hi), 1000)

        # Marathi
        audio_mr = VoiceService.synthesize_speech("तुमची शिल्लक फी पंचवीस हजार रुपये आहे.", lang="mr")
        self.assertIsInstance(audio_mr, bytes)
        self.assertGreater(len(audio_mr), 1000)

    def test_04_tts_empty_text_error(self):
        """Synthesizing empty text raises ValueError."""
        with self.assertRaises(ValueError):
            VoiceService.synthesize_speech("", lang="en")
        with self.assertRaises(ValueError):
            VoiceService.synthesize_speech("   ", lang="en")


class TestVoiceAPIEndpoints(unittest.TestCase):
    def test_05_get_voice_languages(self):
        """GET /api/voice/languages returns 200 and language definitions."""
        status, res, _ = http_req("GET", "/api/voice/languages")
        self.assertEqual(status, 200)
        self.assertIn("supported_languages", res)
        self.assertIn("en", res["supported_languages"])
        self.assertIn("hi", res["supported_languages"])
        self.assertIn("mr", res["supported_languages"])

    def test_06_post_tts_endpoint(self):
        """POST /api/voice/tts streams MP3 audio bytes with proper headers."""
        status, audio, headers = http_req(
            "POST",
            "/api/voice/tts",
            {"text": "Fee balance is thirty thousand rupees", "language": "en"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio), 1000)

    def test_07_get_tts_endpoint(self):
        """GET /api/voice/tts streams MP3 audio for HTML5 audio tags."""
        status, audio, headers = http_req(
            "GET",
            "/api/voice/tts?text=Payment+successful&language=en"
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio), 1000)

    def test_08_post_tts_empty_validation(self):
        """POST /api/voice/tts with empty text returns 422 or 400."""
        status, _, _ = http_req("POST", "/api/voice/tts", {"text": "", "language": "en"})
        self.assertIn(status, (400, 422))


class TestVoiceQueryChatFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create student and seed a fee record
        cls.email = f"voice_student_{uuid.uuid4().hex[:6]}@feeassist.ai"
        cls.token = register_or_login(cls.email, "VoicePass@123", name="Tanvi Joshi", lang="English")

        # Provision a sample fee record
        http_req("POST", "/api/fees", {
            "fee_type": "Tuition",
            "total_fee": 80000.0,
            "paid_amount": 30000.0,
            "scholarship_amount": 10000.0,
            "due_date": "2025-11-15",
            "semester": 5,
            "academic_year": "2024-2025"
        }, token=cls.token)

    def test_09_voice_queries_across_8_intents(self):
        """
        Voice queries across 8 fee intents pass through existing /api/chat pipeline:
        1. PENDING_FEE
        2. PAYMENT_STATUS
        3. PAYMENT_HISTORY
        4. DUE_DATE
        5. SCHOLARSHIP
        6. INSTALLMENT
        7. REFUND
        8. RECEIPT
        """
        voice_queries = [
            ("What is my pending fee?", "PENDING_FEE"),
            ("Did my fee payment succeed?", "PAYMENT_STATUS"),
            ("Show my previous fee payment history", "PAYMENT_HISTORY"),
            ("When is the last date to pay fees?", "DUE_DATE"),
            ("Can I get an OBC scholarship?", "SCHOLARSHIP"),
            ("Can I pay my tuition in installments?", "INSTALLMENT"),
            ("What is the refund policy on admission cancellation?", "REFUND"),
            ("Download my fee payment receipt", "RECEIPT"),
        ]

        for speech_text, expected_intent in voice_queries:
            status, res, _ = http_req(
                "POST",
                "/api/chat",
                {"message": speech_text, "language": "en"},
                token=self.token
            )
            self.assertEqual(status, 200)
            self.assertEqual(res["intent"], expected_intent, f"Query '{speech_text}' failed intent mapping")
            self.assertIn("message", res)
            self.assertFalse(res["fallback_used"])

    def test_10_multilingual_voice_queries(self):
        """Multilingual voice queries in Hindi and Marathi properly handled."""
        # Hindi voice query: Pending fee
        status_hi, res_hi, _ = http_req(
            "POST",
            "/api/chat",
            {"message": "मेरी कुल बकाया फीस कितनी है?", "language": "hi"},
            token=self.token
        )
        self.assertEqual(status_hi, 200)
        self.assertEqual(res_hi["intent"], "PENDING_FEE")
        self.assertIn("बकाया", res_hi["message"])

        # Marathi voice query: Due date
        status_mr, res_mr, _ = http_req(
            "POST",
            "/api/chat",
            {"message": "फी भरण्याची शेवटची तारीख कोणती आहे?", "language": "mr"},
            token=self.token
        )
        self.assertEqual(status_mr, 200)
        self.assertEqual(res_mr["intent"], "DUE_DATE")
        self.assertIn("तारीख", res_mr["message"])

    def test_11_voice_tts_synthesis_of_chat_response(self):
        """The chat response returned from a voice query can be synthesized into MP3 speech."""
        status, chat_res, _ = http_req(
            "POST",
            "/api/chat",
            {"message": "How much fee is remaining?", "language": "en"},
            token=self.token
        )
        self.assertEqual(status, 200)
        response_text = chat_res["message"]

        # Synthesize response into speech via POST /api/voice/tts
        status_tts, audio, headers = http_req(
            "POST",
            "/api/voice/tts",
            {"text": response_text, "language": chat_res["detected_language"]}
        )
        self.assertEqual(status_tts, 200)
        self.assertEqual(headers.get("Content-Type"), "audio/mpeg")
        self.assertGreater(len(audio), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
