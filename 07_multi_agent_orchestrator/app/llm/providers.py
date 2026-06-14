from typing import Protocol

import httpx

from app.config import settings
from app.core.state import OrchestrationState
from app.llm.types import CriticDecision, ExecutorDecision, ToolCall


class LLMProvider(Protocol):
    async def plan(self, goal: str) -> list[str]:
        ...

    async def execute(self, state: OrchestrationState, step: str) -> ExecutorDecision:
        ...

    async def critic(self, state: OrchestrationState) -> CriticDecision:
        ...


class FakeLLMProvider:
    async def plan(self, goal: str) -> list[str]:
        if "calculate" in goal.lower() or "посчитай" in goal.lower():
            return ["Run a small calculation", "Prepare final answer"]
        return ["Clarify useful facts", "Prepare final answer"]

    async def execute(self, state: OrchestrationState, step: str) -> ExecutorDecision:
        if "calculation" in step.lower():
            return ExecutorDecision(
                content="The calculation tool should be used.",
                tool_calls=[ToolCall(name="python_code", arguments={"code": "print(2 + 2)"})],
            )
        if "facts" in step.lower():
            return ExecutorDecision(
                content=f"Relevant fact saved for goal: {state.goal}",
                tool_calls=[ToolCall(name="memory_save", arguments={"text": state.goal})],
            )
        return ExecutorDecision(content=f"Final answer for: {state.goal}")

    async def critic(self, state: OrchestrationState) -> CriticDecision:
        approved = bool(state.draft.strip()) and len(state.completed_steps) >= len(state.plan)
        feedback = "Result is complete." if approved else "Continue execution."
        return CriticDecision(approved=approved, feedback=feedback)


class OpenAICompatibleProvider:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=45,
        )

    async def plan(self, goal: str) -> list[str]:
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": settings.llm_model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Split this goal into 2 to 5 concrete steps:\n{goal}",
                    },
                ],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        steps = [line.strip(" -0123456789.") for line in text.splitlines() if line.strip()]
        return steps[:5] or [goal]

    async def execute(self, state: OrchestrationState, step: str) -> ExecutorDecision:
        return ExecutorDecision(content=f"{step}: provider response is available in configured LLM.")

    async def critic(self, state: OrchestrationState) -> CriticDecision:
        return CriticDecision(approved=True, feedback="Approved by configured provider.")


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai" and settings.llm_api_key:
        return OpenAICompatibleProvider()
    return FakeLLMProvider()
