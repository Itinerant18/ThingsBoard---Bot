# ThingsBoard AI Assistant Project Documentation

This document provides a comprehensive overview of the ThingsBoard AI Assistant project. It includes the project structure, detailed file descriptions, workflow architecture, and setup instructions.

## 1. Project Overview

The **ThingsBoard AI Assistant** is a smart integration that brings conversational AI capabilities to a ThingsBoard IoT dashboard. It allows users to:

1.  **Chat with their Devices**: Ask natural language questions about device status (telemetry and attributes).
2.  **Visualiza Data**: Automatically generate charts based on user queries (e.g., "Show me the battery trend").
3.  **Proactive Alerts**: Receive proactive warnings about critical states (e.g., Low Battery, Active Alarms).

The system consists of a Python Flask backend that acts as a middleware between the user (via a web widget) and the ThingsBoard API + OpenAI API.

## 2. Project Structure

The codebase is organized as follows:

```
c:\Debayan\tb-ai-assistant\
├── .github\                    # GitHub configuration
│   └── instructions\           # Instructions for CI/CD or dev environments
├── things-bot\                 # Main Application Source Code
│   ├── templates\              # Flask HTML Templates
│   │   └── index.html          # Main Chat Interface (Neural Link UI)
│   ├── .env                    # Environment Variables (Secrets) - NOT TRACKED IN GIT
│   ├── .env.example            # Example Environment Variables template
│   ├── app.py                  # Main Flask Application Entry Point
│   ├── dashboard_widget.html   # HTML snippet for embedding in ThingsBoard
│   ├── debug_tb.py             # Script to debug ThingsBoard connection & data fetching
│   ├── debug_device_token.py   # Utility to debug token issues
│   ├── debug_https.py          # Utility to debug HTTPS connections
│   ├── requirements.txt        # Python dependencies
│   ├── tb_client.py            # API Client wrapper for ThingsBoard REST API
│   ├── verify_parser.py        # Utility to test JSON parsing logic
│   └── README.md               # Basic quickstart guide
└── .gitignore                  # Git ignore rules
```

## 3. Workflow & Architecture

### High-Level Data Flow

1.  **User Interaction**: The user types a question into the Chat Widget embedded in ThingsBoard.
2.  **Request Handling**: The request is sent to the Flask Backend (`/ask` endpoint).
3.  **Data Discovery**:
    - The backend uses `tb_client.py` to fetch the _current_ state of the device from ThingsBoard.
    - It fetches **Attributes** (Server, Client, Shared scopes) and **Telemetry** (Timeseries data).
4.  **Context Preparation**:
    - The `app.py` script cleans and formats this data into a JSON context.
    - Timestamps are converted to human-readable formats.
5.  **Intent Recognition (AI)**:
    - The backend asks OpenAI to determine if a chart is needed.
    - If yes, it fetches historical data using `get_history` and prepares chart data.
6.  **Response Generation (AI)**:
    - The backend sends the _User Question_ + _Device Context_ + _System Prompt_ to OpenAI (GPT-3.5/4).
    - The AI generates a natural language answer based _only_ on the provided real-time data.
7.  **Response Delivery**: The JSON response (Answer + Chart Data) is sent back to the frontend widget for display.

### Component Details

#### 1. Backend (`app.py`)

- **Role**: Orchestrator.
- **Key Dependencies**: `flask`, `openai`, `tb_client`.
- **Key Functions**:
  - `prepare_context_data()`: Flattens complex JSON attributes into a readable format for the LLM.
  - `/ask`: Main API endpoint.
  - `/alerts`: Endpoint polled by the frontend to check for critical conditions (Low Battery < 20%, Active Alarms).

#### 2. ThingsBoard Client (`tb_client.py`)

- **Role**: Data Fetcher.
- **Features**:
  - Handles Authentication (JWT Token management).
  - `get_telemetry()`: Fetches latest timeseries.
  - `get_attributes()`: Fetches device attributes.
  - `get_history()`: Fetches historical data for charting.
  - `get_keys()`: Dynamically discovers available data keys.

#### 3. Frontend (`templates/index.html`)

- **Design**: "Neural Link" aesthetic (Dark mode, glassmorphism, neon accents).
- **Features**:
  - Real-time chat interface.
  - Dynamic Chart.js rendering.
  - Markdown rendering of AI responses.
  - Proactive Alert banner.
  - Voice Input (Microphone support).

#### 4. Embedding (`dashboard_widget.html`)

- **Role**: Integration point.
- **Usage**: Detailed `<iframe>` code to be pasted into a "Static HTML" widget in ThingsBoard. It loads the Flask app.

## 4. Setup Instructions

### Prerequisites

- Python 3.8 or higher.
- ThingsBoard Account (Cloud or Local).
- OpenAI API Key.

### Installation

1.  **Clone the Repository**:

    ```bash
    git clone https://github.com/Itinerant18/ThingsBoard---Bot.git
    cd ThingsBoard---Bot/things-bot
    ```

2.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file in the `things-bot` directory with the following credentials:
    ```env
    TB_URL="https://thingsboard.cloud"
    TB_USER="your_username@example.com"
    TB_PASSWORD="your_password_or_token"
    DEVICE_ID="your_device_guid"
    OPENAI_API_KEY="sk-..."
    ```

### Running the Application

1.  **Start the Backend**:

    ```bash
    python app.py
    ```

    The server will start at `http://localhost:5000`.

2.  **Verify Connection**:
    Run the debug script to ensure the bot can talk to ThingsBoard:

    ```bash
    python debug_tb.py
    ```

3.  **Embed in ThingsBoard**:
    - Copy the content of `dashboard_widget.html`.
    - Go to your ThingsBoard Dashboard.
    - Add a **Static HTML** widget.
    - Paste the code into the HTML section.
    - Save and Resize.

## 5. Usage Guide

- **Ask Questions**: "What is the current battery level?", "Is the camera online?", "Show me the configuration".
- **Request Charts**: "Chart the temperature", "Show me a graph of the battery".
- **Check Alerts**: The top banner will turn Red if critical alerts are detected.

## 6. Troubleshooting

- **Login Failed**: Check credentials in `.env`. If using a JWT token in `TB_PASSWORD`, ensure it hasn't expired.
- **No Data**: Run `debug_tb.py` to see if the API returns keys. Ensure your user has `READ` permission for the device.
- **OpenAI Errors**: Check your API Key and Credit balance.
- **CORS Issues**: If the widget doesn't load in ThingsBoard, ensure `flask-cors` is installed and enabled (it is by default in `app.py`).
