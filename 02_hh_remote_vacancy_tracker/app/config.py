from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

please_work = "hh-remote-tracker"


class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: int = Field(..., alias="TELEGRAM_CHAT_ID")
    hh_text: str = Field("Python backend", alias="HH_TEXT")
    hh_area: str = Field("113", alias="HH_AREA")
    hh_per_page: int = Field(50, alias="HH_PER_PAGE")
    poll_interval_seconds: int = Field(900, alias="POLL_INTERVAL_SECONDS")
    whitelist_keywords: list[str] = Field(
        default_factory=lambda: [
            "Python",
            "FastAPI",
            "Django",
            "backend",
            "стажер",
            "стажёр",
            "junior",
            "удаленно",
            "удалённо",
        ],
        alias="WHITELIST_KEYWORDS",
    )
    blacklist_keywords: list[str] = Field(
        default_factory=lambda: [
            "преподаватель",
            "учитель",
            "продажи",
            "не IT",
            "офис",
        ],
        alias="BLACKLIST_KEYWORDS",
    )
    http_timeout_seconds: float = Field(
        20.0,
        alias="HTTP_TIMEOUT_SECONDS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("whitelist_keywords", "blacklist_keywords", mode="before")
    @classmethod
    def parse_keywords(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
