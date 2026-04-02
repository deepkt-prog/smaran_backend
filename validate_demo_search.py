def validate_demo_search():
    print("Validating index.html for Demo Search...")
    path = "app/templates/index.html"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('id="city_search_demo"', "Demo Search Input"),
        ('id="search_results_demo"', "Results Container"),
        ('searchInputDemo.addEventListener', "Demo Search Logic")
    ]
    
    all_pass = True
    for snippet, desc in checks:
        if snippet in content:
            print(f"[PASS] Found {desc}")
        else:
            print(f"[FAIL] Missing {desc}")
            all_pass = False
            
    if all_pass:
        print("Demo Search feature validation passed.")
    else:
        print("Demo Search feature validation FAILED.")

if __name__ == "__main__":
    validate_demo_search()
