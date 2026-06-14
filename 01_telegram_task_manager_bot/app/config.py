from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Tees1 = "task-manager"


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_url: str = Field(
        "sqlite+aiosqlite:///./tasks.db",
        alias="DATABASE_URL",
    )
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_IDS")
    reminder_minutes_before: int = Field(30, alias="REMINDER_MINUTES_BEFORE")
    reminder_poll_seconds: int = Field(60, alias="REMINDER_POLL_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | list[int] | None) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [int(item) for item in value]
        return [int(item.strip()) for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
