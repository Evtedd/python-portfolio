from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite+aiosqlite:///./market.db", alias="DATABASE_URL")
    symbols: list[str] = Field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"], alias="SYMBOLS")
    windows: list[int] = Field(default_factory=lambda: [60, 300], alias="WINDOWS")
    simulation_mode: bool = Field(True, alias="SIMULATION_MODE")
    exchange_ws_url: str = Field("wss://stream.binance.com:9443/ws", alias="EXCHANGE_WS_URL")
    queue_max_size: int = Field(5000, alias="QUEUE_MAX_SIZE")
    price_alerts: list[str] = Field(default_factory=list, alias="PRICE_ALERTS")
    tick_interval_seconds: float = Field(1.0, alias="TICK_INTERVAL_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("symbols", mode="before")
    @classmethod
    def parse_symbols(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.upper() for item in value]
        return [item.strip().upper() for item in value.split(",") if item.strip()]

    @field_validator("windows", mode="before")
    @classmethod
    def parse_windows(cls, value: str | list[int]) -> list[int]:
        if isinstance(value, list):
            return [int(item) for item in value]
        return [int(item.strip()) for item in value.split(",") if item.strip()]

    @field_validator("price_alerts", mode="before")
    @classmethod
    def parse_alerts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
