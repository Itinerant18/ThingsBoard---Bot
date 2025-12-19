import requests
import json

# Hardcoded for test
URL = "https://demo.thingsboard.io"
USER = "rnd1@seple.in"
PASS = "@bcde2025"

print(f"Attempting login to {URL} with {USER}")

try:
    resp = requests.post(f"{URL}/api/auth/login", json={"username": USER, "password": PASS})
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("LOGIN SUCCESS!")
        token = resp.json().get("token")
        print(f"Token received: {token[:10]}...")
    else:
        print(f"Login Failed: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
