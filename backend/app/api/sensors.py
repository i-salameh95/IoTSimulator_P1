"""
Sensor data API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.models.sensor import (
    SensorReading,
    SensorReadingResponse,
    HistoricalDataQuery,
    AggregatedDataQuery
)
from app.core.mongodb_client import mongodb_service

router = APIRouter()


@router.post("/ingest", response_model=dict, status_code=201)
async def ingest_sensor_data(reading: SensorReading):
    """
    Ingest sensor data into MongoDB (simulated in Phase 1)
    """
    try:
        mongodb_service.write_sensor_data(
            measurement=reading.measurement,
            device_id=reading.device_id,
            sensor_id=reading.sensor_id,
            value=reading.value,
            timestamp=reading.timestamp,
            tags=reading.tags
        )
        return {
            "status": "success",
            "message": "Sensor data ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch", response_model=dict, status_code=201)
async def ingest_sensor_data_batch(readings: List[SensorReading]):
    """
    Ingest multiple sensor readings in batch
    """
    try:
        for reading in readings:
            mongodb_service.write_sensor_data(
                measurement=reading.measurement,
                device_id=reading.device_id,
                sensor_id=reading.sensor_id,
                value=reading.value,
                timestamp=reading.timestamp,
                tags=reading.tags
            )
        return {
            "status": "success",
            "message": f"{len(readings)} sensor readings ingested successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/historical", response_model=List[SensorReadingResponse])
async def get_historical_data(query: HistoricalDataQuery):
    """
    Retrieve historical sensor data
    """
    try:
        data = mongodb_service.query_sensor_data(
            measurement=query.measurement,
            device_id=query.device_id,
            sensor_id=query.sensor_id,
            start_time=query.start_time,
            stop_time=query.stop_time,
            limit=query.limit
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/aggregated", response_model=List[SensorReadingResponse])
async def get_aggregated_data(query: AggregatedDataQuery):
    """
    Retrieve aggregated sensor data (summaries)
    """
    try:
        data = mongodb_service.get_aggregated_data(
            measurement=query.measurement,
            device_id=query.device_id,
            sensor_id=query.sensor_id,
            window=query.window,
            aggregate=query.aggregate
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/measurements", response_model=List[str])
async def get_measurements():
    """
    Get list of available measurement types
    """
    try:
        measurements = mongodb_service.get_distinct_measurements()
        # If no measurements exist, return required sensor types per project requirements
        if not measurements:
            return [
                "temperature",
                "light",
                "motion"
            ]
        return measurements
    except Exception as e:
        # Fallback to required sensor types on error
        return [
            "temperature",
            "light",
            "motion"
        ]


@router.get("/devices", response_model=List[str])
async def get_devices():
    """
    Get list of available device IDs
    """
    try:
        devices = mongodb_service.get_distinct_devices()
        return devices
    except Exception as e:
        return []

