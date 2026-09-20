import urllib.request
import json

def test_api():
    base_url = "http://localhost:8000"

    # 1. Test /health
    req = urllib.request.Request(f"{base_url}/health")
    with urllib.request.urlopen(req) as resp:
        health_data = json.loads(resp.read().decode())
        print("1. Health check:", health_data)

    # 2. Test /api/auth/login
    login_payload = json.dumps({
        "email": "demo@feeassist.ai",
        "password": "Password123!"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            login_res = json.loads(resp.read().decode())
            token = login_res.get("access_token")
            print("2. Login success! Token received (truncated):", token[:20] + "...")
    except urllib.error.HTTPError as e:
        print("Login failed with code:", e.code, e.read().decode())
        return

    # 3. Test /api/auth/me
    req = urllib.request.Request(
        f"{base_url}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        user_data = json.loads(resp.read().decode())
        print(f"3. Authenticated User: {user_data['name']} ({user_data['email']}), Course: {user_data['course']}")

    # 4. Test /api/fees
    req = urllib.request.Request(
        f"{base_url}/api/fees",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        fees = json.loads(resp.read().decode())
        print(f"4. Fees count: {len(fees)} records. First semester: {fees[0]['semester']}, Total: ₹{fees[0]['total_fee']}")

    # 5. Test /api/fees/summary
    req = urllib.request.Request(
        f"{base_url}/api/fees/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        summary = json.loads(resp.read().decode())
        print(f"5. Fee summary: Total: ₹{summary['total_fee']}, Paid: ₹{summary['paid_amount']}, Pending: ₹{summary['pending_amount']}")

    # 6. Test /api/payments
    req = urllib.request.Request(
        f"{base_url}/api/payments",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as resp:
        payments = json.loads(resp.read().decode())
        print(f"6. Payments count: {len(payments)} records. First: ₹{payments[0]['amount']} via {payments[0]['payment_method']}")

    # 7. Test Register new user
    import time
    test_email = f"student_{int(time.time())}@feeassist.ai"
    reg_payload = json.dumps({
        "name": "Pooja Deshmukh",
        "email": test_email,
        "password": "SecurePassword123!",
        "preferred_language": "Marathi",
        "course": "B.Tech IT",
        "year": 2,
        "semester": 3
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/api/auth/register",
        data=reg_payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        reg_data = json.loads(resp.read().decode())
        print(f"7. Registration success: {reg_data['name']} ({reg_data['email']})")

    print("\n🎉 ALL BACKEND ENDPOINTS PASSED VERIFICATION!")

if __name__ == "__main__":
    test_api()
