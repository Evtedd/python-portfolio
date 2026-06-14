from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.embeddings.providers import get_text_embeddings
from app.llm.providers import get_llm
from app.repository import SearchRepository
from app.schemas import SearchResultRead, SummaryRead


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query: str, top_k: int | None = None) -> list[SearchResultRead]:
        vector = await get_text_embeddings().embed(query)
        matches = await SearchRepository(self.session).search(
            vector,
            top_k or settings.search_top_k,
        )
        return [
            SearchResultRead(
                asset_id=segment.asset_id,
                filename=segment.asset.filename,
                kind=segment.asset.kind,
                segment_id=segment.id,
                text=segment.text,
                score=round(score, 4),
                page=segment.page,
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                preview_path=segment.preview_path,
            )
            for segment, score in matches
        ]

    async def answer(self, question: str) -> SummaryRead:
        sources = await self.search(question)
        answer = await get_llm().answer(question, sources)
        return SummaryRead(answer=answer, sources=sources)
