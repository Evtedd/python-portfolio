from app.memory.store import VectorMemory
from app.tools.implementations import (
    HttpRequestTool,
    MemorySaveTool,
    PythonCodeTool,
    WebSearchTool,
)
from app.tools.registry import ToolRegistry


def build_default_registry(memory: VectorMemory | None = None) -> ToolRegistry:
    memory = memory or VectorMemory()
    registry = ToolRegistry()
    registry.register(PythonCodeTool())
    registry.register(HttpRequestTool())
    registry.register(MemorySaveTool(memory))
    registry.register(WebSearchTool())
    return registry
