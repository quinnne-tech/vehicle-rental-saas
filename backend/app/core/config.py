"""Application Configuration"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from datetime import timedelta


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # FastAPI
    FASTAPI_ENV: str = os.getenv("FASTAPI_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))

    # MongoDB
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_DB: str = os.getenv("MONGODB_DB", "vehicle_rental_saas")
    MONGODB_USER: str = os.getenv("MONGODB_USER", "admin")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "password123")
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        "mongodb://admin:password123@localhost:27017/vehicle_rental_saas?authSource=admin"
    )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@vehiclerental-saas.com")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Vehicle Rental SaaS")

    # Payment Providers
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    MIDTRANS_SERVER_KEY: Optional[str] = os.getenv("MIDTRANS_SERVER_KEY")
    MIDTRANS_CLIENT_KEY: Optional[str] = os.getenv("MIDTRANS_CLIENT_KEY")

    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
