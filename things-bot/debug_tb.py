import os
import json
from dotenv import load_dotenv
from tb_client import ThingsBoardClient

# Load env variables
load_dotenv()

TB_URL = os.getenv('TB_URL', 'http://demo.thingsboard.io')
TB_USER = os.getenv('TB_USER')
TB_PASS = os.getenv('TB_PASSWORD')
DEVICE_ID = os.getenv('DEVICE_ID')

print(f"Connecting to {TB_URL} as {TB_USER} for device {DEVICE_ID}...")

client = ThingsBoardClient(TB_URL, TB_USER, TB_PASS)
if not client.login():
    print("LOGIN FAILED")
    exit(1)

print("LOGIN SUCCESS")

# define keys
ATTRIBUTE_KEYS = [
    "Dahua_NVR_cameraInfo", "dexter_config", "Hikvision_NVR_cameraInfo", 
    "Hikvision_NVR_deviceID", "Hikvision_NVR_deviceName", "Hikvision_NVR_deviceType", 
    "Hikvision_NVR_firmwareVersion", "Hikvision_NVR_hardwareVersion", 
    "Hikvision_NVR_HDDInfo", "Hikvision_NVR_macAddress"
]

TELEMETRY_KEYS = [
    "ac_status", "accessControlLastHour", "alarmCount", "alerts", 
    "arrLat", "arrLon", "attribute", "basLastHour", "battery_status", 
    "camera_disconnect_last"
]

print("\n--- FETCHING CLIENT SCOPE ATTRIBUTES ---")
data_client = client.get_attributes(DEVICE_ID, scope='CLIENT_SCOPE', keys=ATTRIBUTE_KEYS)
print(json.dumps(data_client, indent=2))

print("\n--- FETCHING SERVER SCOPE ATTRIBUTES ---")
data_server = client.get_attributes(DEVICE_ID, scope='SERVER_SCOPE', keys=ATTRIBUTE_KEYS)
print(json.dumps(data_server, indent=2))

print("\n--- FETCHING SHARED SCOPE ATTRIBUTES ---")
data_shared = client.get_attributes(DEVICE_ID, scope='SHARED_SCOPE', keys=ATTRIBUTE_KEYS)
print(json.dumps(data_shared, indent=2))

print("\n--- FETCHING TELEMETRY ---")
data_telemetry = client.get_telemetry(DEVICE_ID, keys=TELEMETRY_KEYS)
print(json.dumps(data_telemetry, indent=2))
