from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite+aiosqlite:///./multimodal.db", alias="DATABASE_URL")
    storage_dir: Path = Field(Path("./storage"), alias="STORAGE_DIR")
    max_upload_mb: int = Field(200, alias="MAX_UPLOAD_MB")
    text_embeddings_provider: str = Field("hash", alias="TEXT_EMBEDDINGS_PROVIDER")
    image_embeddings_provider: str = Field("hash", alias="IMAGE_EMBEDDINGS_PROVIDER")
    llm_base_url: str = Field("https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    llm_model: str = Field("gpt-4o-mini", alias="LLM_MODEL")
    enable_transcription: bool = Field(False, alias="ENABLE_TRANSCRIPTION")
    enable_inline_worker: bool = Field(True, alias="ENABLE_INLINE_WORKER")
    worker_poll_seconds: float = Field(2.0, alias="WORKER_POLL_SECONDS")
    chunk_words: int = Field(180, alias="CHUNK_WORDS")
    chunk_overlap: int = Field(30, alias="CHUNK_OVERLAP")
    search_top_k: int = Field(8, alias="SEARCH_TOP_K")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
