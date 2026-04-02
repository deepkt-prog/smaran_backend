from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_routes():
    print("Testing Auth Routes...")
    
    # Test Login Page
    response = client.get("/auth/login")
    if response.status_code == 200:
        print("[PASS] Login Page is accessible (200 OK)")
    else:
        print(f"[FAIL] Login Page failed ({response.status_code})")
        sys.exit(1)

    # Test Signup Page
    response = client.get("/auth/signup")
    if response.status_code == 200:
        print("[PASS] Signup Page is accessible (200 OK)")
    else:
        print(f"[FAIL] Signup Page failed ({response.status_code})")
        sys.exit(1)

    # Test Signup Submission (Reproduction)
    print("Testing Signup Submission...")
    signup_data = {
        "email": "test@example.com",
        "password": "password123",
        "mobile_number": "9876543210",
        "latitude": "19.0760",
        "longitude": "72.8777"
    }
    try:
        response = client.post("/auth/signup", data=signup_data)
        if response.status_code == 200 or response.status_code == 303:
            print(f"[PASS] Signup Submission successful ({response.status_code})")
        else:
            print(f"[FAIL] Signup Submission failed ({response.status_code})")
            print(f"Error Details: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Exception during signup: {e}")
        sys.exit(1)
        
    print("All routes passed.")

if __name__ == "__main__":
    test_routes()
