import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self, max_size: int) -> None:
        self.max_size = max_size
        self.subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)

    def subscribe(self, symbol: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_size)
        self.subscribers[symbol.upper()].add(queue)
        return queue

    def unsubscribe(self, symbol: str, queue: asyncio.Queue) -> None:
        self.subscribers[symbol.upper()].discard(queue)

    async def publish(self, symbol: str, event: dict[str, Any]) -> None:
        queues = list(self.subscribers.get(symbol.upper(), set()))
        for queue in queues:
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    continue
            await queue.put(event)
