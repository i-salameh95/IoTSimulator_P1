"""
Actuator controller service
Implements decision-making rules as per project requirements
"""
import time
from typing import Dict, List

from app.models.actuator import ActuatorState
from app.models.sensor import SensorReading
from app.core.logger import iot_logger


class ActuatorController:
    """Central computer (controller) that makes decisions based on sensor data"""

    FAN_THRESHOLD = 30.0
    LIGHT_THRESHOLD = 20.0
    ALARM_THRESHOLD = 37.0

    def __init__(self):
        # Track actuator states per device (actuator_id -> state)
        self.actuators: Dict[str, str] = {}

    def process_sensor_readings(self, readings: List[SensorReading]) -> List[ActuatorState]:
        """
        Process sensor readings and make decisions based on rules

        Rules:
        - If temperature > FAN_THRESHOLD, turn on fan
        - If motion detected and light < LIGHT_THRESHOLD, turn on light
        - If motion detected and temperature >= ALARM_THRESHOLD, trigger alarm
        """
        sensor_data: Dict[str, List[SensorReading]] = {}
        for reading in readings:
            sensor_data.setdefault(reading.measurement, []).append(reading)

        actuator_states: List[ActuatorState] = []

        # Rule 1: Fan control
        if "temperature" in sensor_data:
            for temp_reading in sensor_data["temperature"]:
                actuator_id = f"{temp_reading.device_id}_fan"
                current_state = self.actuators.get(actuator_id, "OFF")

                if temp_reading.value > self.FAN_THRESHOLD:
                    if current_state != "ON":
                        self.actuators[actuator_id] = "ON"
                        iot_logger.info(
                            f"Temperature = {temp_reading.value}°C → Fan ON",
                            source="controller",
                            device_id=temp_reading.device_id,
                            sensor_id=temp_reading.sensor_id,
                            metadata={"rule": "temperature > 30", "action": "fan_on"},
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=temp_reading.device_id,
                                actuator_type="fan",
                                state="ON",
                                timestamp=int(time.time()),
                            )
                        )
                else:
                    if current_state == "ON":
                        self.actuators[actuator_id] = "OFF"
                        iot_logger.info(
                            f"Temperature = {temp_reading.value}°C → Fan OFF",
                            source="controller",
                            device_id=temp_reading.device_id,
                            sensor_id=temp_reading.sensor_id,
                            metadata={"rule": "temperature <= 30", "action": "fan_off"},
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=temp_reading.device_id,
                                actuator_type="fan",
                                state="OFF",
                                timestamp=int(time.time()),
                            )
                        )

        # Rule 2: Light control
        if "motion" in sensor_data and "light" in sensor_data:
            device_ids = {reading.device_id for reading in sensor_data["motion"]}
            for device_id in device_ids:
                motion_readings = [
                    r for r in sensor_data["motion"] if r.device_id == device_id
                ]
                light_readings = [
                    r for r in sensor_data["light"] if r.device_id == device_id
                ]
                if not motion_readings or not light_readings:
                    continue

                motion_value = motion_readings[0].value
                light_value = light_readings[0].value
                actuator_id = f"{device_id}_light"
                current_state = self.actuators.get(actuator_id, "OFF")

                if motion_value == 1 and light_value < self.LIGHT_THRESHOLD:
                    if current_state != "ON":
                        self.actuators[actuator_id] = "ON"
                        iot_logger.info(
                            f"Motion detected and Light = {light_value} → Light ON",
                            source="controller",
                            device_id=device_id,
                            sensor_id=motion_readings[0].sensor_id,
                            metadata={
                                "rule": "motion detected and light < 20",
                                "action": "light_on",
                                "light_value": light_value,
                            },
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=device_id,
                                actuator_type="light",
                                state="ON",
                                timestamp=int(time.time()),
                            )
                        )
                elif motion_value == 0 or light_value >= self.LIGHT_THRESHOLD:
                    if current_state == "ON":
                        self.actuators[actuator_id] = "OFF"
                        reason = (
                            "no motion" if motion_value == 0 else f"light = {light_value}"
                        )
                        iot_logger.info(
                            f"{reason.capitalize()} → Light OFF",
                            source="controller",
                            device_id=device_id,
                            sensor_id=motion_readings[0].sensor_id,
                            metadata={"rule": reason, "action": "light_off"},
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=device_id,
                                actuator_type="light",
                                state="OFF",
                                timestamp=int(time.time()),
                            )
                        )

        # Rule 3: Alarm control
        if "motion" in sensor_data and "temperature" in sensor_data:
            device_ids = {reading.device_id for reading in sensor_data["motion"]}
            for device_id in device_ids:
                motion_readings = [
                    r for r in sensor_data["motion"] if r.device_id == device_id
                ]
                temp_readings = [
                    r for r in sensor_data["temperature"] if r.device_id == device_id
                ]
                if not motion_readings or not temp_readings:
                    continue

                motion_value = motion_readings[0].value
                temperature_value = temp_readings[0].value
                actuator_id = f"{device_id}_alarm"
                current_state = self.actuators.get(actuator_id, "OFF")

                if motion_value == 1 and temperature_value >= self.ALARM_THRESHOLD:
                    if current_state != "ON":
                        self.actuators[actuator_id] = "ON"
                        iot_logger.warning(
                            f"Motion detected and Temperature = {temperature_value}°C → Alarm ON",
                            source="controller",
                            device_id=device_id,
                            sensor_id=motion_readings[0].sensor_id,
                            metadata={
                                "rule": "motion + high temperature",
                                "action": "alarm_on",
                                "temperature": temperature_value,
                            },
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=device_id,
                                actuator_type="alarm",
                                state="ON",
                                timestamp=int(time.time()),
                            )
                        )
                else:
                    if current_state == "ON":
                        self.actuators[actuator_id] = "OFF"
                        reason = (
                            "temperature normalized"
                            if temperature_value < self.ALARM_THRESHOLD
                            else "no motion"
                        )
                        iot_logger.info(
                            f"{reason.capitalize()} → Alarm OFF",
                            source="controller",
                            device_id=device_id,
                            sensor_id=motion_readings[0].sensor_id,
                            metadata={"rule": reason, "action": "alarm_off"},
                        )
                        actuator_states.append(
                            ActuatorState(
                                actuator_id=actuator_id,
                                device_id=device_id,
                                actuator_type="alarm",
                                state="OFF",
                                timestamp=int(time.time()),
                            )
                        )

        return actuator_states

    def get_actuator_states(self) -> Dict[str, str]:
        """Get current state of all actuators"""
        return self.actuators.copy()


# Global instance
actuator_controller = ActuatorController()
