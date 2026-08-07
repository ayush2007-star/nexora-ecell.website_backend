from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ----------------------------
    # Project
    # ----------------------------
    APP_NAME: str = "Nexora Innovation Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ----------------------------
    # Server
    # ----------------------------
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ----------------------------
    # MongoDB
    # ----------------------------
    MONGODB_URI: str
    DATABASE_NAME: str = "nexora"

    # ----------------------------
    # JWT
    # ----------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # ----------------------------
    # Upload
    # ----------------------------
    UPLOAD_FOLDER: str = "app/uploads"
    CERTIFICATE_FOLDER: str = "app/certificates"

    SMTP_HOST: str
    SMTP_PORT: int

    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    EMAIL_FROM: str
    # ----------------------------
    # Registration
    # ----------------------------
    MAX_TEAM_MEMBERS: int = 3
    MAX_PDF_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()