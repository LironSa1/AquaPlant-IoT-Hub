"""
AquaPlant IoT Hub - FastAPI Backend Server
Provides REST API endpoints to ingest, process, and retrieve IoT device telemetry.
"""

import os
from typing import Dict, Any
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import requests
import uvicorn
from dotenv import load_dotenv


# ==========================================
# 1. Configuration & Setup
# ==========================================
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    print("WARNING: TELEGRAM_BOT_TOKEN not found in .env file!")

app = FastAPI(title="AquaPlant IoT Hub API")

SQLALCHEMY_DATABASE_URL = "sqlite:///./telemetry.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==========================================
# 2. Database Models (SQLAlchemy)
# ==========================================
class DBTelemetry(Base):
    __tablename__ = "telemetry_history"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    device_type = Column(String)
    timestamp = Column(String)
    metrics = Column(JSON)
    status = Column(String)

Base.metadata.create_all(bind=engine)


# ==========================================
# 3. Pydantic Models (Validation)
# ==========================================
class TelemetryData(BaseModel):
    device_id: str
    device_type: str
    timestamp: str
    metrics: Dict[str, Any]
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 4. Core Logic & Telegram Alerts
# ==========================================
def send_telegram_alert(message: str):
    """Sends an alert message via Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TELEGRAM] Token or Chat ID not configured, skipping alert.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[TELEGRAM ALERT SENT] {message}")
        else:
            print(f"[TELEGRAM ERROR] Status code: {response.status_code}")
    except Exception as e:
        print(f"[TELEGRAM ERROR] Failed to send message: {e}")


def process_and_check_anomalies(data: TelemetryData) -> str:
    """Checks for anomalies, sends alerts if necessary, and returns the updated status."""
    is_anomaly = False

    if data.device_type == "AQUARIUM":
        temp = data.metrics.get("temperature_celsius")
        if temp and (temp > 27.5 or temp < 22.5):
            is_anomaly = True
            send_telegram_alert(f"⚠️ Aquarium Alert! Abnormal temperature in '{data.device_id}': {temp}°C")

    elif data.device_type == "PLANT":
        moisture = data.metrics.get("soil_moisture_percent")
        if moisture and moisture < 25.0:
            is_anomaly = True
            send_telegram_alert(f"🥀 Plant Alert! Low soil moisture in '{data.device_id}': {moisture}%")

    return "ALERT" if is_anomaly else data.status


# ==========================================
# 5. API Routes
# ==========================================
@app.post("/api/v1/telemetry", status_code=201)
def receive_telemetry(data: TelemetryData, db: Session = Depends(get_db)):
    final_status = process_and_check_anomalies(data)

    db_record = DBTelemetry(
        device_id=data.device_id,
        device_type=data.device_type,
        timestamp=data.timestamp,
        metrics=data.metrics,
        status=final_status
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    print(f"[DB SAVED] Telemetry from '{data.device_id}' stored with status '{final_status}' (Record ID: {db_record.id}).")
    return {"message": "Telemetry saved to database successfully", "id": db_record.id, "status": final_status}


@app.get("/api/v1/telemetry")
def get_telemetry_history(db: Session = Depends(get_db), limit: int = 50):
    records = db.query(DBTelemetry).order_by(DBTelemetry.id.desc()).limit(limit).all()
    return records


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)





# from fastapi import FastAPI, Depends
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, JSON
# from sqlalchemy.orm import declarative_base, sessionmaker, Session
# import requests
# import uvicorn
# from typing import Dict, Any
# import os
# from dotenv import load_dotenv
#
# # ==========================================
# # 1. Configuration & Setup
# # ==========================================
# app = FastAPI(title="AquaPlant IoT Hub API")
#
# load_dotenv()
#
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
#
# if not TELEGRAM_BOT_TOKEN:
#     print("WARNING: TELEGRAM_BOT_TOKEN not found in .env file!")
#
# # הגדרת חיבור למסד הנתונים SQLite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./telemetry.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
#
# # ==========================================
# # 2. Database Models (SQLAlchemy)
# # ==========================================
# class DBTelemetry(Base):
#     __tablename__ = "telemetry_history"
#
#     id = Column(Integer, primary_key=True, index=True)
#     device_id = Column(String, index=True)
#     device_type = Column(String)
#     timestamp = Column(String)
#     metrics = Column(JSON)  # שומר את הנתונים כ-JSON
#     status = Column(String)
#
#
# # יצירת הטבלאות במסד הנתונים (אם לא קיימות)
# Base.metadata.create_all(bind=engine)
#
#
# # ==========================================
# # 3. Pydantic Models (Validation)
# # ==========================================
# class TelemetryData(BaseModel):
#     device_id: str
#     device_type: str
#     timestamp: str
#     metrics: Dict[str, Any]
#     status: str
#
#
# # פונקציית עזר לקבלת גישה למסד הנתונים
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# # ==========================================
# # 4. Core Logic & Telegram Alerts
# # ==========================================
# def send_telegram_alert(message: str):
#     """שולחת הודעה לבוט טלגרם"""
#     if TELEGRAM_BOT_TOKEN == "הכנס_את_הטוקן_כאן":
#         print("[TELEGRAM] Token not configured, skipping alert.")
#         return
#
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#     payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
#     try:
#         response = requests.post(url, json=payload, timeout=5)
#         if response.status_code == 200:
#             print(f"[TELEGRAM ALERT SENT] {message}")
#         else:
#             print(f"[TELEGRAM ERROR] Status code: {response.status_code}")
#     except Exception as e:
#         print(f"[TELEGRAM ERROR] Failed to send message: {e}")
#
#
# # def check_anomalies(data: TelemetryData):
# #     """בודקת חריגות בנתונים ומקפיצה התראות"""
# #     if data.device_type == "AQUARIUM":
# #         temp = data.metrics.get("temperature_celsius")
# #         if temp and (temp > 27.5 or temp < 22.5):
# #             send_telegram_alert(f"⚠️ התראת אקווריום! טמפרטורה חריגה נמדדה ב-'{data.device_id}': {temp}°C")
# #
# #     elif data.device_type == "PLANT":
# #         moisture = data.metrics.get("soil_moisture_percent")
# #         if moisture and moisture < 25.0:
# #             send_telegram_alert(f"🥀 התראת צמח! לחות האדמה של '{data.device_id}' נמוכה מאוד: {moisture}% - כדאי להשקות!")
#
# def process_and_check_anomalies(data: TelemetryData) -> str:
#     """
#     בודקת חריגות בנתונים.
#     אם יש חריגה - שולחת התראה לטלגרם ומחזירה 'ALERT'.
#     אם הכל תקין - מחזירה את הסטטוס המקורי.
#     """
#     is_anomaly = False
#
#     if data.device_type == "AQUARIUM":
#         temp = data.metrics.get("temperature_celsius")
#         if temp and (temp > 27.5 or temp < 22.5):
#             is_anomaly = True
#             send_telegram_alert(f"⚠️ התראת אקווריום! טמפרטורה חריגה נמדדה ב-'{data.device_id}': {temp}°C")
#
#     elif data.device_type == "PLANT":
#         moisture = data.metrics.get("soil_moisture_percent")
#         if moisture and moisture < 25.0:
#             is_anomaly = True
#             send_telegram_alert(f"🥀 התראת צמח! לחות האדמה של '{data.device_id}' נמוכה מאוד: {moisture}% - כדאי להשקות!")
#
#     return "ALERT" if is_anomaly else data.status
#
#
# # ==========================================
# # 5. API Routes
# # ==========================================
# @app.post("/api/v1/telemetry", status_code=201)
# def receive_telemetry(data: TelemetryData, db: Session = Depends(get_db)):
#     # א. נבדוק אם יש חריגות בנתונים
#     # check_anomalies(data)
#     final_status = process_and_check_anomalies(data)
#
#     # ב. נשמור את הנתונים למסד הנתונים SQLite
#     db_record = DBTelemetry(
#         device_id=data.device_id,
#         device_type=data.device_type,
#         timestamp=data.timestamp,
#         metrics=data.metrics,
#         # status=data.status
#         status=final_status
#     )
#     db.add(db_record)
#     db.commit()
#     db.refresh(db_record)
#
#     # print(f"[DB SAVED] Telemetry from '{data.device_id}' stored in SQLite (Record ID: {db_record.id}).")
#     print(f"[DB SAVED] Telemetry from '{data.device_id}' stored with status '{final_status}' (Record ID: {db_record.id}).")
#     return {"message": "Telemetry saved to database successfully", "id": db_record.id, "status": final_status}
#
#
# @app.get("/api/v1/telemetry")
# def get_telemetry_history(db: Session = Depends(get_db), limit: int = 50):
#     # שליפת הנתונים ממסד הנתונים
#     records = db.query(DBTelemetry).order_by(DBTelemetry.id.desc()).limit(limit).all()
#     return records
#
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
#
