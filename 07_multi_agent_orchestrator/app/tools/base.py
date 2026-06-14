from typing import Any, Protocol

from pydantic import BaseModel


class Tool(Protocol):
    name: str
    description: str
    args_model: type[BaseModel]

    async def run(self, arguments: BaseModel) -> dict[str, Any]:
        ...
