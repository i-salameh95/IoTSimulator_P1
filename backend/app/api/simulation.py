"""
Simulation API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.simulation_engine import simulation_engine
from app.core.logger import iot_logger

router = APIRouter()


@router.post("/run-cycle", response_model=dict)
async def run_single_cycle():
    """
    Run a single simulation cycle
    Sensors send data → Central computer analyzes → Actuators respond
    """
    try:
        result = simulation_engine.run_cycle()
        return {
            "status": "success",
            "cycle": result["cycle"],
            "sensor_readings": result["sensor_readings"],
            "actuator_states": result["actuator_states"],
            "decisions_made": result["decisions_made"]
        }
    except Exception as e:
        iot_logger.error(
            f"Error running simulation cycle: {str(e)}",
            source="simulation"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", response_model=dict)
async def run_simulation(
    num_cycles: int = Query(20, ge=1, le=100),
    delay_seconds: float = Query(1.0, ge=0.1, le=10.0)
):
    """
    Run simulation for a fixed number of cycles
    
    Args:
        num_cycles: Number of cycles to run (default: 20 as per requirements)
        delay_seconds: Delay between cycles in seconds
    """
    try:
        results = simulation_engine.run_simulation(
            num_cycles=num_cycles,
            delay_seconds=delay_seconds
        )
        return {
            "status": "success",
            "total_cycles": len(results),
            "results": results
        }
    except Exception as e:
        iot_logger.error(
            f"Error running simulation: {str(e)}",
            source="simulation"
        )
        raise HTTPException(status_code=500, detail=str(e))

