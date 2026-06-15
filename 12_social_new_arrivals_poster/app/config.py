from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://social_poster:social_poster@localhost:54312/social_poster"
    dry_run: bool = True
    instagram_access_token: str = ""
    instagram_account_id: str = ""
    pinterest_access_token: str = ""
    pinterest_board_id: str = ""
    publication_spacing_seconds: int = Field(default=900, ge=60)
    request_timeout: float = 20.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
