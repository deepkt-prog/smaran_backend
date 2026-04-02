from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_delete_flow():
    print("Testing Delete Event Flow...")
    
    # 1. Login
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=False)
    if response.status_code != 303:
        print("[FAIL] Login failed")
        sys.exit(1)
    cookies = response.cookies
    
    # 2. Add Dummy Event
    event_data = {
        "name": "Delete Me",
        "masa": "Chaitra",
        "paksha": "Shukla",
        "tithi": 1,
        "is_recurring": True
    }
    response = client.post("/events/", json=event_data, cookies=cookies)
    if response.status_code != 200:
        print(f"[FAIL] Create failed: {response.status_code}")
        sys.exit(1)
    event_id = response.json()['id']
    print(f"[PASS] Created event ID {event_id}")

    # 3. Delete It
    response = client.delete(f"/events/{event_id}", cookies=cookies)
    if response.status_code == 200:
        print(f"[PASS] Deleted event ID {event_id}")
    else:
        print(f"[FAIL] Delete failed: {response.text}")
        sys.exit(1)
        
    # 4. Verify Gone
    response = client.get("/events/", cookies=cookies)
    events = response.json()
    if any(e['id'] == event_id for e in events):
        print("[FAIL] Event still exists!")
    else:
        print("[PASS] Event verified gone.")

if __name__ == "__main__":
    test_delete_flow()
