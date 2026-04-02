from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_calendar_route():
    print("Testing /calendar route...")
    
    # 1. Login
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=False)
    if response.status_code != 303:
        print("[FAIL] Login failed")
        sys.exit(1)
    cookies = response.cookies
    
    # 2. Access Calendar
    response = client.get("/calendar", cookies=cookies)
    if response.status_code == 200:
        if "Smaran Calendar" in response.text and "calendarGrid" in response.text:
            print("[PASS] Calendar page loaded successfully.")
        else:
            print("[FAIL] Calendar page content missing key elements.")
            print(response.text[:500])
    else:
        print(f"[FAIL] Route returned {response.status_code}")

if __name__ == "__main__":
    test_calendar_route()
