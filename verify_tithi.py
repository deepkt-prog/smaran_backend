from app.engine.panchang import engine_instance
import datetime

def test_logic():
    print("Testing Smaran Engine...")
    
    # Test Case: Ganesh Chaturthi 2025
    # Bhadrapada Shukla Chaturthi (4)
    # Location: Mumbai (19.0760, 72.8777)
    
    year = 2025
    masa = "Chaitra"
    paksha = "Krishna"
    tithi = 3
    lat = 19.0760
    lon = 72.8777
    
    print(f"Finding date for {masa} {paksha} {tithi} in {year} for Mumbai...")
    
    # Debug: Check logic directly
    from app.engine.panchang import engine_instance, MASA_LIST
    target_masa_index = MASA_LIST.index(masa)
    print(f"Target Masa: {masa} ({target_masa_index})")
    
    try:
        date = engine_instance.find_event_date(year, masa, paksha, tithi, lat, lon)
        print(f"Result: {date}")
        
        # Approximate check: Ganesh Chaturthi in 2025 is expected around Aug 27
        if date:
            print(f"Found date: {date}")
        else:
            print("Date not found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logic()
