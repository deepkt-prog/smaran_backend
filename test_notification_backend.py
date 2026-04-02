from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

def test_notification_flow():
    # 1. Login
    login_data = {"username": "thakkerdeep1@gmail.com", "password": "password123"}
    response = client.post("/auth/token", data=login_data)
    
    # If login fails (user might not exist in this clean context?), we might need to signup first or skip.
    # Assuming user exists from previous steps.
    if response.status_code != 200:
        print("[WARN] Login failed, attempting signup...")
        signup_data = {
            "email": "thakkerdeep1@gmail.com", 
            "password": "password123", 
            "mobile_number": "1234567890",
            "latitude": 19.07,
            "longitude": 72.87
        }
        client.post("/auth/signup", data=signup_data)
        response = client.post("/auth/token", data=login_data)
        
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Point: Create Test Notification
    print("creating test notification...")
    resp = client.post("/notifications/test", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    notif_id = data['id']
    print(f"[PASS] Created notification ID: {notif_id}")
    
    # 3. List Notifications
    print("Listing notifications...")
    resp = client.get("/notifications/", headers=headers)
    assert resp.status_code == 200
    notifs = resp.json()
    assert len(notifs) > 0
    print(f"[PASS] Found {len(notifs)} notifications.")
    
    # 4. Mark as Read
    print(f"Marking notification {notif_id} as read...")
    resp = client.post(f"/notifications/{notif_id}/read", headers=headers)
    assert resp.status_code == 200
    assert resp.json()['is_read'] == True
    print("[PASS] Notification marked as read.")

if __name__ == "__main__":
    try:
        test_notification_flow()
        print("Backend Notification Logic Verified Successfully.")
    except Exception as e:
        print(f"Verification FAILED: {e}")
