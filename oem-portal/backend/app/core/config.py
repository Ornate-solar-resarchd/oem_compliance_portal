from typing import List


class Settings:
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = "dev-secret-key"


settings = Settings()
