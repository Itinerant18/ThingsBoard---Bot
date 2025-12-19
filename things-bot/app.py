from flask import Flask, request, jsonify, render_template
from tb_client import ThingsBoardClient
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load OpenAI Client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
TB_URL = os.getenv('TB_URL', 'http://demo.thingsboard.io')
TB_USER = os.getenv('TB_USER')
TB_PASS = os.getenv('TB_PASSWORD')
DEVICE_ID = os.getenv('DEVICE_ID')

# Initialize ThingsBoard Client
tb_client = ThingsBoardClient(TB_URL, TB_USER, TB_PASS)

# Keys defined in the user request
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

def clean_json_string(s):
    """Attempt to parse a string as JSON, or return original if not."""
    if not isinstance(s, str): return s
    try:
        return json.loads(s)
    except:
        return s

def prepare_context_data(attributes, telemetry):
    """Flatten and clean data for LLM Context, adding human-readable timestamps."""
    context = {}
    
    # Process Attributes
    for item in attributes:
        key = item.get('key')
        val = item.get('value')
        # Try to clean if it's a string, else use as is
        context[key] = clean_json_string(val)
        
    # Process Telemetry
    for key, values in telemetry.items():
        if values and len(values) > 0:
            item = values[0]
            val = item.get('value')
            ts = item.get('ts')
            
            # Convert TS to readable string
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts/1000))
            
            clean_val = clean_json_string(val)
            
            # Store value
            context[key] = clean_val
            # Store metadata for AI to know how fresh data is
            context[f"{key}_updated_at"] = time_str
            
    return context

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/token', methods=['GET'])
def get_tb_token():
    """Helper to fetch and view the current ThingsBoard Token."""
    # Force a login attempt
    success = tb_client.login()
    if success:
        return jsonify({
            "status": "success",
            "token": tb_client.token,
            "expiry_at": tb_client.token_expiry
        })
    else:
        return jsonify({"status": "error", "message": "Failed to login to ThingsBoard"}), 401
    
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/alerts', methods=['GET'])
def check_alerts():
    """Proactive alert check endpoint."""
    try:
        telemetry = tb_client.get_telemetry(DEVICE_ID, keys=['alarmCount', 'battery_status'])
        
        alerts = []
        
        # Check active alarms
        alarms_data = telemetry.get('alarmCount', [{'value': 0}])
        if alarms_data:
             alarms = alarms_data[0]['value']
             if int(alarms) > 0:
                alerts.append(f"Warning: {alarms} active alarms detected!")
            
        # Check Battery
        batt_data = telemetry.get('battery_status', [{'value': 0}])
        if batt_data:
            batt = batt_data[0]['value']
            # battery_status might be a JSON string sometimes? Handled by clean_json_string elsewhere but here we want raw check
            # logic usually expects number. If it is string "14.0", int conversion might be needed or handled in get_telemetry
            # For safety, let's just skipp complex logic here and rely on AI for Q&A mostly
            try:
                if float(batt) < 20: 
                    alerts.append(f"Critical: Battery is low ({batt}%)")
            except: pass
            
        if alerts:
            return jsonify({"has_alert": True, "message": " | ".join(alerts)})
            
        return jsonify({"has_alert": False})
    except Exception as e:
        print(f"Alert Check Error: {e}")
        return jsonify({"has_alert": False})


@app.route('/ask', methods=['POST'])
def ask_device_data():
    """
    Endpoint to process natural language queries about the specific device using OpenAI.
    """
    data = request.json
    question = data.get('question', '').lower()
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    # 1. Dynamic Data Discovery
    # Fetch ALL available keys dynamically
    ts_keys = tb_client.get_keys(DEVICE_ID, 'timeseries')
    
    # Fetch Attributes (No keys needed to get all usually, but for safety lets try explicit scopes)
    attr_client = tb_client.get_attributes(DEVICE_ID, keys=None, scope='CLIENT_SCOPE')
    attr_server = tb_client.get_attributes(DEVICE_ID, keys=None, scope='SERVER_SCOPE')
    attr_shared = tb_client.get_attributes(DEVICE_ID, keys=None, scope='SHARED_SCOPE')
    attributes = attr_client + attr_server + attr_shared
    
    # Fetch Telemetry (All detected keys)
    # If list is huge, we might truncate, but for single device usually < 50 keys
    telemetry = tb_client.get_telemetry(DEVICE_ID, keys=ts_keys)
    
    # 2. Prepare Context
    context_data = prepare_context_data(attributes, telemetry)
    
    # 3. Check for Chart Intent
    chart_data = None
    chart_key = None
    if any(k in question for k in ['chart', 'graph', 'trend', 'history', 'plot']):
        try:
            # Ask AI which key to plot from the available keys
            valid_keys = ", ".join(ts_keys)
            prompt = f"User asked: '{question}'. Available keys: [{valid_keys}]. Identify the single most relevant telemetry key to plot. Return ONLY the key name. If none match, return 'None'."
            
            key_resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            extracted_key = key_resp.choices[0].message.content.strip()
            
            if extracted_key in ts_keys:
                chart_key = extracted_key
                # Fetch last 24h history
                end_ts = time.time()
                start_ts = end_ts - (24 * 3600)
                history = tb_client.get_history(DEVICE_ID, [extracted_key], start_ts, end_ts)
                
                # Format for frontend
                if extracted_key in history:
                    chart_data = {
                        "label": extracted_key,
                        "points": [{"t": p['ts'], "y": p['value']} for p in history[extracted_key]]
                    }
        except Exception as e:
            print(f"Chart extraction error: {e}")

    # 4. Generate Answer with OpenAI
    try:
        system_prompt = (
            "You are an intelligent and friendly IoT Device Assistant. "
            "You have access to the COMPLETE real-time state of the device in JSON format, including timestamps for when data was last updated. "
            
            "**Your Instructions:**\n"
            "1. **Be User-Friendly**: Translate technical keys into normal English (e.g., 'ac_status' -> 'AC Power Status', 'batt' -> 'Battery').\n"
            "2. **Summarize**: If the answer involves a large JSON object (like camera lists or configs), do NOT dump the raw JSON. Summarize it (e.g., 'There are 3 cameras online: Cam1, Cam2...').\n"
            "3. **Check Timestamps**: If asked about status, mention if the data looks old or stale based on the '_updated_at' fields provided.\n"
            "4. **Format**: Use Markdown (bolding, lists) to make the response easy to read.\n"
            "5. **Context**: Use the provided context data effectively. If the answer is not in the data, frankly admit it."
        )
        if chart_key:
            system_prompt += f"\n\n[NOTE]: A line chart for '{chart_key}' has been generated and shown to the user. You should mention: 'I've plotted the trend for {chart_key} below.'"

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Device Context: {json.dumps(context_data)}\n\nUser Question: {question}"}
            ]
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")
        answer = "I'm sorry, I encountered an error generating the response from the AI model."

    return jsonify({
        "response": answer,
        "data_used": context_data,
        "chart": chart_data
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
