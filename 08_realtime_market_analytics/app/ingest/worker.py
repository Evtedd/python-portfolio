import asyncio
import logging

from app.bus.memory import EventBus
from app.config import settings
from app.db.base import Base
from app.db.session import engine
from app.service import MarketService


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    stop_event = asyncio.Event()
    await MarketService(EventBus(settings.queue_max_size)).run(stop_event)


if __name__ == "__main__":
    asyncio.run(main())
