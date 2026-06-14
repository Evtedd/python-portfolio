from typing import Any

from pydantic import ValidationError

from app.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise LookupError(f"Unknown tool: {name}") from exc

    async def run(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(name)
        try:
            parsed = tool.args_model.model_validate(arguments)
        except ValidationError as exc:
            raise ValueError(exc.errors()) from exc
        return await tool.run(parsed)

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.args_model.model_json_schema(),
            }
            for tool in self._tools.values()
        ]
