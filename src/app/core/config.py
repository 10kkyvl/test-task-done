from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    FASTAPI_HOST: str = Field("0.0.0.0")
    FASTAPI_PORT: int = Field(8000)
    DATABASE_URL: str = Field(...)
    REDIS_URL: str | None = None
    CLICKHOUSE_URL: str | None = None
    NATS_URL: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings: Settings = Settings()
