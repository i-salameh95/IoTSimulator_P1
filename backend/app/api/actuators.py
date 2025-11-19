"""
Actuator API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.actuator import ActuatorState, ActuatorStateResponse
from app.core.mongodb_client import mongodb_service

router = APIRouter()


@router.get("/states", response_model=List[ActuatorStateResponse])
async def get_actuator_states(limit: int = 100):
    """
    Get actuator states
    """
    try:
        data = mongodb_service.get_actuator_states(limit=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/states/current", response_model=List[dict])
async def get_current_actuator_states():
    """
    Get current state of all actuators
    """
    try:
        data = mongodb_service.get_current_actuator_states()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control", response_model=dict, status_code=201)
async def control_actuator(actuator_state: ActuatorState):
    """
    Manually control an actuator
    """
    try:
        mongodb_service.write_actuator_state(actuator_state)
        return {
            "status": "success",
            "message": f"Actuator {actuator_state.actuator_id} set to {actuator_state.state}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

