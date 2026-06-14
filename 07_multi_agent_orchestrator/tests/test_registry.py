import pytest
from pydantic import BaseModel, Field

from app.tools.registry import ToolRegistry


class Args(BaseModel):
    value: int = Field(gt=0)


class DoubleTool:
    name = "double"
    description = "Double a number"
    args_model = Args

    async def run(self, arguments: Args) -> dict:
        return {"value": arguments.value * 2}


pytestmark = pytest.mark.asyncio


async def test_registry_validates_arguments():
    registry = ToolRegistry()
    registry.register(DoubleTool())

    assert await registry.run("double", {"value": 3}) == {"value": 6}

    with pytest.raises(ValueError):
        await registry.run("double", {"value": 0})
