from app.database import SessionLocal
from app.models import User, Event
from app.engine.panchang import engine_instance, MASA_LIST
from process_reminders import process_daily_reminders
from datetime import date
import logging

# We need to find ONE Tithi that is TODAY for the test user's location to trigger a notification.
# Or, simpler: We can just create a dummy event that we know falls today?
# BUT, the system calculates the date DYNAMICALLY based on Tithi.
# So we must find what Tithi corresponds to TODAY.

def test_notification_flow():
    print("Setting up Notification Test...")
    db = SessionLocal()
    
    # 1. Create/Get Test User
    user = db.query(User).filter(User.email == "notify_test@example.com").first()
    if not user:
        user = User(
            email="notify_test@example.com", 
            hashed_password="hashed_pw", 
            mobile_number="1234567890",
            latitude=19.0760, # Mumbai
            longitude=72.8777,
            timezone="UTC"
        )
        db.add(user)
        db.commit()
    
    # 2. Reverse Engineer: What is the Tithi for TODAY in Mumbai?
    # We can use the engine's internal tools or just brute force check?
    # Better: Use the engine to find the Tithi for "Sunrise Today".
    
    today = date.today()
    print(f"Today is: {today}")
    
    # Let's try to add a dummy event and see if it triggers.
    # Actually, finding the exact Tithi for today might be tricky without a 'get_tithi_for_date' helper.
    # Let's add a helper to panchang.py temporarily or just use the Skyfield logic here.
    
    from skyfield.api import Topos, load
    ts = load.timescale()
    t = ts.utc(today.year, today.month, today.day, 0) # Approximation
    # Actually, let's just use the `get_tithi` function we wrote if accessible?
    # It requires a Time object.
    
    # Alternative: Just run the process and see if it logs anything? No, likely no events match today by chance.
    
    # Let's Mock `engine_instance.find_event_date` to return TODAY for a specific test event.
    # This proves the Reminder Logic works, assuming calculation is correct (which we verified separately).
    
    original_find_date = engine_instance.find_event_date
    
    def mock_find_event_date(year, masa, paksha, tithi, latitude, longitude):
        if masa == "TEST_MASA":
            return today
        return original_find_date(year, masa, paksha, tithi, latitude, longitude)
    
    # Monkey patch
    engine_instance.find_event_date = mock_find_event_date
    
    # Add Test Event
    event = Event(
        user_id=user.id,
        name="Test Notification Event",
        masa="TEST_MASA",
        paksha="Shukla",
        tithi=1,
        is_recurring=True
    )
    db.add(event)
    db.commit()
    
    print("Running Process Reminders...")
    try:
        process_daily_reminders()
        print("Process finished.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        db.delete(event)
        # db.delete(user) # Keep user for potential re-runs or manual check
        db.commit()
        engine_instance.find_event_date = original_find_date

    # 3. Check Log File
    try:
        with open("notification_logs.txt", "r") as f:
            logs = f.read()
            if "Test Notification Event is TODAY" in logs and user.email in logs:
                print("[PASS] Notification logged successfully.")
            else:
                print("[FAIL] Notification NOT found in logs.")
                print("Logs content:")
                print(logs)
    except FileNotFoundError:
        print("[FAIL] Log file not found.")

if __name__ == "__main__":
    test_notification_flow()
