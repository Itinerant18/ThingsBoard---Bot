import requests
import json
import os

# User provided these in the prompt
ACCESS_TOKEN = "KOHIMA-UN-ID" 
TB_URL = "http://demo.thingsboard.io"

print(f"Testing Device API with Token: {ACCESS_TOKEN}")

# 1. Fetch Attributes (Client Scope)
url_attr = f"{TB_URL}/api/v1/{ACCESS_TOKEN}/attributes?clientKeys=Hikvision_NVR_deviceName,dexter_config"

try:
    print(f"GET {url_attr}")
    resp = requests.get(url_attr)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")

# 2. Fetch Telemetry
url_tel = f"{TB_URL}/api/v1/{ACCESS_TOKEN}/telemetry?keys=battery_status"
try:
    print(f"GET {url_tel}")
    resp = requests.get(url_tel)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
