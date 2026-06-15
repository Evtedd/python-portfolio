from typing import Any

from app.connectors.base import Connector
from app.connectors.registry import ConnectorRegistry
from app.core.engine import FlowEngine
from app.schemas import ActionStep, FlowDefinition, TriggerSpec


class FlakyConnector(Connector):
    name = "flaky"

    def __init__(self) -> None:
        self.calls = 0

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary")
        return {"value": payload["value"]}


async def test_engine_retries_and_passes_context() -> None:
    connector = FlakyConnector()
    registry = ConnectorRegistry()
    registry.register(connector)
    flow = FlowDefinition(
        name="flow",
        trigger=TriggerSpec(type="webhook", key="x"),
        steps=[ActionStep(name="step1", connector="flaky", input={"value": "{{event.value}}"}, retries=1)],
    )

    result = await FlowEngine(registry).run(flow, {"value": "ok"})

    assert result.status == "success"
    assert result.context["step1"]["value"] == "ok"
    assert connector.calls == 2
