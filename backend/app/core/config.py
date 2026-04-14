"""
Application configuration via environment variables
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Job Application Copilot"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://copilot:copilot@db:5432/job_copilot"

    # Auth / JWT
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000"]

    # AI / Anthropic
    ANTHROPIC_API_KEY: str = ""

    # File uploads
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
