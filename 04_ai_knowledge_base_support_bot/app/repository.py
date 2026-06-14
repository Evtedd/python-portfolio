import json

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.embeddings.providers import EmbeddingProvider
from app.ingestion.chunker import chunk_text
from app.ingestion.parser import parse_document
from app.models import Chunk, Document, QAHistory
from app.retrieval.search import SearchResult


class KnowledgeRepository:
    def __init__(self, session: AsyncSession, embeddings: EmbeddingProvider) -> None:
        self.session = session
        self.embeddings = embeddings

    async def add_document(self, filename: str, content_type: str, content: bytes) -> Document:
        pages = parse_document(filename, content)
        if not pages:
            raise ValueError("Document has no readable text")

        document = Document(filename=filename, content_type=content_type)
        self.session.add(document)
        await self.session.flush()

        chunk_index = 1
        for page in pages:
            for chunk in chunk_text(
                page.text,
                settings.chunk_size,
                settings.chunk_overlap,
                page=page.page,
            ):
                vector = await self.embeddings.embed(chunk.text)
                document.chunks.append(
                    Chunk(
                        document_id=document.id,
                        index=chunk_index,
                        page=chunk.page,
                        text=chunk.text,
                        embedding=json.dumps(vector),
                    ),
                )
                chunk_index += 1

        await self.session.commit()
        return document

    async def list_documents(self) -> list[Document]:
        result = await self.session.execute(
            select(Document).options(selectinload(Document.chunks)).order_by(Document.id),
        )
        return list(result.scalars().all())

    async def delete_document(self, document_id: int) -> bool:
        document = await self.session.get(Document, document_id)
        if document is None:
            return False
        await self.session.delete(document)
        await self.session.commit()
        return True

    async def save_history(
        self,
        question: str,
        answer: str,
        sources: list[SearchResult],
    ) -> None:
        source_text = json.dumps(
            [
                {
                    "document": item.document,
                    "chunk": item.index,
                    "page": item.page,
                    "score": item.score,
                }
                for item in sources
            ],
            ensure_ascii=False,
        )
        self.session.add(QAHistory(question=question, answer=answer, sources=source_text))
        await self.session.commit()
