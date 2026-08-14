"""
AquaPlant IoT Hub - Device Telemetry Emulator
Simulates IoT telemetry data for Aquariums and Indoor Plants.
Outputs JSON formatted telemetry payloads periodically.
"""

import json
import random
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests


class IoTDevice:
    """Base class for AquaPlant IoT Devices."""
    def __init__(self, device_id: str, device_type: str):
        self.device_id = device_id
        self.device_type = device_type

    def generate_metrics(self) -> Dict[str, Any]:
        """Abstract method to generate metrics dictionary."""
        raise NotImplementedError("Subclasses must implement generate_metrics()")

    def get_telemetry_payload(self) -> Dict[str, Any]:
        """Generates a complete telemetry payload."""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": self.generate_metrics(),
            "status": "NORMAL"
        }


class AquariumDevice(IoTDevice):
    """Simulates an Aquarium IoT device."""
    def __init__(self, device_id: str):
        super().__init__(device_id=device_id, device_type="AQUARIUM")

    def generate_metrics(self) -> Dict[str, Any]:
        return {
            "temperature_celsius": round(random.uniform(22.0, 28.0), 2),
            "ph_level": round(random.uniform(6.5, 7.8), 2),
            "tds_ppm": random.randint(150, 250)
        }


class PlantDevice(IoTDevice):
    """Simulates an Indoor Plant IoT device."""
    def __init__(self, device_id: str):
        super().__init__(device_id=device_id, device_type="PLANT")

    def generate_metrics(self) -> Dict[str, Any]:
        return {
            "temperature_celsius": round(random.uniform(18.0, 26.0), 2),
            "soil_moisture_percent": round(random.uniform(20.0, 90.0), 2),
            "light_level_lux": random.randint(1000, 5000)
        }


class AquaPlantIoTHubEmulator:
    """Manages the IoT device collection and telemetry broadcast loop."""
    def __init__(self):
        self.devices: List[IoTDevice] = [
            AquariumDevice("aquarium_01"),
            AquariumDevice("aquarium_02"),
            AquariumDevice("aquarium_03"),
            AquariumDevice("aquarium_04"),
            AquariumDevice("aquarium_05"),
            PlantDevice("plant_parlor_palm")
        ]

    def select_random_device(self) -> IoTDevice:
        """Selects a random device from the registered devices list."""
        return random.choice(self.devices)

    def publish_telemetry(self, payload: Dict[str, Any]) -> None:
        """Outputs formatted JSON to the console and posts payload to backend API server."""
        formatted_json = json.dumps(payload, indent=2)
        print("=== [TELEMETRY BROADCAST] ===")
        print(formatted_json)
        print("-" * 30 + "\n")

        api_url = "http://127.0.0.1:8000/api/v1/telemetry"
        try:
            response = requests.post(api_url, json=payload, timeout=5)
            if response.status_code == 201:
                response_data = response.json()
                server_status = response_data.get("status", "NORMAL")
                print(f"[HTTP SUCCESS] Telemetry for '{payload['device_id']}' posted to server. (Server Status: {server_status})")
            else:
                print(f"[HTTP WARNING] Server returned status code {response.status_code}.")
        except requests.exceptions.RequestException as err:
            print(f"[HTTP WARNING] Could not reach telemetry server at {api_url}: {err}")

    def run(self, interval_seconds: int = 30) -> None:
        """Runs the telemetry emulation loop indefinitely every interval_seconds."""
        print(f"Starting AquaPlant IoT Hub Emulator (Interval: {interval_seconds}s)...")
        print(f"Registered Devices: {[d.device_id for d in self.devices]}\n")
        try:
            while True:
                for device in self.devices:
                    payload = device.get_telemetry_payload()
                    self.publish_telemetry(payload)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nEmulator stopped by user.")


if __name__ == "__main__":
    emulator = AquaPlantIoTHubEmulator()
    emulator.run()





# import json
# import random
# import time
# from datetime import datetime, timezone
# from typing import Dict, Any, List
# import requests
#
#
# class IoTDevice:
#     """Base class for AquaPlant IoT Devices."""
#
#     def __init__(self, device_id: str, device_type: str):
#         self.device_id = device_id
#         self.device_type = device_type
#
#     def generate_metrics(self) -> Dict[str, Any]:
#         """Abstract method to generate metrics dictionary."""
#         raise NotImplementedError("Subclasses must implement generate_metrics()")
#
#     def get_telemetry_payload(self) -> Dict[str, Any]:
#         """Generates a complete telemetry payload."""
#         return {
#             "device_id": self.device_id,
#             "device_type": self.device_type,
#             "timestamp": datetime.now(timezone.utc).isoformat(),
#             "metrics": self.generate_metrics(),
#             "status": "NORMAL"
#         }
#
#
# class AquariumDevice(IoTDevice):
#     """Simulates an Aquarium IoT device."""
#
#     def __init__(self, device_id: str):
#         super().__init__(device_id=device_id, device_type="AQUARIUM")
#
#     def generate_metrics(self) -> Dict[str, Any]:
#         return {
#             "temperature_celsius": round(random.uniform(22.0, 28.0), 2),
#             "ph_level": round(random.uniform(6.5, 7.8), 2),
#             "tds_ppm": random.randint(150, 250)
#         }
#
#
# class PlantDevice(IoTDevice):
#     """Simulates an Indoor Plant IoT device."""
#
#     def __init__(self, device_id: str):
#         super().__init__(device_id=device_id, device_type="PLANT")
#
#     def generate_metrics(self) -> Dict[str, Any]:
#         return {
#             "temperature_celsius": round(random.uniform(18.0, 26.0), 2),
#             "soil_moisture_percent": round(random.uniform(20.0, 90.0), 2),
#             "light_level_lux": random.randint(1000, 5000)
#         }
#
#
# class AquaPlantIoTHubEmulator:
#     """Manages the IoT device collection and telemetry broadcast loop."""
#
#     def __init__(self):
#         self.devices: List[IoTDevice] = [
#             AquariumDevice("aquarium_01"),
#             AquariumDevice("aquarium_02"),
#             AquariumDevice("aquarium_03"),
#             AquariumDevice("aquarium_04"),
#             AquariumDevice("aquarium_05"),
#             PlantDevice("plant_parlor_palm")
#         ]
#
#     def select_random_device(self) -> IoTDevice:
#         """Selects a random device from the registered devices list."""
#         return random.choice(self.devices)
#
#     def publish_telemetry(self, payload: Dict[str, Any]) -> None:
#         """
#         Outputs formatted JSON to the console and posts payload to backend API server.
#         """
#         formatted_json = json.dumps(payload, indent=2)
#         print("=== [TELEMETRY BROADCAST] ===")
#         print(formatted_json)
#         print("-" * 30 + "\n")
#
#         # Transmit telemetry via HTTP POST request
#         api_url = "http://127.0.0.1:8000/api/v1/telemetry"
#         # try:
#         #     response = requests.post(api_url, json=payload, timeout=5)
#         #     if response.status_code == 201:
#         #         print(f"[HTTP SUCCESS] Telemetry for '{payload['device_id']}' posted to server.")
#         #     else:
#         #         print(f"[HTTP WARNING] Server returned status code {response.status_code}.")
#         # except requests.exceptions.RequestException as err:
#         #     print(f"[HTTP WARNING] Could not reach telemetry server at {api_url}: {err}")
#         try:
#             response = requests.post(api_url, json=payload, timeout=5)
#             if response.status_code == 201:
#                 # שליפת התשובה מהשרת כדי לראות את הסטטוס המעודכן
#                 response_data = response.json()
#                 server_status = response_data.get("status", "NORMAL")
#                 print(
#                     f"[HTTP SUCCESS] Telemetry for '{payload['device_id']}' posted to server. (Server Status: {server_status})")
#             else:
#                 print(f"[HTTP WARNING] Server returned status code {response.status_code}.")
#         except requests.exceptions.RequestException as err:
#             print(f"[HTTP WARNING] Could not reach telemetry server at {api_url}: {err}")
#
#     def run(self, interval_seconds: int = 30) -> None:
#         """Runs the telemetry emulation loop indefinitely every interval_seconds."""
#         print(f"Starting AquaPlant IoT Hub Emulator (Interval: {interval_seconds}s)...")
#         print(f"Registered Devices: {[d.device_id for d in self.devices]}\n")
#         try:
#             while True:
#                 for device in self.devices:
#                     payload = device.get_telemetry_payload()
#                     self.publish_telemetry(payload)
#                 time.sleep(interval_seconds)
#         except KeyboardInterrupt:
#             print("Emulator stopped by user.")
#
#
# if __name__ == "__main__":
#     emulator = AquaPlantIoTHubEmulator()
#     emulator.run()
