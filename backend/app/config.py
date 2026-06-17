from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "development"

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/dbname?charset=utf8mb4"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600

    JWT_ACCESS_SECRET: str = "change-me-access-secret"
    JWT_REFRESH_SECRET: str = "change-me-refresh-secret"
    JWT_ACCESS_TTL_MINUTES: int = 30
    JWT_REFRESH_TTL_DAYS: int = 7

    LLM_API_BASE: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_FALLBACK_ENABLED: bool = True
    LLM_MAX_TOKENS: int = 2048

    MESSAGE_ENCRYPTION_KEY: str = ""

    WS_PATH: str = "/ws"

    SAFETY_ESCALATION_NOTIFY: str = ""

    SMS_ENABLED: bool = False
    WECHAT_NOTIFY_ENABLED: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
