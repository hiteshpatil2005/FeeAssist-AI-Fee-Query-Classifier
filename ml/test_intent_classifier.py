"""
FeeAssist AI — Automated Intent Classifier Test Suite

Comprehensive automated test suite covering:
1. English language fee queries
2. Hindi language fee queries (Devanagari script)
3. Marathi language fee queries (Devanagari script)
4. Different wording & phrasing for the same intent
5. Short keyword queries
6. Long conversational & polite multi-sentence queries
7. Edge cases (empty string, punctuation, ambiguous input)
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict import predict_intent


def run_tests():
    print("=" * 75)
    print("FeeAssist AI — Intent Classifier Test Suite")
    print("=" * 75)

    passed = 0
    total = 0

    # 1. English Queries Across Distinct Intents
    print("\n--- Test Suite 1: English Queries Across Key Fee Intents ---")
    en_tests = [
        ("Can I pay my semester fee in installments?", "INSTALLMENT"),
        ("What is the last date to submit the college fees without fine?", "DUE_DATE"),
        ("I need to download my fee payment receipt for income tax", "RECEIPT"),
        ("Is there any government scholarship for OBC students?", "SCHOLARSHIP"),
        ("How can I apply for fee refund after admission cancellation?", "REFUND"),
        ("What is the total fee structure for B.Tech computer science?", "FEE_STRUCTURE"),
    ]

    for text, expected in en_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 2. Hindi Queries (Devanagari)
    print("\n--- Test Suite 2: Hindi Fee Queries (Devanagari) ---")
    hi_tests = [
        ("मेरी फीस कितनी बाकी है?", "PENDING_FEE"),
        ("क्या मैं फीस किस्तों में भर सकता हूँ?", "INSTALLMENT"),
        ("फीस भरने की अंतिम तारीख क्या है?", "DUE_DATE"),
        ("मुझे अपनी फीस की रसीद चाहिए", "RECEIPT"),
        ("क्या मुझे छात्रवृत्ति मिल सकती है?", "SCHOLARSHIP"),
        ("क्या एडमिशन रद्द करने पर फीस वापस मिलेगी?", "REFUND"),
    ]

    for text, expected in hi_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 3. Marathi Queries (Devanagari)
    print("\n--- Test Suite 3: Marathi Fee Queries (Devanagari) ---")
    mr_tests = [
        ("माझी किती फी बाकी आहे?", "PENDING_FEE"),
        ("फी भरण्याची शेवटची तारीख कोणती आहे?", "DUE_DATE"),
        ("मला भरलेल्या फीची पावती हवी आहे", "RECEIPT"),
        ("ईबीसी स्कॉलरशिप कशी मिळेल?", "SCHOLARSHIP"),
        ("मला फी हप्त्यांमध्ये भरता येईल का?", "INSTALLMENT"),
        ("प्रवेश रद्द केल्यास फी परत मिळेल का?", "REFUND"),
    ]

    for text, expected in mr_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 4. Different Phrasings of Same Intent
    print("\n--- Test Suite 4: Diverse Phrasings for Same Intent ---")
    phrasing_tests = [
        # INSTALLMENT phrasings
        ("Can I pay in parts?", "INSTALLMENT"),
        ("Is EMI facility available for fees?", "INSTALLMENT"),
        ("हप्त्यांमध्ये फी भरता येईल का?", "INSTALLMENT"),
        # RECEIPT phrasings
        ("Download receipt", "RECEIPT"),
        ("Where can I find my payment challan acknowledgment?", "RECEIPT"),
        ("रसीद डाउनलोड करनी है", "RECEIPT"),
    ]

    for text, expected in phrasing_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 5. Short Keyword Queries
    print("\n--- Test Suite 5: Short Keyword Queries ---")
    short_tests = [
        ("scholarship", "SCHOLARSHIP"),
        ("installment", "INSTALLMENT"),
        ("receipt", "RECEIPT"),
        ("refund", "REFUND"),
        ("due date", "DUE_DATE"),
    ]

    for text, expected in short_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 6. Conversational / Polite Long Queries
    print("\n--- Test Suite 6: Conversational & Multi-Sentence Queries ---")
    long_tests = [
        ("Hello sir, good morning. Could you please let me know when the deadline is for paying second term fee?", "DUE_DATE"),
        ("I made an online payment yesterday through UPI but my status still shows pending. Please confirm my transaction", "PAYMENT_STATUS"),
        ("नमस्ते सर, क्या मुझे बता सकते हैं कि इस साल फीस भरने की आखिरी तारीख कब है?", "DUE_DATE"),
    ]

    for text, expected in long_tests:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    # 7. Edge Cases & Ambiguous Queries
    print("\n--- Test Suite 7: Edge Cases & Ambiguous Queries ---")
    edge_cases = [
        ("", "OTHER_FEE_QUERY"),
        ("   ", "OTHER_FEE_QUERY"),
        ("???!!!", "OTHER_FEE_QUERY"),
    ]

    for text, expected in edge_cases:
        total += 1
        res = predict_intent(text)
        status = "PASSED" if res["intent"] == expected else "FAILED"
        if status == "PASSED":
            passed += 1
        print(f"[{status}] '{text}' -> Got: {res['intent']} (Expected: {expected}, Conf: {res['confidence']*100:.1f}%)")

    print("\n" + "=" * 75)
    accuracy = (passed / total) * 100
    print(f"Test Results: {passed}/{total} Passed ({accuracy:.1f}%)")
    print("=" * 75)

    if passed < total * 0.80:
        raise AssertionError(f"Test suite pass rate ({accuracy:.1f}%) below acceptable 80% threshold.")

    print("🎉 ALL INTENT CLASSIFICATION SUITE CHECKS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
