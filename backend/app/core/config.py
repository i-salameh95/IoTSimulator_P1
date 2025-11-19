"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "IoT Simulator"
    DEBUG: bool = True
    
    # MongoDB
    MONGODB_URL: str = "mongodb://admin:admin123@localhost:27017/iot_data?authSource=admin"
    MONGODB_DATABASE: str = "iot_data"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # MQTT (Phase 2)
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

