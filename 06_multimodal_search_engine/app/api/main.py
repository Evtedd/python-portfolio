import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.base import Base
from app.db.session import SessionFactory, engine, get_session
from app.ingestion.types import EXTENSION_KIND
from app.repository import AssetRepository
from app.schemas import AssetRead, SearchRequest, SearchResultRead, SummaryRead
from app.search.service import SearchService
from app.workers.indexer import worker_loop

logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal Search Engine", version="1.0.0")
stop_event = asyncio.Event()
worker_task: asyncio.Task | None = None


@app.on_event("startup")
async def startup() -> None:
    global worker_task
    logging.basicConfig(level=logging.INFO)
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    if settings.enable_inline_worker:
        worker_task = asyncio.create_task(worker_loop(SessionFactory, stop_event))


@app.on_event("shutdown")
async def shutdown() -> None:
    stop_event.set()
    if worker_task is not None:
        await worker_task


@app.post("/assets", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> AssetRead:
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    kind = EXTENSION_KIND.get(suffix)
    if kind is None:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File is too large")

    target = settings.storage_dir / f"{uuid4().hex}{suffix}"
    target.write_bytes(content)
    asset = await AssetRepository(session).create_asset(
        filename=filename,
        kind=kind,
        content_type=file.content_type or "application/octet-stream",
        path=target,
    )
    return asset


@app.get("/assets", response_model=list[AssetRead])
async def list_assets(session: AsyncSession = Depends(get_session)) -> list[AssetRead]:
    return await AssetRepository(session).list_assets()


@app.post("/search", response_model=list[SearchResultRead])
async def search(
    payload: SearchRequest,
    session: AsyncSession = Depends(get_session),
) -> list[SearchResultRead]:
    return await SearchService(session).search(payload.query, payload.top_k)


@app.post("/chat", response_model=SummaryRead)
async def chat(
    payload: SearchRequest,
    session: AsyncSession = Depends(get_session),
) -> SummaryRead:
    return await SearchService(session).answer(payload.query)
