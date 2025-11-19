"""
Script to generate test sensor data for Phase 1
"""
import sys
import time
import requests
from app.services.simulator import sensor_simulator

API_URL = "http://localhost:8000/api/v1"

def generate_test_data(count=50):
    """Generate and ingest test sensor data"""
    print(f"Generating {count} sensor readings...")
    
    readings = []
    for i in range(count):
        reading = sensor_simulator.generate_reading()
        readings.append({
            "measurement": reading.measurement,
            "device_id": reading.device_id,
            "sensor_id": reading.sensor_id,
            "value": reading.value,
            "timestamp": reading.timestamp,
            "tags": reading.tags
        })
        
        # Spread timestamps over the last hour
        if i > 0:
            readings[-1]["timestamp"] = int(time.time()) - (count - i) * 60
    
    # Ingest batch
    try:
        response = requests.post(
            f"{API_URL}/sensors/ingest/batch",
            json=readings
        )
        response.raise_for_status()
        print(f"✓ Successfully ingested {count} sensor readings")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Error ingesting data: {e}")
        return False

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    success = generate_test_data(count)
    sys.exit(0 if success else 1)

