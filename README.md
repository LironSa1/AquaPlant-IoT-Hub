# AquaPlant IoT Hub

AquaPlant IoT Hub is a lightweight Internet of Things (IoT) simulation and processing system. It is designed to ingest, analyze, and alert on telemetry data from smart environments. 

This project demonstrates core backend and architectural skills—ideal for Fullstack and DevOps workflows—including REST API development, database integration, external API communication, and decoupled system design.

## Project Architecture
The system is decoupled into two primary components:
1. **IoT Device Emulator (`emulator.py`)**: A Python script that simulates various sensors (temperature, pH, soil moisture) and periodically broadcasts JSON payloads via HTTP POST requests.
2. **FastAPI Backend Server (`main.py`)**: A high-performance REST API server that receives the telemetry, analyzes it for anomalies, saves records to a local SQLite database, and dispatches Telegram alerts when critical thresholds are breached.

## Technologies Used
* **Python 3.10+**
* **FastAPI & Uvicorn** (High-performance API framework)
* **SQLAlchemy** (ORM for SQLite database interaction)
* **Pydantic** (Data validation and parsing)
* **python-dotenv** (Environment variable management)

## Setup and Installation

1. Clone the repository:
    git clone https://github.com/Liron/AquaPlant-IoT-Hub.git
    cd AquaPlant-IoT-Hub

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
    pip install -r requirements.txt

## Configuration
Create a `.env` file in the root directory (do not commit this to version control) and add your Telegram bot credentials:

    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
    TELEGRAM_CHAT_ID=your_chat_id_here

## Running the System

Start the API Server:
    python main.py

*(The server will start on http://127.0.0.1:8000. A SQLite database `telemetry.db` will be created automatically.)*

Start the IoT Emulator (in a separate terminal):
    python emulator.py