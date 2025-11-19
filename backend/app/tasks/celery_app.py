"""
Celery application configuration
"""
from celery import Celery
from app.core.config import settings
from app.tasks.celerybeat_schedule import CELERY_BEAT_SCHEDULE

celery_app = Celery(
    "iot_simulator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.aggregation", "app.tasks.rules"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule=CELERY_BEAT_SCHEDULE,
)

