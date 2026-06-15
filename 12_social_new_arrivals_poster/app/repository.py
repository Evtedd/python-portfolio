from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProductArrival, PublicationJob
from app.schemas import ProductArrivalIn


class PublicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_product(self, product: ProductArrivalIn) -> None:
        statement = insert(ProductArrival).values(
            product_id=product.product_id,
            payload=product.model_dump(mode="json"),
        )
        statement = statement.on_conflict_do_update(
            index_elements=[ProductArrival.product_id],
            set_={"payload": product.model_dump(mode="json")},
        )
        await self.session.execute(statement)

    async def enqueue(self, product: ProductArrivalIn, platform: str, payload: dict, scheduled_at: datetime) -> bool:
        statement = insert(PublicationJob).values(
            product_id=product.product_id,
            platform=platform,
            payload=payload,
            scheduled_at=scheduled_at,
            status="queued",
        )
        statement = statement.on_conflict_do_nothing(
            index_elements=[PublicationJob.product_id, PublicationJob.platform]
        )
        result = await self.session.execute(statement)
        return bool(result.rowcount)

    async def due_jobs(self, now: datetime, limit: int = 20) -> list[PublicationJob]:
        result = await self.session.execute(
            select(PublicationJob)
            .where(PublicationJob.status == "queued", PublicationJob.scheduled_at <= now)
            .order_by(PublicationJob.scheduled_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_done(self, job: PublicationJob, external_id: str) -> None:
        job.status = "published"
        job.external_id = external_id
        job.error = None

    async def mark_failed(self, job: PublicationJob, error: str) -> None:
        job.status = "failed" if job.attempts >= 2 else "queued"
        job.error = error
        job.attempts += 1

    async def list_jobs(self) -> list[PublicationJob]:
        result = await self.session.execute(select(PublicationJob).order_by(PublicationJob.created_at.desc()).limit(100))
        return list(result.scalars().all())

    async def commit(self) -> None:
        await self.session.commit()
