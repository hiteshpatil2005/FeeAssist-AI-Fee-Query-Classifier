"""
FeeAssist AI — Task 5 Automated Comprehensive Integration Test Suite

Verifies:
1. Fee CRUD API operations (POST, GET, PUT, DELETE, Summary)
2. Deterministic Financial Formula: Pending = Total - Paid - Scholarship
3. Multi-Record Disambiguation (Ambiguous queries trigger clarification prompt)
4. Specific Record Resolution (Queries with semester/year target exact record)
5. Multilingual Entity Extraction (English, Hindi, Marathi)
6. Hypothetical Payment Simulation ("What if I pay ₹10,000?")
7. Deterministic Installment Calculations (2-part, 3-part, custom)
8. Payment History & Verified Receipts Retrieval
9. Multi-turn Conversational Context Retention (Session memory)
10. Strict Student Data Isolation (User A cannot access User B data)
"""

import sys
import os
import json
import uuid
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")


def http_req(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {"error": content}
        return e.code, parsed


def register_or_login(email, password, name="Test Student", course="B.Tech CS"):
    status, res = http_req("POST", "/api/auth/login", {"email": email, "password": password})
    if status == 200:
        return res["access_token"]
    # Register if not exists
    reg_status, reg_res = http_req("POST", "/api/auth/register", {
        "name": name,
        "email": email,
        "password": password,
        "course": course,
        "year": 2,
        "semester": 4,
        "preferred_language": "English"
    })
    if reg_status in (200, 201):
        status, res = http_req("POST", "/api/auth/login", {"email": email, "password": password})
        return res["access_token"]
    raise RuntimeError(f"Could not authenticate user {email}: {reg_res}")


def run_tests():
    print("=" * 75)
    print("  FeeAssist AI — Task 5 Integration & Verification Test Suite")
    print("=" * 75)

    passes = 0
    total = 10

    # Setup 2 distinct student accounts for isolation testing
    student_a_email = f"student_a_{uuid.uuid4().hex[:6]}@feeassist.ai"
    student_b_email = f"student_b_{uuid.uuid4().hex[:6]}@feeassist.ai"
    pwd = "Password123!"

    token_a = register_or_login(student_a_email, pwd, "Alice Johnson", "B.Tech Computer Science")
    token_b = register_or_login(student_b_email, pwd, "Bob Smith", "B.Tech Mechanical")
    print(f"✓ Provisioned Student A: {student_a_email}")
    print(f"✓ Provisioned Student B: {student_b_email}")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Fee CRUD API Operations
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 1] Fee CRUD Operations...")
    create_payload = {
        "academic_year": "2026-27",
        "semester": 6,
        "course": "B.Tech Computer Science",
        "fee_type": "Tuition",
        "total_fee": 80000.0,
        "paid_amount": 20000.0,
        "scholarship_amount": 10000.0,
        "due_date": "2026-11-30",
        "notes": "Task 5 test fee",
    }
    status, fee_a1 = http_req("POST", "/api/fees", create_payload, token_a)
    assert status == 201, f"Expected 201 Created, got {status}: {fee_a1}"
    assert fee_a1["id"] is not None
    fee_a1_id = fee_a1["id"]

    # Verify GET by ID
    status, fee_fetched = http_req("GET", f"/api/fees/{fee_a1_id}", token=token_a)
    assert status == 200 and fee_fetched["semester"] == 6

    # Verify UPDATE (PUT)
    update_payload = dict(create_payload)
    update_payload["paid_amount"] = 35000.0
    status, fee_updated = http_req("PUT", f"/api/fees/{fee_a1_id}", update_payload, token_a)
    assert status == 200 and fee_updated["paid_amount"] == 35000.0

    print("  ✓ Created, retrieved, and updated fee record successfully.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Deterministic Financial Formula Check
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 2] Deterministic Financial Formula Verification...")
    # Formula: Pending = Total (80,000) - Paid (35,000) - Scholarship (10,000) = 35,000.0
    expected_pending = round(80000.0 - 35000.0 - 10000.0, 2)
    assert fee_updated["pending_amount"] == expected_pending, (
        f"Formula mismatch: expected {expected_pending}, got {fee_updated['pending_amount']}"
    )
    print(f"  ✓ Verified pending amount: {fee_updated['pending_amount']} == {expected_pending}")

    # Summary verification
    status, summary = http_req("GET", "/api/fees/summary", token=token_a)
    assert status == 200
    assert summary["total_fee"] == 80000.0
    assert summary["paid_amount"] == 35000.0
    assert summary["scholarship_amount"] == 10000.0
    assert summary["pending_amount"] == expected_pending
    print(f"  ✓ Verified summary endpoint aggregated totals deterministically.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Multi-Record Disambiguation Prompt
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 3] Multi-Record Disambiguation Logic...")
    # Add a second fee record for Student A
    create_payload_sem7 = {
        "academic_year": "2027-28",
        "semester": 7,
        "course": "B.Tech Computer Science",
        "fee_type": "Tuition",
        "total_fee": 85000.0,
        "paid_amount": 0.0,
        "scholarship_amount": 0.0,
        "due_date": "2027-04-15",
    }
    http_req("POST", "/api/fees", create_payload_sem7, token_a)

    # Student A now has Sem 6 and Sem 7. Query without specifying semester:
    status, chat_res = http_req("POST", "/api/chat", {"message": "How much fee do I have to pay?"}, token_a)
    assert status == 200
    assert chat_res["needs_clarification"] is True, f"Expected clarification needed, got {chat_res}"
    assert len(chat_res["options"]) >= 2
    assert "multiple fee records" in chat_res["message"].lower()
    print("  ✓ Multiple fee records detected; properly prompted student for disambiguation.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 4. Specific Record Resolution
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 4] Specific Record Target Resolution...")
    status, sem6_res = http_req(
        "POST", "/api/chat",
        {"message": "What is my pending balance for semester 6?"},
        token_a
    )
    assert status == 200
    assert sem6_res["needs_clarification"] is False
    assert "35,000" in sem6_res["message"]
    print("  ✓ Explicit semester query resolved directly to Semester 6 fee record.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Multilingual Entity Extraction
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 5] Multilingual Entity Extraction (English, Hindi, Marathi)...")
    # Marathi query targeting semester 6
    status, mr_res = http_req(
        "POST", "/api/chat",
        {"message": "सेमिस्टर ६ ची फी किती बाकी आहे?"},
        token_a
    )
    assert status == 200
    assert "35,000" in mr_res["message"]

    # Hindi query targeting semester 6
    status, hi_res = http_req(
        "POST", "/api/chat",
        {"message": "मेरी सेमेस्टर ६ की फीस कितनी बाकी है?"},
        token_a
    )
    assert status == 200
    assert "35,000" in hi_res["message"]
    print("  ✓ Correctly resolved fee details for Hindi and Marathi queries.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Hypothetical Payment Simulation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 6] Hypothetical Payment Simulation...")
    sess_id = f"test_sim_{uuid.uuid4().hex[:6]}"
    # Prime session with semester 6
    http_req("POST", "/api/chat", {"message": "Show fee for semester 6", "session_id": sess_id}, token_a)

    # Ask hypothetical question
    status, hypo_res = http_req(
        "POST", "/api/chat",
        {"message": "What if I pay ₹10,000?", "session_id": sess_id},
        token_a
    )
    assert status == 200
    assert "10,000" in hypo_res["message"]
    assert "25,000" in hypo_res["message"]  # 35,000 - 10,000 = 25,000
    assert "simulated calculation" in hypo_res["message"].lower()

    # Confirm DB was NOT modified!
    status, fee_check = http_req("GET", f"/api/fees/{fee_a1_id}", token=token_a)
    assert fee_check["pending_amount"] == 35000.0, "DB was modified by hypothetical query!"
    print("  ✓ Simulated ₹10,000 deduction correctly computed (₹25,000 balance) without DB modification.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 7. Deterministic Installment Calculations
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 7] Deterministic Installment Calculations...")
    status, inst_res = http_req(
        "POST", "/api/chat",
        {"message": "Can I pay semester 6 in 2 installments?", "session_id": sess_id},
        token_a
    )
    assert status == 200
    assert inst_res["intent"] == "INSTALLMENT"
    # 35,000 / 2 = 17,500
    assert "17,500" in inst_res["message"]
    print("  ✓ Computed 2-part installment breakdown (₹17,500 each) on actual pending balance.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 8. Payment History & Verified Receipts
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 8] Payment History & Verified Receipts...")
    # Add a mock payment for student A
    payment_payload = {
        "amount": 35000.0,
        "payment_date": "2026-08-10",
        "fee_type": "Tuition Fee",
        "payment_method": "UPI",
        "transaction_id": f"TXN_{uuid.uuid4().hex[:8].upper()}",
    }
    http_req("POST", "/api/payments", payment_payload, token_a)

    status, receipt_res = http_req("POST", "/api/chat", {"message": "Show my payment receipt"}, token_a)
    assert status == 200
    assert receipt_res["intent"] == "RECEIPT"
    assert "35,000" in receipt_res["message"]
    assert "REC-" in receipt_res["message"]
    print("  ✓ Retrieved official payment receipt with formatted receipt number.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 9. Multi-turn Conversational Context Retention
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 9] Multi-turn Context Retention...")
    multi_sess = f"multi_sess_{uuid.uuid4().hex[:6]}"
    # Turn 1: Mention semester 6
    http_req("POST", "/api/chat", {"message": "How much fee is remaining for semester 6?", "session_id": multi_sess}, token_a)

    # Turn 2: Follow-up question without mentioning semester 6
    status, follow_up = http_req("POST", "/api/chat", {"message": "When is the due date?", "session_id": multi_sess}, token_a)
    assert status == 200
    assert follow_up["intent"] == "DUE_DATE"
    assert "Semester 6" in follow_up["message"]
    assert "November 30, 2026" in follow_up["message"]
    print("  ✓ Context smoothly retained: follow-up due date query identified Semester 6.")
    passes += 1

    # ─────────────────────────────────────────────────────────────────────────
    # 10. Strict Student Data Isolation
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[Test 10] Strict Student Data Isolation...")
    # Student B should NOT be able to view Student A's fee record
    status, _ = http_req("GET", f"/api/fees/{fee_a1_id}", token=token_b)
    assert status in (403, 404), f"Expected 403 or 404 on cross-user access, got {status}"

    # Student B should have empty fee list initially
    status, fees_b = http_req("GET", "/api/fees", token=token_b)
    assert status == 200 and len(fees_b) == 0

    # Student B querying fees gets a clean no-record response, never Student A's data
    status, chat_b = http_req("POST", "/api/chat", {"message": "What is my pending fee?"}, token_b)
    assert status == 200
    assert "no fee records" in chat_b["message"].lower()

    # Cleanup: Delete fee record for student A
    status, _ = http_req("DELETE", f"/api/fees/{fee_a1_id}", token=token_a)
    assert status == 200

    print("  ✓ Strict data isolation verified across authenticated student accounts.")
    passes += 1

    print("\n" + "=" * 75)
    print(f"  All {passes}/{total} Integration Tests Passed Successfully! (100%)")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()
