from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Flow, FlowRun
from app.schemas import FlowDefinition, RunResult


class FlowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_flow(self, flow: FlowDefinition) -> None:
        statement = insert(Flow).values(
            name=flow.name,
            enabled=flow.enabled,
            definition=flow.model_dump(mode="json"),
        )
        statement = statement.on_conflict_do_update(
            index_elements=[Flow.name],
            set_={"enabled": flow.enabled, "definition": flow.model_dump(mode="json")},
        )
        await self.session.execute(statement)

    async def get_flow(self, name: str) -> FlowDefinition | None:
        result = await self.session.execute(select(Flow).where(Flow.name == name))
        flow = result.scalar_one_or_none()
        return FlowDefinition.model_validate(flow.definition) if flow else None

    async def flows_for_webhook(self, key: str) -> list[FlowDefinition]:
        result = await self.session.execute(select(Flow).where(Flow.enabled.is_(True)))
        flows = [FlowDefinition.model_validate(row.definition) for row in result.scalars().all()]
        return [flow for flow in flows if flow.trigger.type == "webhook" and flow.trigger.key == key]

    async def list_flows(self) -> list[FlowDefinition]:
        result = await self.session.execute(select(Flow).order_by(Flow.name))
        return [FlowDefinition.model_validate(row.definition) for row in result.scalars().all()]

    async def save_run(self, flow_name: str, event: dict, result: RunResult) -> None:
        self.session.add(
            FlowRun(
                flow_name=flow_name,
                status=result.status,
                input_payload=event,
                result=result.model_dump(mode="json"),
                error=None if result.status == "success" else result.steps[-1].error if result.steps else "failed",
            )
        )

    async def commit(self) -> None:
        await self.session.commit()
