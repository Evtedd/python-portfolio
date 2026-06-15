import json

from redis.asyncio import Redis


class RedisFlowQueue:
    def __init__(self, redis: Redis, key: str = "flow-runs") -> None:
        self.redis = redis
        self.key = key

    async def enqueue(self, flow_name: str, event: dict) -> None:
        await self.redis.rpush(self.key, json.dumps({"flow_name": flow_name, "event": event}, ensure_ascii=False))

    async def pop(self) -> dict | None:
        item = await self.redis.blpop(self.key, timeout=5)
        if not item:
            return None
        return json.loads(item[1])
