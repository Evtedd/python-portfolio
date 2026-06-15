from datetime import datetime

from app.content import ContentBuilder
from app.queue import PublicationQueue
from app.schemas import ProductArrivalIn, PublishResult


class FakeRepository:
    def __init__(self) -> None:
        self.keys: set[tuple[str, str]] = set()
        self.saved = 0

    async def save_product(self, product: ProductArrivalIn) -> None:
        self.saved += 1

    async def enqueue(self, product: ProductArrivalIn, platform: str, payload: dict, scheduled_at: datetime) -> bool:
        key = (product.product_id, platform)
        if key in self.keys:
            return False
        self.keys.add(key)
        return True

    async def commit(self) -> None:
        return None


class FakePublisher:
    platform = "instagram"

    async def publish(self, request):
        return PublishResult(platform=self.platform, external_id="ok", dry_run=True)


async def test_queue_deduplicates_product_platform() -> None:
    repo = FakeRepository()
    queue = PublicationQueue(repo, {"instagram": FakePublisher()}, ContentBuilder(), 60)
    product = ProductArrivalIn(product_id="sku1", name="A", url="https://shop.example/a")

    first = await queue.enqueue_product(product)
    second = await queue.enqueue_product(product)

    assert first["added"] == 1
    assert second["added"] == 0
