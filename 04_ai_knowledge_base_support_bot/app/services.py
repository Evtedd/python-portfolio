from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.embeddings.providers import EmbeddingProvider
from app.llm.providers import LLMProvider
from app.repository import KnowledgeRepository
from app.retrieval.search import Retriever, SearchResult


class QAService:
    def __init__(
        self,
        session: AsyncSession,
        embeddings: EmbeddingProvider,
        llm: LLMProvider,
    ) -> None:
        self.session = session
        self.embeddings = embeddings
        self.llm = llm

    async def ask(self, question: str) -> tuple[str, list[SearchResult]]:
        retriever = Retriever(self.session, self.embeddings)
        results = await retriever.search(question, top_k=settings.top_k)
        relevant = [item for item in results if item.score > 0.05]
        answer = await self.llm.answer(question, relevant)
        await KnowledgeRepository(self.session, self.embeddings).save_history(
            question,
            answer,
            relevant,
        )
        return answer, relevant
