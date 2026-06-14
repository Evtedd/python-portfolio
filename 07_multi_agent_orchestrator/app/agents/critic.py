from app.core.state import OrchestrationState
from app.llm.providers import LLMProvider
from app.llm.types import CriticDecision


class CriticAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def review(self, state: OrchestrationState) -> CriticDecision:
        return await self.llm.critic(state)
