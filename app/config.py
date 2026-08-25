from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ----------------------------
    # Project
    # ----------------------------
    APP_NAME: str = "Nexora Innovation Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ----------------------------
    # Server & Port (Render binds dynamically to $PORT and 0.0.0.0)
    # ----------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ----------------------------
    # MongoDB
    # ----------------------------
    MONGODB_URI: str = "MongoDB_URL"
    DATABASE_NAME: str = "nexora"

    # ----------------------------
    # JWT
    # ----------------------------
    SECRET_KEY: str = "nexora-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # ----------------------------
    # Upload & Certificates
    # ----------------------------
    UPLOAD_FOLDER: str = "app/uploads"
    CERTIFICATE_FOLDER: str = "app/certificates"

    # ----------------------------
    # SMTP / Email (Optional - will not crash if not set)
    # ----------------------------
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # ----------------------------
    # Frontend & CORS
    # ----------------------------
    FRONTEND_URLS: str = "FRONTEND_URL"

    # ----------------------------
    # Registration & File Limits
    # ----------------------------
    MAX_TEAM_MEMBERS: int = 3
    MAX_PDF_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
