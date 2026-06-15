from abc import ABC, abstractmethod

from app.schemas import PublishRequest, PublishResult


class Publisher(ABC):
    platform: str

    @abstractmethod
    async def publish(self, request: PublishRequest) -> PublishResult:
        ...
