def validate_localization():
    print("Validating Localization files...")
    
    # Check i18n
    try:
        from app.i18n import TRANSLATIONS
        if 'hi' in TRANSLATIONS and 'welcome' in TRANSLATIONS['hi']:
            print("[PASS] i18n.py loaded with Hindi translations.")
        else:
            print("[FAIL] i18n.py missing Hindi.")
    except Exception as e:
        print(f"[FAIL] Error loading i18n.py: {e}")

    # Check index.html for t['welcome']
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
        if "{{ t['welcome'] }}" in html:
            print("[PASS] index.html uses t['welcome']")
        else:
            print("[FAIL] index.html missing dynamic welcome text")
            
        if '<select name="language"' in html:
            print("[PASS] Language switcher detected")
        else:
            print("[FAIL] Language switcher missing")

if __name__ == "__main__":
    validate_localization()
