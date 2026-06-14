import json
import math
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.embeddings.providers import EmbeddingProvider
from app.models import Chunk


@dataclass(frozen=True)
class SearchResult:
    chunk_id: int
    document: str
    index: int
    page: int | None
    text: str
    score: float


class Retriever:
    def __init__(self, session: AsyncSession, embeddings: EmbeddingProvider) -> None:
        self.session = session
        self.embeddings = embeddings

    async def search(self, question: str, top_k: int) -> list[SearchResult]:
        query_vector = await self.embeddings.embed(question)
        result = await self.session.execute(
            select(Chunk).options(selectinload(Chunk.document)),
        )
        scored: list[SearchResult] = []
        for chunk in result.scalars().all():
            vector = [float(item) for item in json.loads(chunk.embedding)]
            score = cosine_similarity(query_vector, vector)
            scored.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document=chunk.document.filename,
                    index=chunk.index,
                    page=chunk.page,
                    text=chunk.text,
                    score=score,
                ),
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
