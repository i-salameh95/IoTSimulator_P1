"""
Logs API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.log import LogEntry, LogEntryResponse, LogLevel
from app.core.logger import iot_logger

router = APIRouter()


@router.post("/", response_model=dict, status_code=201)
async def create_log(log_entry: LogEntry):
    """
    Create a log entry
    """
    try:
        iot_logger.log(
            level=log_entry.level,
            message=log_entry.message,
            source=log_entry.source,
            device_id=log_entry.device_id,
            sensor_id=log_entry.sensor_id,
            actuator_id=log_entry.actuator_id,
            metadata=log_entry.metadata
        )
        return {
            "status": "success",
            "message": "Log entry created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[LogEntryResponse])
async def get_logs(
    level: Optional[str] = None,
    source: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100
):
    """
    Get logs with optional filters
    """
    try:
        logs = iot_logger.get_logs(
            level=level,
            source=source,
            device_id=device_id,
            limit=limit
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

