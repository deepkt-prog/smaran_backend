import os

# Google SSO Configuration
# Get these from https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") or "734621987525-fuh1fcc0944vim0ahqfl4vpv7ib59jrp.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or "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"

# Ensure this matches the URI you added in Google Console
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"

# Secret Key for Session (Important for SSO)
SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key-please-change"
