from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AnswerOut, DocumentRead, QuestionIn, SourceRead
from app.db.base import Base
from app.db.session import engine, get_session
from app.embeddings.providers import get_embedding_provider
from app.llm.providers import get_llm_provider
from app.repository import KnowledgeRepository
from app.services import QAService

app = FastAPI(
    title="AI Knowledge Base Support Bot",
    description="RAG API for document ingestion and question answering.",
    version="1.0.0",
)


@app.on_event("startup")
async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> DocumentRead:
    content = await file.read()
    repository = KnowledgeRepository(session, get_embedding_provider())
    try:
        document = await repository.add_document(
            filename=file.filename or "document",
            content_type=file.content_type or "application/octet-stream",
            content=content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return DocumentRead(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        chunks_count=len(document.chunks),
        created_at=document.created_at,
    )


@app.get("/documents", response_model=list[DocumentRead])
async def list_documents(session: AsyncSession = Depends(get_session)) -> list[DocumentRead]:
    repository = KnowledgeRepository(session, get_embedding_provider())
    documents = await repository.list_documents()
    return [
        DocumentRead(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            chunks_count=len(document.chunks),
            created_at=document.created_at,
        )
        for document in documents
    ]


@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    repository = KnowledgeRepository(session, get_embedding_provider())
    deleted = await repository.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@app.post("/ask", response_model=AnswerOut)
async def ask(
    payload: QuestionIn,
    session: AsyncSession = Depends(get_session),
) -> AnswerOut:
    service = QAService(session, get_embedding_provider(), get_llm_provider())
    answer, sources = await service.ask(payload.question)
    return AnswerOut(
        answer=answer,
        sources=[
            SourceRead(
                document=source.document,
                chunk=source.index,
                page=source.page,
                score=source.score,
            )
            for source in sources
        ],
    )
