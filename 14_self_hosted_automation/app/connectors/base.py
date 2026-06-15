from abc import ABC, abstractmethod
from typing import Any


class Connector(ABC):
    name: str

    @abstractmethod
    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        ...
