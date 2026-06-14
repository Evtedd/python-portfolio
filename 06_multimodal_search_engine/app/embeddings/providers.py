import hashlib
import math
from typing import Protocol

import httpx

from app.config import settings


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]:
        ...


class HashEmbeddingProvider:
    def __init__(self, dimensions: int = 96) -> None:
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=30,
        )

    async def embed(self, text: str) -> list[float]:
        response = await self.client.post(
            "/embeddings",
            json={"model": "text-embedding-3-small", "input": text},
        )
        response.raise_for_status()
        return [float(item) for item in response.json()["data"][0]["embedding"]]


def get_text_embeddings() -> EmbeddingProvider:
    if settings.text_embeddings_provider == "openai" and settings.llm_api_key:
        return OpenAIEmbeddingProvider()
    return HashEmbeddingProvider()


def get_image_embeddings() -> EmbeddingProvider:
    return HashEmbeddingProvider()
