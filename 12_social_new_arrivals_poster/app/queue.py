from datetime import datetime, timedelta, timezone

from app.content import ContentBuilder
from app.publishers.base import Publisher
from app.repository import PublicationRepository
from app.schemas import ProductArrivalIn, PublishRequest


class PublicationQueue:
    def __init__(
        self,
        repository: PublicationRepository,
        publishers: dict[str, Publisher],
        content_builder: ContentBuilder,
        spacing_seconds: int,
    ) -> None:
        self.repository = repository
        self.publishers = publishers
        self.content_builder = content_builder
        self.spacing_seconds = spacing_seconds

    async def enqueue_product(self, product: ProductArrivalIn) -> dict[str, int]:
        await self.repository.save_product(product)
        content = self.content_builder.build(product)
        added = 0
        now = datetime.now(timezone.utc)
        for offset, platform in enumerate(self.publishers):
            payload = PublishRequest(product_id=product.product_id, platform=platform, content=content).model_dump(mode="json")
            scheduled_at = now + timedelta(seconds=offset * self.spacing_seconds)
            if await self.repository.enqueue(product, platform, payload, scheduled_at):
                added += 1
        await self.repository.commit()
        return {"added": added, "platforms": len(self.publishers)}

    async def run_due(self) -> dict[str, int]:
        jobs = await self.repository.due_jobs(datetime.now(timezone.utc))
        published = 0
        failed = 0
        for job in jobs:
            request = PublishRequest.model_validate(job.payload)
            publisher = self.publishers[request.platform]
            try:
                result = await publisher.publish(request)
                await self.repository.mark_done(job, result.external_id)
                published += 1
            except Exception as exc:
                await self.repository.mark_failed(job, str(exc))
                failed += 1
        await self.repository.commit()
        return {"published": published, "failed": failed}
