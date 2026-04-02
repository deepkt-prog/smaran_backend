from app.engine.panchang import engine_instance
import datetime

def verify_pausha():
    print("Verifying Pausha Krishna 1, 2026...")
    # Expected: Around Jan 4, 2026
    
    # Inputs
    year = 2026
    masa = "Pausha"
    paksha = "Krishna"
    tithi = 1
    lat = 19.0760
    lon = 72.8777
    
    date = engine_instance.find_event_date(year, masa, paksha, tithi, lat, lon)
    print(f"Calculated Date: {date}")
    
    if date == datetime.date(2026, 1, 4) or date == datetime.date(2026, 1, 5):
        print("[PASS] Matches expected Jan 4/5 2026.")
    elif date == datetime.date(2026, 2, 2):
        print("[FAIL] Matches the reported incorrect date (Feb 2). Logic is likely off by 1 month.")
    else:
        print(f"[INFO] Result {date} is neither Jan 4 nor Feb 2.")

if __name__ == "__main__":
    verify_pausha()
