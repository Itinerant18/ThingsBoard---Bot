# ThingsBoard Chatbot Integration

This project implements the backend and provides frontend snippets for a ThingsBoard Dashboard Chatbot.

## 1. Setup

### Prerequisites

- Python 3.8+
- A ThingsBoard account (URL, Username, Password)
- A Device ID in ThingsBoard to query.

### Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure Environment:

   - Rename `.env.example` to `.env`.
   - Edit `.env` and fill in your ThingsBoard URL, User, Password, and Device ID.

   _Note: The defaults in the code use the keys provided in your guide._

## 2. Running the Backend

Start the Flask server:

```bash
python app.py
```

This starts a server at `http://localhost:5000`.

### API Endpoints

- `POST /ask`: Accepts a JSON body `{"question": "battery status"}` and returns a natural language response with device data.

## 3. Connecting to a Chatbot Platform

### Botpress / Dialogflow

You need to configure your chatbot (Botpress Actions or Dialogflow Fulfillment) to make a POST request to this backend's `/ask` endpoint (tunneling via ngrok might be needed if running locally).

## 4. Embedding in ThingsBoard

1. Open your ThingsBoard Dashboard.
2. Add a new **Static HTML** widget.
3. Open `dashboard_widget.html` from this folder.
4. Copy the code for your chosen platform (Botpress or Dialogflow).
5. Paste it into the Widget's **HTML** tab.
6. Save and view the dashboard.
