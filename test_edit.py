from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

def test_edit_flow():
    print("Testing Edit Event Flow...")
    
    # 1. Login
    response = client.post("/auth/login", data={"email": "test@example.com", "password": "password123"}, follow_redirects=False)
    if response.status_code != 303:
        print("[FAIL] Login failed")
        sys.exit(1)
    cookies = response.cookies
    
    # 2. Add Dummy Event
    event_data = {
        "name": "Edit Me",
        "masa": "Chaitra",
        "paksha": "Shukla",
        "tithi": 1,
        "is_recurring": True
    }
    response = client.post("/events/", json=event_data, cookies=cookies)
    event_id = response.json()['id']
    print(f"[PASS] Created event ID {event_id}")

    # 3. Edit It
    update_data = {
        "name": "I WAS EDITED",
        "tithi": 5
    }
    response = client.put(f"/events/{event_id}", json=update_data, cookies=cookies)
    if response.status_code == 200:
        updated_event = response.json()
        if updated_event['name'] == "I WAS EDITED" and updated_event['tithi'] == 5:
            print(f"[PASS] Event updated successfully.")
        else:
            print(f"[FAIL] Attributes mismatch: {updated_event}")
            sys.exit(1)
    else:
        print(f"[FAIL] Update failed: {response.text}")
        sys.exit(1)
    
    # Cleanup
    client.delete(f"/events/{event_id}", cookies=cookies)

if __name__ == "__main__":
    test_edit_flow()
