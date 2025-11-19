"""
Sensor data simulator service (Phase 1)
Implements exact requirements from project specification
"""
import random
import time
from typing import List
from app.models.sensor import SensorReading


class SensorSimulator:
    """Simulates IoT sensor data according to project requirements"""
    
    def __init__(self):
        # Smart home devices with sensors as per requirements
        self.devices = [
            {"device_id": "smart_home_001", "location": "living_room"},
            {"device_id": "smart_home_002", "location": "bedroom"},
            {"device_id": "smart_home_003", "location": "kitchen"},
        ]
        
        # Required sensor types per requirements
        self.sensor_types = ["temperature", "light", "motion"]
    
    def generate_reading(
        self,
        device_id: str = None,
        sensor_type: str = None,
    ) -> SensorReading:
        """
        Generate a simulated sensor reading according to project requirements
        
        Args:
            device_id: Specific device (random if not provided)
            sensor_type: Specific sensor type (random if not provided)
        
        Returns:
            SensorReading with value in required range
        """
        # Select random device if not specified
        if not device_id:
            device = random.choice(self.devices)
            device_id = device["device_id"]
        else:
            device = next((d for d in self.devices if d["device_id"] == device_id), self.devices[0])
        
        # Select random sensor type if not specified
        if not sensor_type:
            sensor_type = random.choice(self.sensor_types)
        
        # Generate value based on sensor type according to requirements
        if sensor_type == "temperature":
            # Temperature: 15-40 °C (as per requirements)
            value = round(random.uniform(15.0, 40.0), 1)
        elif sensor_type == "light":
            # Light: 0-100 (0 = dark, 100 = bright) (as per requirements)
            value = round(random.uniform(0.0, 100.0), 1)
        elif sensor_type == "motion":
            # Motion: 0 (no motion) or 1 (motion detected) (as per requirements)
            value = random.choice([0, 1])
        else:
            # Default fallback
            value = round(random.uniform(0.0, 100.0), 1)
        
        return SensorReading(
            measurement=sensor_type,
            device_id=device_id,
            sensor_id=f"{device_id}_{sensor_type}",
            value=value,
            timestamp=int(time.time()),
            tags={"location": device.get("location", "unknown")}
        )
    
    def generate_all_sensor_readings(self, device_id: str = None) -> List[SensorReading]:
        """
        Generate readings for all sensor types for a device
        
        Args:
            device_id: Device ID (random if not provided)
        
        Returns:
            List of SensorReading for all sensor types
        """
        if not device_id:
            device = random.choice(self.devices)
            device_id = device["device_id"]
        
        readings = []
        for sensor_type in self.sensor_types:
            readings.append(self.generate_reading(device_id=device_id, sensor_type=sensor_type))
        
        return readings
    
    def generate_batch(self, count: int = 10) -> List[SensorReading]:
        """Generate a batch of sensor readings"""
        return [self.generate_reading() for _ in range(count)]


# Global instance
sensor_simulator = SensorSimulator()

