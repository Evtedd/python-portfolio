import asyncio
import logging

from redis.asyncio import Redis

from app.config import get_settings
from app.queue.redis_queue import RedisFlowQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    queue = RedisFlowQueue(redis)
    while True:
        item = await queue.pop()
        if item is None:
            continue
        logger.info("queued flow received", extra={"flow": item.get("flow_name")})


if __name__ == "__main__":
    asyncio.run(main())
