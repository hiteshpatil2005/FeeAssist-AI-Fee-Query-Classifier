"""
FeeAssist AI — Controlled Gemini Fallback Service

Integrates Google Gemini API as a controlled secondary fallback for
low-confidence (< NLP_CONFIDENCE_THRESHOLD) or complex fee-related queries.

Strict Constraints:
1. Server-side only: GEMINI_API_KEY is never exposed to frontend code.
2. Grounded Context: Gemini only receives verified student fee/payment facts.
3. Financial Safety: Gemini must NEVER invent financial figures or dates.
4. Domain Limitation: Strictly declines out-of-domain queries (e.g. poetry, jokes).
5. Graceful Degradation: Handles missing keys, timeouts, and rate limits cleanly.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

from app.config import settings

logger = logging.getLogger("feeassist.gemini")

# Non-fee domain patterns for fast boundary protection
OUT_OF_DOMAIN_KEYWORDS = [
    "poem", "poetry", "कविता", "शायरी", "joke", "chutkula", "चुटकुला", "विनोद", "जोक",
    "essay", "story", "कहानी", "गोष्ट", "song", "गाना", "गाणे",
    "recipe", "cooking", "capital of", "president of", "weather", "मौसम", "हवामान",
    "movie", "cricket score", "write code", "python script", "translate"
]


class GeminiService:
    @staticmethod
    def is_out_of_domain(text: str) -> bool:
        """Checks if the query is clearly outside the college fee domain using Unicode-aware boundaries."""
        import re
        low = text.lower()
        for k in OUT_OF_DOMAIN_KEYWORDS:
            # Unicode boundary check works for both Latin and Devanagari while preventing 'story' in 'history'
            pattern = r'(?:^|[\s\W])' + re.escape(k) + r'(?:[\s\W]|$)'
            if re.search(pattern, low):
                return True
        return False

    @staticmethod
    def get_out_of_domain_refusal(lang: str = "en") -> str:
        """Returns a polite domain limitation refusal in the target language."""
        if lang == "mr":
            return (
                "मी **FeeAssist AI** आहे — केवळ महाविद्यालयीन फी, शिल्लक रक्कम, देय तारखा, "
                "शिष्यवृत्ती आणि हप्ता योजना यासंबंधी मदत करण्यासाठी डिझाइन केलेला सहाय्यक आहे.\n\n"
                "कृपया कॉलेजच्या फी विषयी प्रश्न विचारा."
            )
        elif lang == "hi":
            return (
                "मैं **FeeAssist AI** हूँ — केवल कॉलेज फीस, बकाया राशि, अंतिम तिथि, "
                "छात्रवृत्ति और किस्त विकल्पों में सहायता के लिए बनाया गया विशेष सहायक।\n\n"
                "कृपया कॉलेज फीस से संबंधित प्रश्न पूछें।"
            )
        return (
            "I am **FeeAssist AI** — a dedicated assistant designed specifically for college fee inquiries, "
            "payment records, scholarships, and installment options.\n\n"
            "Please ask a fee-related question to proceed."
        )

    @classmethod
    def generate_fallback_response(
        cls,
        query: str,
        verified_context: Dict[str, Any],
        intent: Optional[str] = None,
        confidence: Optional[float] = None,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """
        Calls Gemini API with grounded context for low-confidence or complex queries.

        Returns a structured dictionary:
        {
            "success": bool,
            "response": str,
            "fallback_used": bool,
            "source": "gemini" | "domain_guardrail" | "fallback",
            "error_category": Optional[str]
        }
        """
        # 1. Domain Boundary Check
        if cls.is_out_of_domain(query):
            logger.info(
                f"[Gemini Fallback] Out-of-domain query intercepted | Intent: {intent} | Conf: {confidence}"
            )
            return {
                "success": True,
                "response": cls.get_out_of_domain_refusal(lang),
                "fallback_used": True,
                "source": "domain_guardrail",
                "error_category": None,
            }

        # 2. Check API Key
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.startswith("AQ.Ab8RN6JC19rfznfZG-ZkYiNcGPfz3AMBmAZDdfgfescWuIhFgQ"):
            # If default placeholder or missing
            logger.warning("[Gemini Fallback] Valid GEMINI_API_KEY not configured. Falling back to FeeService.")
            return {
                "success": False,
                "response": "",
                "fallback_used": False,
                "source": "fallback",
                "error_category": "MISSING_OR_PLACEHOLDER_KEY",
            }

        # 3. Construct Grounded Context Prompt
        lang_names = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
        target_lang_name = lang_names.get(lang, "English")

        system_instruction = (
            "You are FeeAssist AI, an official college fee assistant.\n\n"
            "CRITICAL SAFETY RULES:\n"
            "1. You must ONLY state financial facts explicitly present in the VERIFIED STUDENT DATA below.\n"
            "2. NEVER invent, hallucinate, or estimate fee balances, paid amounts, due dates, scholarship discounts, or transaction IDs.\n"
            "3. If the requested information is absent from the verified data, clearly say it is not available in official student records and recommend checking the college accounts section.\n"
            "4. Keep answers concise, factual, and strictly relevant to student fees.\n"
            f"5. Answer in {target_lang_name} ({lang}) using natural, native phrasing."
        )

        verified_data_str = json.dumps(verified_context, indent=2, ensure_ascii=False)

        prompt_payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{system_instruction}\n\n"
                                f"=== VERIFIED STUDENT DATA ===\n"
                                f"{verified_data_str}\n\n"
                                f"=== STUDENT QUERY ===\n"
                                f"{query}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for strict factual adherence
                "maxOutputTokens": 800,
            }
        }

        # 4. Invoke Google Generative Language API
        model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(prompt_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        answer = parts[0]["text"].strip()
                        logger.info(
                            f"[Gemini Fallback] Success | Intent: {intent} | Conf: {confidence} | Lang: {lang}"
                        )
                        return {
                            "success": True,
                            "response": answer,
                            "fallback_used": True,
                            "source": "gemini",
                            "error_category": None,
                        }

                logger.warning("[Gemini Fallback] Empty or malformed response structure from Gemini API.")
                return {
                    "success": False,
                    "response": "",
                    "fallback_used": False,
                    "source": "fallback",
                    "error_category": "UNEXPECTED_RESPONSE_STRUCTURE",
                }

        except urllib.error.HTTPError as e:
            cat = "RATE_LIMIT" if e.code == 429 else ("AUTH_ERROR" if e.code in (401, 403) else f"HTTP_{e.code}")
            logger.error(f"[Gemini Fallback] HTTP error: {e.code} ({cat})")
            return {
                "success": False,
                "response": "",
                "fallback_used": False,
                "source": "fallback",
                "error_category": cat,
            }

        except (urllib.error.URLError, TimeoutError) as e:
            logger.error(f"[Gemini Fallback] Network / Timeout error: {e}")
            return {
                "success": False,
                "response": "",
                "fallback_used": False,
                "source": "fallback",
                "error_category": "TIMEOUT_OR_NETWORK",
            }

        except Exception as e:
            logger.error(f"[Gemini Fallback] Unexpected error: {type(e).__name__}")
            return {
                "success": False,
                "response": "",
                "fallback_used": False,
                "source": "fallback",
                "error_category": "INTERNAL_EXCEPTION",
            }
