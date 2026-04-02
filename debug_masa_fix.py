from app.engine.panchang import engine_instance
import datetime
import traceback

try:
    # Test case from user: July 25, 1997
    # Expected: Ashadha (index 3), Krishna, Tithi 6.
    date_obj = datetime.date(1997, 7, 25)
    lat = 19.0760
    lon = 72.8777
    
    print(f"Testing for {date_obj} at {lat}, {lon}")
    
    result = engine_instance.get_panchang_from_date(date_obj, lat, lon)
    print("Result:", result)
    
    if result["masa"] == "Ashadha" and result["paksha"] == "Krishna" and result["tithi"] == 6:
        print("SUCCESS: Matches User Expectation")
    else:
        print("FAILURE: Does NOT match expectation (Ashadha Krishna 6)")

except Exception as e:
    print("Caught Exception:")
    traceback.print_exc()
