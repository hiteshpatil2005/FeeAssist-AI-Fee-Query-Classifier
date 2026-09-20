"""
FeeAssist AI — Live FastAPI Endpoint Verification Script
Tests POST /api/nlp/classify with multilingual queries.
"""

import json
import sys
import urllib.request

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

API_URL = "http://localhost:8001/api/nlp/classify"

test_cases = [
    ("How much fee do I have left?", "PENDING_FEE"),
    ("मेरी फीस कितनी बाकी है?", "PENDING_FEE"),
    ("माझी किती फी बाकी आहे?", "PENDING_FEE"),
    ("Can I pay in installments?", "INSTALLMENT"),
    ("Where can I download my fee receipt?", "RECEIPT"),
    ("How can I apply for EBC scholarship?", "SCHOLARSHIP"),
    ("When is the last date to pay fees?", "DUE_DATE"),
    ("Will I get a refund if I cancel admission?", "REFUND"),
]

print("=" * 70)
print(f"Testing Live Endpoint: {API_URL}")
print("=" * 70)

all_passed = True
for text, expected in test_cases:
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            status = res.status
            data = json.loads(res.read().decode("utf-8"))
            intent = data.get("intent")
            conf = data.get("confidence", 0.0)
            is_match = intent == expected
            status_tag = "MATCH" if is_match else "DIFFER"
            print(f"[{status_tag}] (HTTP {status}) '{text}'")
            print(f"   -> Result: {intent} (Expected: {expected}, Confidence: {conf * 100:.1f}%)\n")
    except Exception as e:
        print(f"[ERROR] Failed for query '{text}': {e}\n")
        all_passed = False

print("=" * 70)
print("Live FastAPI /api/nlp/classify Endpoint Verification Completed!")
print("=" * 70)
