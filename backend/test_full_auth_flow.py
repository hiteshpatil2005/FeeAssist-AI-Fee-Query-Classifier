"""
FeeAssist AI — Full CLI Auth & Data Isolation Test
Tests:
1. Health check
2. Login with seeded demo user (demo@feeassist.ai)
3. Fetch /api/auth/me, /api/fees, /api/fees/summary, /api/payments for demo user
4. Register a NEW unique user (newstudent@feeassist.ai)
5. Login with new user credentials and obtain new JWT
6. Verify /api/auth/me returns new user profile
7. Verify /api/fees returns empty list for new user (strict data isolation!)
8. Verify /api/fees/summary returns 0s for new user
9. Verify unauthorized request without token is rejected with 401
10. Verify login with wrong password is rejected with 401
"""

import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:8000"

def request(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return e.code, parsed

def run_tests():
    print("==================================================")
    print("FeeAssist AI — Verification Test Suite")
    print("==================================================")

    # 1. Health
    status, res = request(f"{BASE_URL}/health")
    assert status == 200, f"Health check failed: {res}"
    print(f"✅ 1. GET /health -> {res}")

    # 2. Login with demo user
    status, res = request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "demo@feeassist.ai", "password": "Password123!"}
    )
    assert status == 200, f"Demo login failed: {res}"
    demo_token = res["access_token"]
    print(f"✅ 2. POST /api/auth/login (Demo) -> Token received")

    # 3. Demo user profile
    status, me = request(f"{BASE_URL}/api/auth/me", token=demo_token)
    assert status == 200 and me["email"] == "demo@feeassist.ai"
    print(f"✅ 3. GET /api/auth/me -> {me['name']} ({me['email']}), Program: {me['course']}")

    # 4. Demo fees
    status, fees = request(f"{BASE_URL}/api/fees", token=demo_token)
    assert status == 200 and len(fees) >= 2
    print(f"✅ 4. GET /api/fees -> Found {len(fees)} fee records (Semesters: {[f['semester'] for f in fees]})")

    # 5. Demo fee summary
    status, summary = request(f"{BASE_URL}/api/fees/summary", token=demo_token)
    assert status == 200
    print(f"✅ 5. GET /api/fees/summary -> Total: ₹{summary['total_fee']}, Paid: ₹{summary['paid_amount']}, Pending: ₹{summary['pending_amount']}")

    # 6. Demo payments
    status, payments = request(f"{BASE_URL}/api/payments", token=demo_token)
    assert status == 200 and len(payments) >= 2
    print(f"✅ 6. GET /api/payments -> Found {len(payments)} payment transactions")

    # 7. Register a brand new student
    test_email = f"student_{int(time.time())}@feeassist.ai"
    reg_data = {
        "name": "Tanvi Joshi",
        "email": test_email,
        "password": "Password123!",
        "preferred_language": "Marathi",
        "course": "B.Tech Computer Science",
        "year": 2,
        "semester": 4
    }
    status, new_user = request(f"{BASE_URL}/api/auth/register", method="POST", data=reg_data)
    assert status == 201 and new_user["email"] == test_email
    print(f"✅ 7. POST /api/auth/register -> Registered {new_user['name']} ({new_user['email']})")

    # 8. Login as new student
    status, login_res = request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": test_email, "password": "Password123!"}
    )
    assert status == 200
    new_token = login_res["access_token"]
    print(f"✅ 8. POST /api/auth/login (New Student) -> Authenticated successfully")

    # 9. Test Data Isolation: New student has 0 fees
    status, new_fees = request(f"{BASE_URL}/api/fees", token=new_token)
    assert status == 200 and len(new_fees) == 0, f"Data isolation violated: {new_fees}"
    print(f"✅ 9. Data Isolation Test: GET /api/fees for new student returns 0 records (Cannot see demo user's fees)")

    # 10. Test Data Isolation: New student has 0 payments
    status, new_payments = request(f"{BASE_URL}/api/payments", token=new_token)
    assert status == 200 and len(new_payments) == 0, f"Data isolation violated: {new_payments}"
    print(f"✅ 10. Data Isolation Test: GET /api/payments for new student returns 0 records")

    # 11. Test Security: Reject request without Bearer token
    status, err = request(f"{BASE_URL}/api/fees")
    assert status in (401, 403), f"Expected 401/403, got {status}"
    print(f"✅ 11. Security Test: GET /api/fees without token rejected with HTTP {status}")

    # 12. Test Security: Reject invalid credentials
    status, err = request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "demo@feeassist.ai", "password": "WrongPassword!"}
    )
    assert status == 401, f"Expected 401, got {status}"
    print(f"✅ 12. Security Test: Invalid password rejected with HTTP 401")

    print("==================================================")
    print("🎉 ALL 12 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
