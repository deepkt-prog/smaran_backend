def validate_search():
    print("Validating signup.html for City Search...")
    path = "app/templates/signup.html"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('id="city_search"', "Search Input"),
        ('id="search_results"', "Results Container"),
        ('nominatim.openstreetmap.org', "Nominatim API URL"),
        ('document.getElementById(\'lat\').value = place.lat', "Coordinate Filling Logic")
    ]
    
    all_pass = True
    for snippet, desc in checks:
        if snippet in content:
            print(f"[PASS] Found {desc}")
        else:
            print(f"[FAIL] Missing {desc}")
            all_pass = False
            
    if all_pass:
        print("Search feature validation passed.")
    else:
        print("Search feature validation FAILED.")

if __name__ == "__main__":
    validate_search()
