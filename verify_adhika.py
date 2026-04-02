from app.engine.panchang import engine_instance
import datetime

def verify_adhika_ashadha():
    print("Verifying Ashadha Krishna 6, 2026 (Adhika Masa Check)...")
    # Scenario: 2026 has Adhika Ashadha in June/July. Nija Ashadha is July/Aug.
    # Ashadha Krishna 6 should be in NIJA Ashadha by default.
    # Expected: 4th Aug 2026.
    
    # Inputs
    year = 2026
    masa = "Ashadha"
    paksha = "Krishna"
    tithi = 6
    lat = 19.0760
    lon = 72.8777
    
    date = engine_instance.find_event_date(year, masa, paksha, tithi, lat, lon)
    print(f"Calculated Date: {date}")
    
    expected_date = datetime.date(2026, 8, 4)
    incorrect_date = datetime.date(2026, 7, 6) # Likely Adhika date
    
    if date == expected_date:
        print("[PASS] Correctly identified Nija Ashadha date: Aug 4, 2026.")
    elif date == incorrect_date:
        print("[FAIL] Returned July 6, 2026. This is likely the Adhika Masa, not Nija.")
    else:
        print(f"[INFO] Result {date} is neither expected.")

if __name__ == "__main__":
    verify_adhika_ashadha()
