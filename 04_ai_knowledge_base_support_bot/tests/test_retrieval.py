import json

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import Chunk, Document
from app.retrieval.search import Retriever


class FakeEmbeddings:
    async def embed(self, text: str) -> list[float]:
        return [1.0, 0.0] if "python" in text.lower() else [0.0, 1.0]


pytestmark = pytest.mark.asyncio


async def test_retriever_returns_best_chunk():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        document = Document(filename="guide.md", content_type="text/markdown")
        session.add(document)
        await session.flush()
        session.add_all(
            [
                Chunk(
                    document_id=document.id,
                    index=1,
                    page=None,
                    text="Python setup",
                    embedding=json.dumps([1.0, 0.0]),
                ),
                Chunk(
                    document_id=document.id,
                    index=2,
                    page=None,
                    text="Billing help",
                    embedding=json.dumps([0.0, 1.0]),
                ),
            ],
        )
        await session.commit()

        results = await Retriever(session, FakeEmbeddings()).search("python", top_k=1)

    await engine.dispose()

    assert results[0].text == "Python setup"
