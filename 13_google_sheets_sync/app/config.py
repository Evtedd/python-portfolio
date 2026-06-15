import json
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SyncTask(BaseModel):
    name: str
    spreadsheet_id: str
    range_name: str
    table_name: str
    key_column: str
    columns: dict[str, str]
    bidirectional: bool = False


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://sheets_sync:sheets_sync@localhost:54313/sheets_sync"
    google_fake_mode: bool = True
    google_credentials_path: str = ""
    google_credentials_json: str = ""
    sync_tasks_json: str = Field(
        default='[{"name":"products","spreadsheet_id":"demo","range_name":"products!A:Z","table_name":"products","key_column":"sku","columns":{"sku":"sku","name":"name","price":"price"},"bidirectional":false}]'
    )
    sync_interval_seconds: int = Field(default=300, ge=30)
    alert_telegram_token: str = ""
    alert_telegram_chat_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sync_tasks(self) -> list[SyncTask]:
        return [SyncTask.model_validate(item) for item in json.loads(self.sync_tasks_json)]


@lru_cache
def get_settings() -> Settings:
    return Settings()
