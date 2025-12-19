import json

# Data strings provided by the user in the prompt
DEXTER_CONFIG_STR = '{"powerzone":"{1 1 6 0 1 2 0 1 3 0 1 4 1 1 5 0 1 6 0 1 1 0 1 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0}","zone":"{1 1 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0}","brand":"SEPLE","branch":"SDF","modem_parameter":{"client_id":"KOHIMA-CL-ID","user_name":"KOHIMA-UN-ID","password":"KOHIMA-PWD","gsm_modem_mode":"physical","network_type":"gsm","device_name":"BOI-KOHIMA"},"integration":[{"id":1,"device_type":"HikvisionNVR1","ip_address":"192.168.1.168","username":"admin","password":"hik@8234","port":8080,"camera_ip":[{"ip_address":"192.168.1.18","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.64","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.7","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.8","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.4","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.3","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.5","username":"admin","password":"hik@8234"},{"ip_address":"192.168.1.6","username":"admin","password":"hik@8234"},{"username":"admin","password":"hik@8234"},{"username":"admin","password":"hik@8234"}]},{"id":2,"device_type":"DahuaNVR1","ip_address":"192.168.0.102","username":"admin","password":"Sepl@1984","port":8080,"camera_ip":[]},{"id":3,"device_type":"HikvisionBioMetric1","ip_address":"192.168.0.27","username":"sepl","password":"sepl1984","port":8082},{"id":4,"device_type":"CP_PlusNVR1","ip_address":"192.168.0.102","username":"admin","password":"Sepl@1984","port":8080}],"active_device_parameter":{"active_integration_hikvision_nvr":1,"active_integration_hikvision_biometric":0,"active_integration_dahua_nvr":0,"active_integration_cp_plus_nvr":0},"active_parameter":{"active_integration_on_off_bit":1},"network_parameter":{"e-SIM Enable/Disable":"True","Network Selection for e-SIM":"LTE","Enable/Disable GNSS":"True","Alert Types (SMS)":"Vibrate","Notification Schedule":"Every hour","Enable/Disable for Network LED Status":"True","Enable/Disable for Wireless LAN":"False","APN Settings":"internet","Network Test":"False","Enable/Disable GSM":"True","Enable/Disable IP Module":"False","DNS Setup":"Automatic","Enable/Disable Static/dynamic":"Static","IPv4/IPv6 Selection":"IPv4","reset_to_dhcp":"True","Set Port Number":"8080","preferred_dns_server":"8.8.8.8","alternate_dns_server":"8.8.4.4","Subnet mask":"255.255.255.0","Set IP Address":"192.168.1.46","Gateway":"192.168.1.1"},"batt":"67","timestamp":"2025-12-16T15:40:42"}'

HIK_CAM_INFO_STR = '{"1":{"Channel Name":"Camera 01","Device Index":"c3701e2b-4d5f-4fbb-995d-1d72117a2d71","IP Address":"192.168.1.18","Proxy Protocol":"HIKVISION","Streaming Channel Name":"101","Video Resolution":"1920x1080","Max Frame Rate":"0"},"2":{"Channel Name":"Camera 01","Device Index":"N/A","IP Address":"192.168.1.64","Proxy Protocol":"HIKVISION"}}'

def clean_json_string(s):
    if not s or s == "NA": return {}
    try:
        return json.loads(s)
    except:
        return {}

print("--- TESTING DEXTER CONFIG ---")
dexter = clean_json_string(DEXTER_CONFIG_STR)
print(f"Parsed Successfully: {isinstance(dexter, dict)}")
print(f"Battery: {dexter.get('batt')}")
print(f"IP: {dexter.get('network_parameter', {}).get('Set IP Address')}")

print("\n--- TESTING HIK CAM INFO ---")
cam = clean_json_string(HIK_CAM_INFO_STR)
print(f"Parsed Successfully: {isinstance(cam, dict)}")
print(f"Cam 1 IP: {cam.get('1', {}).get('IP Address')}")
