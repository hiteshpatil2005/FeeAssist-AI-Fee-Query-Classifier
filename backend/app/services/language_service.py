"""
FeeAssist AI — Language Detection & Resolution Service

Identifies query language (English, Hindi, Marathi), implements the 4-tier
language priority hierarchy, and ensures consistent language context.

Priority Order:
1. Current query language (if detected with high/distinct markers)
2. Conversation language (from active session)
3. User profile preferred language
4. Safe default ('en')
"""

import re
from typing import Optional, Dict


# Distinctive lexical markers for Devanagari script disambiguation
MARATHI_MARKERS = {
    # Pronouns & Possessives
    "माझी", "माझे", "माझ्या", "तुझी", "तुमची", "तुमचे", "तुमच्या", "आपली", "आपले",
    # Question Words & Adverbs
    "किती", "कधी", "कशी", "कसे", "कुठे", "का", "कशा",
    # Verbs & Auxiliaries
    "आहे", "आहेत", "नाही", "नाहीत", "होते", "होती", "होता", "असेल", "नसेल",
    "भरायची", "भरायचे", "भरायचा", "भरले", "भरली", "भरला", "भरू",
    "मिळेल", "होईल", "द्यावी", "द्यावे", "द्यावा", "द्यायचे", "द्यायचा",
    "लागेल", "करावी", "करावे", "करावा", "सांगा", "बघायची", "दाखवा",
    "शकतो", "शकते", "शकतात", "झाले", "झाली", "झाला",
    # Domain Nouns
    "सत्र", "हप्ता", "हप्ते", "पावती", "सूट", "परतावा", "माहिती", "चौकशी",
    "मुदत", "दिनांक", "शुल्क", "शिक्षण", "वसतिगृह", "वाचनालय",
    # Particles & Postpositions
    "तर", "ची", "चे", "च्या", "ला", "मध्ये", "वरून", "सुद्धा", "पण", "हवे", "हवी",
}

HINDI_MARKERS = {
    # Pronouns & Possessives
    "मेरी", "मेरा", "मेरे", "मुझे", "मुझको", "आपकी", "आपका", "आपके", "हमारा", "हमारी",
    # Question Words & Adverbs
    "कितनी", "कितना", "कितने", "कब", "कैसे", "कैसा", "कहाँ", "क्यों",
    # Verbs & Auxiliaries
    "है", "हैं", "हूँ", "हो", "था", "थी", "थे", "होगा", "होगी", "होंगे",
    "देनी", "देना", "देने", "दिया", "दिए", "दी", "जमा", "करना", "करनी", "करें",
    "पड़ेगा", "पड़ेगी", "पड़ेंगे", "सकते", "सकता", "सकती", "रहा", "रही", "रहे",
    "किए", "किया", "बताना", "बताएं", "बताओ", "चाहिए",
    # Domain Nouns
    "किस्त", "किस्तें", "किस्तों", "रसीद", "छात्रवृत्ति", "वापसी", "भुगतान", "बकाया",
    "तारीख", "शुल्क",
    # Postpositions & Particles
    "की", "का", "के", "को", "से", "में", "पर", "लिए", "तो", "भी",
}

# Romanized / Transliterated markers
ROMAN_MARATHI_MARKERS = {"kiti", "ahe", "maza", "mazi", "baki", "bharaychi", "bharle", "kadhi", "sang", "dakva"}
ROMAN_HINDI_MARKERS = {"kitna", "kitni", "hai", "meri", "mera", "baki", "dena", "deni", "kab", "batao", "chahiye"}


def detect_language(text: str) -> Optional[str]:
    """
    Detects whether the input text is English ('en'), Hindi ('hi'), or Marathi ('mr').
    Returns language code or None if input is ambiguous.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return None

    clean = text.strip()

    # Check for Devanagari characters: Unicode range U+0900 to U+097F
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', clean))
    total_letters = len(re.findall(r'[a-zA-Z\u0900-\u097F]', clean))

    # If there are no alphabetical characters (e.g. only numbers '5', '10000', symbols), language is ambiguous
    if total_letters == 0:
        return None

    # 1. Predominantly Latin Script
    if devanagari_chars == 0 or (total_letters > 0 and devanagari_chars / total_letters < 0.25):
        low_words = set(re.findall(r'\b[a-zA-Z]+\b', clean.lower()))
        mr_matches = len(low_words & ROMAN_MARATHI_MARKERS)
        hi_matches = len(low_words & ROMAN_HINDI_MARKERS)

        if mr_matches > hi_matches and mr_matches >= 2:
            return "mr"
        if hi_matches > mr_matches and hi_matches >= 2:
            return "hi"
        return "en"

    # 2. Devanagari Script: Disambiguate Marathi vs Hindi
    words = re.findall(r'[\u0900-\u097F]+', clean)
    if not words:
        return "en"

    mr_score = 0
    hi_score = 0

    for w in words:
        if w in MARATHI_MARKERS:
            mr_score += 2
        if w in HINDI_MARKERS:
            hi_score += 2

        # Suffix and morphological checks
        if len(w) >= 3:
            if w.endswith(("ची", "चे", "च्या", "ला", "त", "हून", "वरून")):
                mr_score += 1
            if w.endswith(("की", "का", "के", "को", "ों", "ियां", "ाएं")):
                hi_score += 1

    if mr_score > hi_score:
        return "mr"
    elif hi_score > mr_score:
        return "hi"

    # Secondary heuristic for single words or short phrases
    # Look for characteristic letter combinations: e.g. ळ (U+0933) is exclusively Marathi
    if "ळ" in clean:
        return "mr"

    return "hi" if hi_score > 0 else ("mr" if mr_score > 0 else None)


def normalize_pref_language(pref: Optional[str]) -> str:
    """Converts user profile language string into 2-letter ISO code."""
    if not pref:
        return "en"
    low = pref.lower().strip()
    if "marathi" in low or low == "mr":
        return "mr"
    if "hindi" in low or low == "hi":
        return "hi"
    return "en"


def resolve_language(
    query_text: str,
    session_lang: Optional[str] = None,
    user_pref: Optional[str] = None,
) -> str:
    """
    Applies the strict 4-tier language priority hierarchy:
    1. Current query language (if recognized)
    2. Active conversation language
    3. User profile preferred language
    4. Safe default ('en')
    """
    # 1. Current query language
    query_lang = detect_language(query_text)
    if query_lang in ("en", "hi", "mr"):
        return query_lang

    # 2. Conversation language
    if session_lang and session_lang in ("en", "hi", "mr"):
        return session_lang

    # 3. User preferred language
    if user_pref:
        user_lang = normalize_pref_language(user_pref)
        if user_lang in ("en", "hi", "mr"):
            return user_lang

    # 4. Safe default
    return "en"
