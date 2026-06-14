import json

from app.core.state import OrchestrationState
from app.llm.providers import LLMProvider
from app.tools.registry import ToolRegistry


class ExecutorAgent:
    def __init__(self, llm: LLMProvider, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools

    async def execute(self, state: OrchestrationState, step: str) -> str:
        decision = await self.llm.execute(state, step)
        tool_outputs: list[str] = []
        for call in decision.tool_calls:
            output = await self.tools.run(call.name, call.arguments)
            tool_outputs.append(f"{call.name}: {json.dumps(output, ensure_ascii=False)}")
        suffix = "\n".join(tool_outputs)
        return decision.content if not suffix else f"{decision.content}\n{suffix}"
