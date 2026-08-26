"""
Application Configuration
"""

import json
from typing import List, Optional

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    APP_NAME: str = "Hospital Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    FRONTEND_URL: str = "http://localhost:3000"

    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    CORS_ORIGINS: List[str] = Field(default_factory=list)

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    TRUSTED_PROXY_IPS: List[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    DATABASE_URL: str

    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_READ_URL: str = ""

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None
    SMTP_TLS: bool = True

    # ------------------------------------------------------------------
    # SMS
    # ------------------------------------------------------------------

    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_API_SECRET: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None

    # ------------------------------------------------------------------
    # WhatsApp
    # ------------------------------------------------------------------

    WHATSAPP_API_KEY: Optional[str] = None
    WHATSAPP_API_URL: Optional[str] = None

    # ------------------------------------------------------------------
    # Uploads
    # ------------------------------------------------------------------

    UPLOAD_DIR: str = "/tmp/uploads"

    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024

    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "pdf",
            "doc",
            "docx",
        ]
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    REDIS_URL: Optional[str] = None
    REDIS_ENABLED: bool = False
    REDIS_CACHE_TTL: int = 300

    # ------------------------------------------------------------------
    # Celery
    # ------------------------------------------------------------------

    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # ------------------------------------------------------------------
    # Sentry
    # ------------------------------------------------------------------

    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None

    # ------------------------------------------------------------------
    # AI
    # ------------------------------------------------------------------

    AI_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"

    # ------------------------------------------------------------------
    # Subscription Limits
    # ------------------------------------------------------------------

    FREE_TIER_MAX_PATIENTS: int = 50
    FREE_TIER_MAX_DOCTORS: int = 2
    FREE_TIER_MAX_APPOINTMENTS_PER_MONTH: int = 100

    BASIC_TIER_MAX_PATIENTS: int = 500
    BASIC_TIER_MAX_DOCTORS: int = 5
    BASIC_TIER_MAX_APPOINTMENTS_PER_MONTH: int = 1000

    PREMIUM_TIER_MAX_PATIENTS: int = 5000
    PREMIUM_TIER_MAX_DOCTORS: int = 20
    PREMIUM_TIER_MAX_APPOINTMENTS_PER_MONTH: int = 10000

    AUDIT_LOG_RETENTION_DAYS: int = 365
    DATA_RETENTION_DAYS: int = 2555

    ENABLE_DATA_ACCESS_LOGGING: bool = True

    DEFAULT_TIMEZONE: str = "UTC"

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")

        if (
            info.data.get("ENVIRONMENT") == "production"
            and v == "your-secret-key-change-in-production-min-32-chars"
        ):
            raise ValueError("Default SECRET_KEY cannot be used in production")

        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if v in (None, ""):
            return []

        if isinstance(v, list):
            return v

        if isinstance(v, str):
            return json.loads(v)

        return v

    @field_validator("TRUSTED_PROXY_IPS", mode="before")
    @classmethod
    def parse_proxy(cls, v):
        if v in (None, ""):
            return []

        if isinstance(v, list):
            return v

        if isinstance(v, str):
            return json.loads(v)

        return v


settings = Settings()


def is_feature_enabled(feature: str) -> bool:
    return {
        "ai": settings.AI_ENABLED,
        "email": bool(settings.SMTP_HOST),
        "sms": bool(settings.SMS_API_KEY),
        "whatsapp": bool(settings.WHATSAPP_API_KEY),
        "redis": settings.REDIS_ENABLED,
        "celery": bool(settings.CELERY_BROKER_URL),
        "sentry": bool(settings.SENTRY_DSN),
    }.get(feature.lower(), False)


def get_tier_limits(tier: str):
    tiers = {
        "FREE": {
            "max_patients": settings.FREE_TIER_MAX_PATIENTS,
            "max_doctors": settings.FREE_TIER_MAX_DOCTORS,
            "max_appointments_per_month": settings.FREE_TIER_MAX_APPOINTMENTS_PER_MONTH,
        },
        "BASIC": {
            "max_patients": settings.BASIC_TIER_MAX_PATIENTS,
            "max_doctors": settings.BASIC_TIER_MAX_DOCTORS,
            "max_appointments_per_month": settings.BASIC_TIER_MAX_APPOINTMENTS_PER_MONTH,
        },
        "PREMIUM": {
            "max_patients": settings.PREMIUM_TIER_MAX_PATIENTS,
            "max_doctors": settings.PREMIUM_TIER_MAX_DOCTORS,
            "max_appointments_per_month": settings.PREMIUM_TIER_MAX_APPOINTMENTS_PER_MONTH,
        },
        "ENTERPRISE": {
            "max_patients": -1,
            "max_doctors": -1,
            "max_appointments_per_month": -1,
        },
    }

    return tiers.get(tier.upper(), tiers["FREE"])