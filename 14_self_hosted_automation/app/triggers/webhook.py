from app.repository import FlowRepository
from app.schemas import FlowDefinition


class WebhookTrigger:
    def __init__(self, repository: FlowRepository) -> None:
        self.repository = repository

    async def match(self, key: str) -> list[FlowDefinition]:
        return await self.repository.flows_for_webhook(key)
