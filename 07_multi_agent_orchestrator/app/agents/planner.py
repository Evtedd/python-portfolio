from app.llm.providers import LLMProvider


class PlannerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def plan(self, goal: str) -> list[str]:
        return await self.llm.plan(goal)
