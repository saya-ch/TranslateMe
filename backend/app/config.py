from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_ENV: str = "development"

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/dbname?charset=utf8mb4"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_POOL_SIZE: int = 10

    # JWT - 统一使用一个密钥（简化）
    JWT_SECRET: str = "change-this-to-a-long-random-secret-key-please"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    JWT_ACCESS_SECRET: Optional[str] = None
    JWT_REFRESH_SECRET: Optional[str] = None
    JWT_ACCESS_TTL_MINUTES: int = 30
    JWT_REFRESH_TTL_DAYS: int = 7

    # AES 加密
    ENCRYPTION_AES_KEY: str = "please-change-this-to-32-byte-key-please"
    MESSAGE_ENCRYPTION_KEY: Optional[str] = None

    # LLM
    LLM_API_BASE: str = ""
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_FALLBACK_ENABLED: bool = True
    LLM_MAX_TOKENS: int = 800

    # WebSocket
    WS_PATH: str = "/ws"

    # 安全
    SAFETY_ESCALATION_NOTIFY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    def get_jwt_secret(self) -> str:
        return self.JWT_ACCESS_SECRET or self.JWT_SECRET

    def get_refresh_secret(self) -> str:
        return self.JWT_REFRESH_SECRET or self.JWT_SECRET

    def get_aes_key(self) -> str:
        return self.MESSAGE_ENCRYPTION_KEY or self.ENCRYPTION_AES_KEY


settings = Settings()
