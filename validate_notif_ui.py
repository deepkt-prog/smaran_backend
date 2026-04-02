def validate_notification_ui():
    print("Validating index.html for Notification UI...")
    path = "app/templates/index.html"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = [
        ('id="notif-bell"', "Bell Icon Container"),
        ('id="notif-badge"', "Notification Badge"),
        ('fetch(\'/notifications/\')', "Fetch Logic"),
        ('markAsRead', "Mark Read Logic"),
        ('.notification-wrapper', "CSS Styles")
    ]
    
    all_pass = True
    for snippet, desc in checks:
        if snippet in content:
            print(f"[PASS] Found {desc}")
        else:
            print(f"[FAIL] Missing {desc}")
            all_pass = False
            
    if all_pass:
        print("Notification UI validation passed.")
    else:
        print("Notification UI validation FAILED.")

if __name__ == "__main__":
    validate_notification_ui()
