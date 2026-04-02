from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_pwa_assets():
    print("Testing PWA Assets...")
    
    # 1. Manifest
    resp = client.get("/static/manifest.json")
    if resp.status_code == 200:
        try:
            data = resp.json()
            if data['name'] == "Smaran" and len(data['icons']) == 2:
                print("[PASS] manifest.json is valid.")
            else:
                print("[FAIL] manifest.json content incorrect.")
        except json.JSONDecodeError:
            print("[FAIL] manifest.json is not valid JSON.")
    else:
        print(f"[FAIL] manifest.json returned {resp.status_code}")

    # 2. Service Worker
    resp = client.get("/static/sw.js")
    if resp.status_code == 200:
        if "CACHE_NAME" in resp.text:
            print("[PASS] sw.js is served correctly.")
        else:
            print("[FAIL] sw.js content incorrect.")
    else:
        print(f"[FAIL] sw.js returned {resp.status_code}")

    # 3. Icons
    resp = client.get("/static/icons/icon-192.png")
    if resp.status_code == 200:
        print("[PASS] Icon 192 served.")
    else:
        print(f"[FAIL] Icon 192 missing. {resp.status_code}")

if __name__ == "__main__":
    test_pwa_assets()
