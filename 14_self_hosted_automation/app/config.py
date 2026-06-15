from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://automation:automation@localhost:54314/automation"
    redis_url: str = "redis://localhost:63714/0"
    api_key: str = "change-me"
    fernet_key: str = ""
    fake_mode: bool = True
    request_timeout: float = 20.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
