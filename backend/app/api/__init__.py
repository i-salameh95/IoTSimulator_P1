from fastapi import APIRouter
from app.api import sensors, actuators, logs, simulation

router = APIRouter()

router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
router.include_router(actuators.router, prefix="/actuators", tags=["actuators"])
router.include_router(logs.router, prefix="/logs", tags=["logs"])
router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])

