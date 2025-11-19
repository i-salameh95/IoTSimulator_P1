"""
Simulation engine for IoT Smart Home
Implements simulation cycles as per project requirements
"""
import time
from typing import List
from app.services.simulator import SensorSimulator
from app.services.actuator_controller import ActuatorController
from app.core.mongodb_client import mongodb_service
from app.core.logger import iot_logger
from app.models.sensor import SensorReading
from app.models.actuator import ActuatorState


class SimulationEngine:
    """Runs simulation cycles: sensors → controller → actuators"""
    
    def __init__(self):
        self.sensor_simulator = SensorSimulator()
        self.actuator_controller = ActuatorController()
        self.current_cycle = 0
    
    def run_cycle(self, cycle_number: int = None) -> dict:
        """
        Run a single simulation cycle
        
        Cycle flow (as per requirements):
        1. Sensors send data
        2. Central computer analyzes
        3. Actuators respond
        
        Args:
            cycle_number: Cycle number (optional)
        
        Returns:
            Dictionary with cycle results
        """
        if cycle_number is None:
            self.current_cycle += 1
            cycle_number = self.current_cycle
        else:
            self.current_cycle = cycle_number
        
        iot_logger.info(
            f"=== Simulation Cycle {cycle_number} Started ===",
            source="simulation"
        )
        
        # Step 1: Sensors send data
        # Generate readings for all sensor types from all devices
        all_readings = []
        for device in self.sensor_simulator.devices:
            device_readings = self.sensor_simulator.generate_all_sensor_readings(
                device_id=device["device_id"]
            )
            all_readings.extend(device_readings)
            
            # Log sensor readings (as per requirements: "Temperature = 35 → Fan ON")
            for reading in device_readings:
                if reading.measurement == "temperature":
                    unit = "°C"
                    log_msg = f"Temperature = {reading.value}{unit}"
                elif reading.measurement == "light":
                    unit = ""
                    log_msg = f"Light = {reading.value}"
                elif reading.measurement == "motion":
                    unit = ""
                    motion_text = "detected" if reading.value == 1 else "no motion"
                    log_msg = f"Motion = {motion_text}"
                else:
                    unit = ""
                    log_msg = f"{reading.measurement.capitalize()} = {reading.value}{unit}"
                
                iot_logger.info(
                    log_msg,
                    source="sensor",
                    device_id=reading.device_id,
                    sensor_id=reading.sensor_id
                )
        
        # Store sensor readings in MongoDB
        for reading in all_readings:
            mongodb_service.write_sensor_data(
                measurement=reading.measurement,
                device_id=reading.device_id,
                sensor_id=reading.sensor_id,
                value=reading.value,
                timestamp=reading.timestamp,
                tags=reading.tags
            )
        
        # Step 2: Central computer analyzes and makes decisions
        actuator_states = self.actuator_controller.process_sensor_readings(all_readings)
        
        # Step 3: Store actuator states
        for actuator_state in actuator_states:
            mongodb_service.write_actuator_state(actuator_state)
        
        # Get current actuator states
        current_states = self.actuator_controller.get_actuator_states()
        
        # Log actuator states
        for actuator_id, state in current_states.items():
            iot_logger.info(
                f"Actuator {actuator_id}: {state}",
                source="actuator",
                actuator_id=actuator_id
            )
        
        iot_logger.info(
            f"=== Simulation Cycle {cycle_number} Completed ===",
            source="simulation"
        )
        
        return {
            "cycle": cycle_number,
            "sensor_readings": len(all_readings),
            "actuator_states": current_states,
            "decisions_made": len(actuator_states)
        }
    
    def run_simulation(self, num_cycles: int = 20, delay_seconds: float = 1.0) -> List[dict]:
        """
        Run simulation for a fixed number of cycles
        
        Args:
            num_cycles: Number of cycles to run (default: 20 as per requirements)
            delay_seconds: Delay between cycles in seconds
        
        Returns:
            List of cycle results
        """
        iot_logger.info(
            f"Starting simulation with {num_cycles} cycles",
            source="simulation"
        )
        
        results = []
        for i in range(1, num_cycles + 1):
            cycle_result = self.run_cycle(i)
            results.append(cycle_result)
            
            if i < num_cycles:
                time.sleep(delay_seconds)
        
        iot_logger.info(
            f"Simulation completed. Total cycles: {num_cycles}",
            source="simulation"
        )
        
        return results


# Global instance
simulation_engine = SimulationEngine()

