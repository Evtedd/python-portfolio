import asyncio
import logging

from app.db.base import Base
from app.db.session import SessionFactory, engine
from app.workers.indexer import worker_loop


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    stop_event = asyncio.Event()
    await worker_loop(SessionFactory, stop_event)


if __name__ == "__main__":
    asyncio.run(main())
