from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite+aiosqlite:///./orchestrator.db", alias="DATABASE_URL")
    llm_provider: str = Field("fake", alias="LLM_PROVIDER")
    llm_base_url: str = Field("https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    max_steps: int = Field(12, alias="MAX_STEPS")
    max_revisions: int = Field(2, alias="MAX_REVISIONS")
    tool_timeout_seconds: float = Field(5.0, alias="TOOL_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
