import asyncio
import logging
from typing import Any

from app.connectors.registry import ConnectorRegistry
from app.core.template import render_value
from app.schemas import FlowDefinition, RunResult, StepResult

logger = logging.getLogger(__name__)


class FlowEngine:
    def __init__(self, registry: ConnectorRegistry) -> None:
        self.registry = registry

    async def run(self, flow: FlowDefinition, event: dict[str, Any]) -> RunResult:
        context: dict[str, Any] = {"event": event}
        result = RunResult(flow_name=flow.name, status="success", context=context)
        for step in flow.steps:
            connector = self.registry.get(step.connector)
            rendered_input = render_value(step.input, context)
            rendered_settings = render_value(step.settings, context)
            try:
                output = await self._run_with_retries(connector, rendered_settings, rendered_input, step.retries)
                context[step.name] = output
                result.steps.append(StepResult(name=step.name, status="success", output=output))
            except Exception as exc:
                logger.exception("flow step failed", extra={"flow": flow.name, "step": step.name})
                result.status = "failed"
                result.steps.append(StepResult(name=step.name, status="failed", error=str(exc)))
                break
        result.context = context
        return result

    @staticmethod
    async def _run_with_retries(connector, settings: dict[str, Any], payload: dict[str, Any], retries: int) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                return await connector.run(settings, payload)
            except Exception as exc:
                last_error = exc
                if attempt >= retries:
                    break
                await asyncio.sleep(0.2 * (attempt + 1))
        raise RuntimeError(str(last_error)) from last_error
