import hashlib
import math
from typing import Protocol

import httpx

from app.config import settings


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]:
        ...


class HashEmbeddingProvider:
    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for word in text.lower().split():
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(item * item for item in vector)) or 1.0
        return [item / norm for item in vector]


class OpenAIEmbeddingProvider:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.embeddings_base_url,
            headers={"Authorization": f"Bearer {settings.embeddings_api_key}"},
            timeout=30,
        )

    async def embed(self, text: str) -> list[float]:
        response = await self.client.post(
            "/embeddings",
            json={"model": settings.embeddings_model, "input": text},
        )
        response.raise_for_status()
        data = response.json()["data"][0]["embedding"]
        return [float(item) for item in data]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.embeddings_provider == "openai":
        if not settings.embeddings_api_key:
            raise RuntimeError("EMBEDDINGS_API_KEY is required for openai embeddings")
        return OpenAIEmbeddingProvider()
    return HashEmbeddingProvider()
