import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Run, RunStatus, TraceEvent


class RunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, goal: str) -> Run:
        run = Run(goal=goal, status=RunStatus.running.value)
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def add_event(
        self,
        run_id: int,
        step: int,
        actor: str,
        event_type: str,
        payload: dict,
    ) -> None:
        self.session.add(
            TraceEvent(
                run_id=run_id,
                step=step,
                actor=actor,
                event_type=event_type,
                payload=json.dumps(payload, ensure_ascii=False),
            ),
        )
        await self.session.commit()

    async def finish(
        self,
        run_id: int,
        status: RunStatus,
        result: str,
        step_count: int,
    ) -> None:
        run = await self.session.get(Run, run_id)
        if run is None:
            return
        run.status = status.value
        run.result = result
        run.step_count = step_count
        await self.session.commit()

    async def get(self, run_id: int) -> Run | None:
        return await self.session.scalar(
            select(Run).options(selectinload(Run.events)).where(Run.id == run_id),
        )

    async def events_after(self, run_id: int, event_id: int) -> list[TraceEvent]:
        result = await self.session.execute(
            select(TraceEvent)
            .where(TraceEvent.run_id == run_id, TraceEvent.id > event_id)
            .order_by(TraceEvent.id),
        )
        return list(result.scalars().all())
