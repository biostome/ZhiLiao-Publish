from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # App
    APP_NAME: str = Field(default="TaskIngestService")
    LOG_LEVEL: str = Field(default="INFO")
    TIMEZONE: str = Field(default="Asia/Shanghai")
    DATA_SOURCES_FILE: str = Field(default="./config/sources.yaml")
    SCHEDULE_INTERVAL_SECONDS: int = Field(default=600)
    SCHEDULER_ENABLED: bool = Field(default=False)
    REQUEST_TIMEOUT_SECONDS: int = Field(default=20)
    USER_AGENT: str = Field(default="TaskIngestBot/1.0")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    DUP_TTL_DAYS: int = Field(default=14)

    # Database
    POSTGRES_DSN: str = Field(default="postgresql+psycopg://taskuser:taskpass@localhost:5432/taskdb")

    # Task Management API
    TASK_API_BASE_URL: str = Field(default="http://localhost:9000/api")
    TASK_API_TOKEN: str = Field(default="")
    TASK_API_TIMEOUT_SECONDS: int = Field(default=20)

    # AI Generation
    ENABLE_AI: bool = Field(default=True)
    MODEL_NAME: str = Field(default="gpt-4o-mini")
    MODEL_PROVIDER: str = Field(default="openai")
    MODEL_API_KEY: str = Field(default="")

    # Validation
    ENABLE_VALIDATION: bool = Field(default=True)


settings = Settings()