import os
from typing import List, Optional


class Settings:
    APP_ENV: str = os.environ.get("APP_ENV", "development")
    APP_PORT: int = int(os.environ.get("PORT", 8000))
    CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://ornate_admin:ornate_secure_2026@postgres:5432/compliance",
    )
    DATABASE_URL_SYNC: Optional[str] = os.environ.get("DATABASE_URL_SYNC", None)


settings = Settings()
