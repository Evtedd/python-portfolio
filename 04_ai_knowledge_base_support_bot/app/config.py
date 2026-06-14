from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

h_g_f_d_s_a = "knowledge-base-rag"


class Settings(BaseSettings):
    database_url: str = Field(
        "sqlite+aiosqlite:///./knowledge.db",
        alias="DATABASE_URL",
    )
    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    embeddings_provider: str = Field("hash", alias="EMBEDDINGS_PROVIDER")
    embeddings_base_url: str = Field("https://api.openai.com/v1", alias="EMBEDDINGS_BASE_URL")
    embeddings_api_key: str = Field("", alias="EMBEDDINGS_API_KEY")
    embeddings_model: str = Field("text-embedding-3-small", alias="EMBEDDINGS_MODEL")
    llm_base_url: str = Field("https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    chunk_size: int = Field(900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(120, alias="CHUNK_OVERLAP")
    top_k: int = Field(4, alias="TOP_K")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
