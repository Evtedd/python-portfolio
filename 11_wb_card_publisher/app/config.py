from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://wb_cards:wb_cards@localhost:54311/wb_cards"
    wb_api_key: str = ""
    source_type: str = Field(default="csv", pattern="^(csv|db|sheets)$")
    csv_path: Path = Path("products.csv")
    dry_run: bool = True
    sandbox: bool = True
    batch_size: int = Field(default=50, ge=1, le=100)
    wb_base_url: str = "https://content-api.wildberries.ru"
    google_sheet_id: str = ""
    google_range: str = "products!A:Z"
    google_credentials_json: str = ""
    request_timeout: float = 20.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
