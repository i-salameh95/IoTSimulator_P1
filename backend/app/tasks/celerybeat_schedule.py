"""
Celery Beat schedule configuration
"""
from datetime import timedelta

# Periodic task schedule
CELERY_BEAT_SCHEDULE = {
    # Aggregate sensor data every hour
    "aggregate-hourly": {
        "task": "aggregate_sensor_data",
        "schedule": timedelta(hours=1),
        "args": ("temperature", "1h")
    },
    # Daily aggregation at midnight
    "aggregate-daily": {
        "task": "daily_aggregation",
        "schedule": timedelta(days=1),
    },
    # Evaluate rules every 5 minutes
    "evaluate-rules": {
        "task": "evaluate_rules",
        "schedule": timedelta(minutes=5),
    },
}

