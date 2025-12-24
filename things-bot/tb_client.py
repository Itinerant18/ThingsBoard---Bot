import requests
import time
import os

class ThingsBoardClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = 0
        
        # Check if the provided 'password' is actually a Bearer Token (very long string)
        if len(password) > 150: 
            print("[TB] Detected static JWT token in configuration.")
            self.token = password
            self.token_expiry = time.time() + (24 * 3600) * 365 # Assume valid for a year if static
            self.is_static_token = True
        else:
            print("[TB] Detected password. Will perform auto-login to fetch token.")
            self.is_static_token = False

    def login(self):
        """Authenticates with ThingsBoard and gets a fresh JWT token."""
        if self.is_static_token:
            return True

        url = f"{self.base_url}/api/auth/login"
        payload = {"username": self.username, "password": self.password}
        
        print(f"[TB] Logging in to {self.base_url} as {self.username}...")
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            # Set expiry (default TB token is 2.5 hours, refresh safely after 2 hours)
            self.token_expiry = time.time() + 7200 
            print(f"[TB] Login Successful! Token acquired (Starts with: {self.token[:10]}...)")
            return True
        except Exception as e:
            print(f"[TB] Login Failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[TB] Server Response: {e.response.text}")
            return False

    def get_header(self):
        """Returns the auth header, ensuring token is valid."""
        # Refresh if we have no token OR it's expired/about to expire (within 5 mins)
        if not self.token or (not self.is_static_token and time.time() > self.token_expiry - 300):
            print("[TB] Token expired or missing. Refreshing...")
            if not self.login():
                raise Exception("Unable to authenticate with ThingsBoard API.")
                
        return {"X-Authorization": f"Bearer {self.token}"}

    def get_attributes(self, device_id, scope='SERVER_SCOPE', keys=None):
        """Fetch device attributes."""
        url = f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/attributes/{scope}"
        if keys:
            url += f"?keys={','.join(keys)}"
        
        try:
            print(f"DEBUG: Fetching Attributes from {url}")
            response = requests.get(url, headers=self.get_header())
            print(f"DEBUG: Status {response.status_code}")
            # print(f"DEBUG: Response {response.text}") # Uncomment if response is huge
            response.raise_for_status()
            return response.json() # Returns List of {key, value, lastUpdateTs}
        except Exception as e:
            print(f"Error fetching attributes: {e}")
            return []

    def get_telemetry(self, device_id, keys=None):
        if not self.token: self.login()
        url =f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        if keys:
            url += f"?keys={','.join(keys)}"
        
        headers = {"X-Authorization": f"Bearer {self.token}"}
        print(f"DEBUG: Fetching Telemetry from {url}") 
        resp = requests.get(url, headers=headers)
        print(f"DEBUG: Status {resp.status_code}")
        
        if resp.status_code == 200:
            return resp.json()
        return {}

    def get_history(self, device_id, keys, start_ts, end_ts, limit=100):
        """Fetch historical timeseries data."""
        if not self.token: self.login()
        # API expects comma separated keys
        keys_str = ','.join(keys)
        url = f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        params = {
            'keys': keys_str,
            'startTs': int(start_ts * 1000), # Unix timestamp in ms
            'endTs': int(end_ts * 1000),
            'limit': limit
        }
        headers = {"X-Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Error fetching history: {e}")
        return {}

    def get_keys(self, device_id, data_type='timeseries'):
        """
        Fetch list of available keys for the device.
        data_type: 'timeseries' or 'attributes'
        """
        if not self.token: self.login()
        url = f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/keys/{data_type}"
        headers = {"X-Authorization": f"Bearer {self.token}"}
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json() # Returns List[str] e.g. ['temp', 'batt']
        except Exception as e:
            print(f"Error fetching keys ({data_type}): {e}")
        return []
