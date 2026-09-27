"""
FeeAssist AI — Entity Extraction Service

Extracts structured financial, temporal, and academic entities from
multilingual queries in English, Hindi, and Marathi:
- amount: Numeric value (e.g. 15000.0) from ₹15,000, Rs 15000, 10k, १०,००० रुपये
- date: Normalized string or date indicator (e.g. "yesterday", "2026-11-15")
- semester: Integer (e.g. 2, 4, 5)
- academic_year: Normalized academic year (e.g. "2025-26")
- fee_type: Fee category (e.g. "Tuition", "Hostel", "Exam", "Mess")
- payment_method: Payment mode (e.g. "UPI", "Net Banking", "Card")
- transaction_id: Transaction identifier (e.g. "TXN192847192")
- installment_count: Number of requested installments (e.g. 2, 3)
- is_hypothetical: Boolean True if the query is a hypothetical simulation ("What if I pay ₹10,000?")
"""

import re
from typing import Dict, Any, Optional

# Devanagari digit conversion map
DEVANAGARI_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

def to_western_digits(text: str) -> str:
    """Convert Devanagari numerals (०-९) to Western digits (0-9)."""
    return "".join(DEVANAGARI_DIGITS.get(ch, ch) for ch in text)


def extract_amount(text: str) -> Optional[float]:
    """
    Extract monetary amount from text:
    Supports ₹15,000, Rs 15000, 10k, 10,000 INR, 15000 rupees, १०००० रुपये
    """
    converted = to_western_digits(text)

    # 1. Match 'k' or 'k' notation (e.g. 10k, 25.5k)
    k_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k\b', converted, re.IGNORECASE)
    if k_match:
        try:
            return round(float(k_match.group(1)) * 1000.0, 2)
        except ValueError:
            pass

    # 2. Match standard currency patterns: ₹ 15,000 or Rs. 15,000 or 15000 rupees/रुपये
    amount_match = re.search(
        r'(?:₹|rs\.?|inr|रुपये|रु\.?)\s*(\d[\d,]*(?:\.\d{1,2})?)|(\d[\d,]*(?:\.\d{1,2})?)\s*(?:₹|rs\.?|inr|rupees|rupee|रुपये|रु\.?)',
        converted,
        re.IGNORECASE
    )
    if amount_match:
        val_str = amount_match.group(1) or amount_match.group(2)
        clean_num = val_str.replace(",", "")
        try:
            val = float(clean_num)
            if val > 0:
                return round(val, 2)
        except ValueError:
            pass

    # 3. Match standalone numbers when context implies amount (e.g., "if I pay 10,000", "१०,००० भरले", "१०,००० जमा")
    amount_keywords = ['pay', 'paid', 'paying', 'give', 'भरले', 'दिए', 'देता', 'भरा', 'भरणे', 'देने', 'जमा', 'करूँ', 'दिले', 'रुपये', 'रुपया', 'रुपयांची']
    if any(k in converted.lower() for k in amount_keywords) or is_hypothetical_query(text):
        standalone = re.search(r'(?:^|\s|₹|rs\.?)(\d{1,3}(?:,\d{2,3})+(?:\.\d{1,2})?|\d{3,7}(?:\.\d{1,2})?)(?:\s|$|[.,?!])', converted)
        if standalone:
            try:
                clean_s = standalone.group(1).replace(",", "")
                val = float(clean_s)
                if val > 0:
                    return round(val, 2)
            except ValueError:
                pass

    return None


def extract_semester(text: str) -> Optional[int]:
    """Extract semester number (1-12) from English, Hindi, or Marathi."""
    converted = to_western_digits(text)

    # English, Hindi, Marathi: "semester 4", "sem 4", "सत्र 4", "सेमेस्टर 4", "सेमिस्टर 4"
    patterns = [
        r'(?:semester|sem|सत्र|सेमेस्टर|सेमिस्टर)\s*[-:]?\s*(\d{1,2})',
        r'(\d{1,2})(?:st|nd|rd|th)?\s*(?:semester|sem|सत्र|सेमेस्टर|सेमिस्टर)',
    ]
    for pat in patterns:
        m = re.search(pat, converted, re.IGNORECASE)
        if m:
            try:
                sem = int(m.group(1))
                if 1 <= sem <= 12:
                    return sem
            except ValueError:
                pass

    # Word-based numbers: "first sem", "second semester", "दुसरे सत्र", "सहावे सत्र"
    word_map = {
        'first': 1, '1st': 1, 'पहिला': 1, 'पहिले': 1, 'प्रथम': 1,
        'second': 2, '2nd': 2, 'दूसरा': 2, 'दुसरे': 2, 'द्वितीय': 2,
        'third': 3, '3rd': 3, 'तीसरा': 3, 'तिसरे': 3, 'तृतीय': 3,
        'fourth': 4, '4th': 4, 'चौथा': 4, 'चौथे': 4,
        'fifth': 5, '5th': 5, 'पांचवा': 5, 'पाचवे': 5,
        'sixth': 6, '6th': 6, 'छठा': 6, 'सहावे': 6,
        'seventh': 7, '7th': 7, 'सातवा': 7, 'सातवे': 7,
        'eighth': 8, '8th': 8, 'आठवा': 8, 'आठवे': 8,
    }
    low = text.lower()
    for word, sem in word_map.items():
        if word in low and any(term in low for term in ['sem', 'semester', 'सत्र', 'सेमेस्टर', 'सेमिस्टर']):
            return sem

    return None


def extract_academic_year(text: str) -> Optional[str]:
    """Extract academic year: '2025-26', '2025-2026', '25-26'."""
    converted = to_western_digits(text)
    m = re.search(r'\b(20\d{2})[-/](20\d{2}|\d{2})\b', converted)
    if m:
        start_yr = m.group(1)
        end_yr = m.group(2)
        if len(end_yr) == 4:
            end_yr = end_yr[2:]
        return f"{start_yr}-{end_yr}"
    return None


def extract_fee_type(text: str) -> Optional[str]:
    """Extract fee category: Tuition, Hostel, Exam, Mess, Library, etc."""
    low = text.lower()
    # Helper to match whole word or delimited by whitespace/punctuation
    def has_word(pattern_list):
        for pat in pattern_list:
            if re.search(rf'(?<![\w\u0900-\u097F]){re.escape(pat)}(?![\w\u0900-\u097F])', low):
                return True
        return False

    if has_word(['tuition', 'ट्यूशन', 'शिक्षण']):
        return "Tuition"
    if has_word(['hostel', 'हॉस्टेल', 'वसतिगृह']):
        return "Hostel"
    if has_word(['mess', 'मेस', 'भोजन']):
        return "Mess"
    if has_word(['exam', 'परीक्षा', 'परीक्षेची']):
        return "Exam"
    if has_word(['library', 'वाचनालय', 'ग्रंथालय']):
        return "Library"
    if has_word(['bus', 'transport', 'बस', 'वाहतूक']):
        return "Transport"
    return None


def extract_payment_method(text: str) -> Optional[str]:
    """Extract payment method: UPI, Net Banking, Card, Cash."""
    low = text.lower()
    if any(k in low for k in ['upi', 'gpay', 'phonepe', 'paytm']):
        return "UPI"
    if any(k in low for k in ['net banking', 'netbanking', 'bank transfer', 'neft', 'rtgs', 'imps']):
        return "Net Banking"
    if any(k in low for k in ['debit card', 'credit card', 'card']):
        return "Card"
    if any(k in low for k in ['cash', 'रोकड', 'नकद']):
        return "Cash"
    if any(k in low for k in ['cheque', 'check', 'धनादेश']):
        return "Cheque"
    return None


def extract_transaction_id(text: str) -> Optional[str]:
    """Extract transaction identifiers like TXN192847192, UPI/123456789012."""
    m = re.search(r'\b(TXN[A-Za-z0-9]+|UPI/[0-9]+|[0-9]{12,18})\b', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def extract_date(text: str) -> Optional[str]:
    """Extract temporal references: yesterday, today, tomorrow, or explicit date."""
    low = text.lower()
    if any(k in low for k in ['yesterday', 'काल']):
        return "yesterday"
    if any(k in low for k in ['today', 'आज']):
        return "today"
    if any(k in low for k in ['tomorrow', 'उद्या']):
        return "tomorrow"
    if 'कल' in text:
        # In Hindi, 'कल' can mean yesterday or tomorrow depending on verb tense
        if any(v in low for v in ['था', 'थी', 'थे', 'किया', 'दिया']):
            return "yesterday"
        return "tomorrow"

    # Explicit dates: 15th Nov, 15 November 2026, 2026-11-15
    m = re.search(r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:\s+\d{2,4})?|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def extract_installment_count(text: str) -> Optional[int]:
    """Extract installment count: '2 installments', '3 parts', '२ हप्ते'."""
    converted = to_western_digits(text)
    m = re.search(r'\b(\d{1,2})\s*(?:installments?|parts?|emis?|हप्ते|हप्त्यांमध्ये|किस्त(?:ों|ें)?)\b', converted, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def is_hypothetical_query(text: str) -> bool:
    """
    Check if query is asking a hypothetical payment calculation:
    e.g. "What if I pay ₹10,000?", "If I pay 5000 how much will remain?",
         "जर मी १०,००० भरले तर किती बाकी राहील?", "अगर मैं ५००० दूँ तो"
    """
    low = text.lower()
    hypothetical_indicators = [
        "what if i pay",
        "if i pay",
        "what if i give",
        "suppose i pay",
        "how much will remain if",
        "how much fee will be left if",
        "will remain if i pay",
        "जर मी",
        "भरले तर किती",
        "अगर मैं",
        "दूँ तो कितना",
        "भर दूँ तो",
    ]
    return any(ind in low for ind in hypothetical_indicators)


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Unified entity extraction for FeeAssist AI.
    Returns structured dict with all extracted entities.
    """
    return {
        "amount": extract_amount(text),
        "semester": extract_semester(text),
        "academic_year": extract_academic_year(text),
        "fee_type": extract_fee_type(text),
        "payment_method": extract_payment_method(text),
        "transaction_id": extract_transaction_id(text),
        "date": extract_date(text),
        "installment_count": extract_installment_count(text),
        "is_hypothetical": is_hypothetical_query(text),
    }
