import asyncio
import logging

from app.queue import PublicationQueue

logger = logging.getLogger(__name__)


async def run_forever(queue: PublicationQueue, interval_seconds: int = 60) -> None:
    while True:
        result = await queue.run_due()
        if result["published"] or result["failed"]:
            logger.info("publication queue processed", extra=result)
        await asyncio.sleep(interval_seconds)
