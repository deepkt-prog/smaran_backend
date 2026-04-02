import os

def validate_frontend():
    print("Validating index.html structure...")
    path = "app/templates/index.html"
    
    if not os.path.exists(path):
        print(f"[FAIL] File {path} not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('id="editModal"', "Edit Modal container"),
        ('id="edit_event_id"', "Edit Event ID field"),
        ('onclick="openEditModal(this)"', "Edit Button event handler"),
        ('function openEditModal(btn)', "JS function definition"),
        ('data-masa=', "Data attribute usage")
    ]
    
    all_pass = True
    for snippet, desc in checks:
        if snippet in content:
            print(f"[PASS] Found {desc}")
        else:
            print(f"[FAIL] Missing {desc}")
            all_pass = False
            
    if all_pass:
        print("Frontend validation passed successfully.")
    else:
        print("Frontend validation FAILED.")

if __name__ == "__main__":
    validate_frontend()
