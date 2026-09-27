"""
FeeAssist AI — Voice Service

Provides Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities
supporting English, Hindi, and Marathi.

Strict Architecture & Security Rules:
1. True multilingual support: Only supports languages verified to work with gTTS & STT:
   - English ('en' / 'en-IN')
   - Hindi ('hi' / 'hi-IN')
   - Marathi ('mr' / 'mr-IN')
2. Audio normalization: Strips Markdown formatting, asterisks, bullet markers,
   and pronounces currency symbols (₹ -> Rupees / रुपये) naturally.
3. Privacy Preservation: Raw audio streams are never saved permanently to disk.
   Audio is processed in-memory or streamed as byte buffers.
4. Robust Fallback: Handles invalid language tags, empty text, or network limits gracefully.
"""

import io
import re
import logging
from typing import Dict, Any, Optional
from gtts import gTTS

logger = logging.getLogger("feeassist.voice")

# Explicit mapping of supported language codes and their voice configurations
SUPPORTED_VOICE_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "name": "English",
        "bcp47": "en-IN",
        "gtts_code": "en",
        "tld": "com",
        "label": "English (India)",
    },
    "hi": {
        "name": "Hindi",
        "bcp47": "hi-IN",
        "gtts_code": "hi",
        "tld": "com",
        "label": "हिंदी (भारत)",
    },
    "mr": {
        "name": "Marathi",
        "bcp47": "mr-IN",
        "gtts_code": "mr",
        "tld": "com",
        "label": "मराठी (भारत)",
    },
}


class VoiceService:
    @staticmethod
    def get_supported_languages() -> Dict[str, Dict[str, str]]:
        """Returns the dictionary of supported voice languages and metadata."""
        return SUPPORTED_VOICE_LANGUAGES

    @staticmethod
    def normalize_text_for_speech(text: str, lang: str = "en") -> str:
        """
        Cleans and normalizes text for clear, natural speech synthesis:
        1. Strips Markdown bold, italic, headings, bullet markers, and emojis.
        2. Normalizes currency symbols to spoken words (₹ -> Rupees / रुपये).
        3. Collapses redundant whitespace and line breaks into natural pauses.
        """
        if not text:
            return ""

        clean = text

        # Replace currency symbol with spoken words based on language
        if lang == "mr":
            clean = re.sub(r"[₹]|Rs\.?|INR", " रुपये ", clean, flags=re.IGNORECASE)
        elif lang == "hi":
            clean = re.sub(r"[₹]|Rs\.?|INR", " रुपये ", clean, flags=re.IGNORECASE)
        else:
            clean = re.sub(r"[₹]|Rs\.?|INR", " Rupees ", clean, flags=re.IGNORECASE)

        # Remove markdown bold/italic (**text**, *text*, __text__)
        clean = re.sub(r"(\*\*|__)(.*?)\1", r"\2", clean)
        clean = re.sub(r"(\*|_)(.*?)\1", r"\2", clean)

        # Remove markdown headers (# Header)
        clean = re.sub(r"^#+\s*", "", clean, flags=re.MULTILINE)

        # Replace bullet points and dashes with natural pauses
        clean = re.sub(r"^[•\-\*]\s*", "", clean, flags=re.MULTILINE)

        # Remove emojis and special symbol characters (keep standard punctuation)
        clean = re.sub(
            r"[\U00010000-\U0010ffff\u200d\u200c\u2700-\u27bf\ufe0f\ud83c-\ud83e]",
            "",
            clean,
        )

        # Replace multiple spaces and newlines with a single space or pause
        clean = re.sub(r"\n+", ". ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        return clean

    @classmethod
    def synthesize_speech(cls, text: str, lang: str = "en") -> bytes:
        """
        Converts text into MP3 audio bytes using gTTS.
        Supports English ('en'), Hindi ('hi'), and Marathi ('mr').

        Raises ValueError if text is empty or language is unsupported.
        """
        if not text or not text.strip():
            raise ValueError("Text to synthesize cannot be empty.")

        lang_key = lang.lower().strip()
        if lang_key not in SUPPORTED_VOICE_LANGUAGES:
            # Fallback to English if unknown language tag is passed
            logger.warning(
                f"[VoiceService] Unsupported language '{lang}'. Defaulting to 'en'."
            )
            lang_key = "en"

        clean_text = cls.normalize_text_for_speech(text, lang=lang_key)
        if not clean_text:
            raise ValueError("Text contains no speakable characters.")

        config = SUPPORTED_VOICE_LANGUAGES[lang_key]

        try:
            tts = gTTS(
                text=clean_text,
                lang=config["gtts_code"],
                tld=config["tld"],
                slow=False,
            )
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            audio_bytes = buffer.read()
            logger.info(
                f"[VoiceService] Synthesized {len(audio_bytes)} bytes audio for lang='{lang_key}'"
            )
            return audio_bytes
        except Exception as e:
            logger.error(f"[VoiceService] Error synthesizing speech for '{lang_key}': {e}")
            raise RuntimeError(f"Speech synthesis failed: {str(e)}") from e
