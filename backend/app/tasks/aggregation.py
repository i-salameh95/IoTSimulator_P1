"""
Celery tasks for periodic aggregations and analytics
"""
from app.tasks.celery_app import celery_app
from app.core.mongodb_client import mongodb_service
from datetime import datetime, timedelta


@celery_app.task(name="aggregate_sensor_data")
def aggregate_sensor_data(measurement: str, window: str = "1h"):
    """
    Periodic task to aggregate sensor data
    
    This task runs periodically to compute aggregations
    and store summaries for faster frontend queries
    """
    try:
        # Get aggregated data for the last window
        data = mongodb_service.get_aggregated_data(
            measurement=measurement,
            window=window,
            aggregate="mean"
        )
        
        # Store aggregated results or perform analytics
        # This is where you might store pre-computed aggregations
        # or trigger alerts based on thresholds
        
        return {
            "status": "success",
            "measurement": measurement,
            "window": window,
            "records_processed": len(data)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="daily_aggregation")
def daily_aggregation():
    """
    Daily aggregation task for all measurements
    """
    measurements = ["temperature", "humidity", "pressure", "light"]
    results = []
    
    for measurement in measurements:
        result = aggregate_sensor_data.delay(measurement, window="24h")
        results.append(result.id)
    
    return {
        "status": "success",
        "tasks_queued": len(results),
        "task_ids": results
    }

