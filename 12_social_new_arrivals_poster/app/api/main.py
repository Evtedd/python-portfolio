import logging

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.content import ContentBuilder
from app.db.session import get_session
from app.publishers.factory import build_publishers
from app.queue import PublicationQueue
from app.repository import PublicationRepository
from app.schemas import JobView, ProductArrivalIn

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Social new arrivals poster")


def build_queue(settings: Settings, session: AsyncSession) -> PublicationQueue:
    return PublicationQueue(
        PublicationRepository(session),
        build_publishers(settings),
        ContentBuilder(),
        settings.publication_spacing_seconds,
    )


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, bool]:
    return {"ok": True, "dry_run": settings.dry_run}


@app.post("/webhooks/products")
async def product_webhook(
    product: ProductArrivalIn,
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    return await build_queue(settings, session).enqueue_product(product)


@app.post("/queue/run")
async def run_queue(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    return await build_queue(settings, session).run_due()


@app.get("/queue", response_model=list[JobView])
async def list_queue(session: AsyncSession = Depends(get_session)) -> list[JobView]:
    jobs = await PublicationRepository(session).list_jobs()
    return [JobView.model_validate(job, from_attributes=True) for job in jobs]
