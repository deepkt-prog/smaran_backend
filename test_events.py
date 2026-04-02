from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_event_flow():
    print("Testing Event Management Flow...")
    
    # 1. Login to get cookie
    login_data = {"username": "test@example.com", "password": "password123"}
    # Note: Login endpoint expects form data 'email' not username if using standard OAuth2, 
    # but our custom auth uses 'email'. Let's check auth.py again if I need to matches exactly.
    # checking auth.py: email: str = Form(...), password: str = Form(...)
    
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=False)
    
    if response.status_code != 303:
             print(f"[FAIL] Login expected 303 redirect, got {response.status_code}")
             print(f"Details: {response.text[:200]}...") # Print only start to avoid huge dump
             sys.exit(1)
            
    # Get the cookie
    cookies = response.cookies
    print("[PASS] Login successful, got cookies.")

    # 2. Add Event
    event_data = {
        "name": "Test Event",
        "masa": "Chaitra",
        "paksha": "Shukla",
        "tithi": 1,
        "is_recurring": True
    }
    
    print("Adding Event...")
    response = client.post("/events/", json=event_data, cookies=cookies)
    if response.status_code == 200:
        created_event = response.json()
        print(f"[PASS] Event created: {created_event['name']} (ID: {created_event['id']})")
    else:
        print(f"[FAIL] Create Event failed ({response.status_code})")
        print(response.text)
        sys.exit(1)

    # 3. List Events
    print("Listing Events...")
    response = client.get("/events/", cookies=cookies)
    if response.status_code == 200:
        events = response.json()
        found = any(e['name'] == "Test Event" for e in events)
        if found:
            print(f"[PASS] Event found in list.")
        else:
            print("[FAIL] Event NOT found in list.")
            print(events)
            sys.exit(1)
    else:
        print(f"[FAIL] List Events failed ({response.status_code})")
        sys.exit(1)

if __name__ == "__main__":
    test_event_flow()
