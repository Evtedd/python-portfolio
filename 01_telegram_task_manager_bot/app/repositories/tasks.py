from datetime import datetime, timedelta, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        owner_id: int,
        text: str,
        deadline_at: datetime | None = None,
        category: str | None = None,
    ) -> Task:
        task = Task(
            owner_id=owner_id,
            text=text,
            deadline_at=deadline_at,
            category=category,
            status=TaskStatus.new.value,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_owned(self, owner_id: int, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task).where(Task.owner_id == owner_id, Task.id == task_id),
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        owner_id: int,
        status: TaskStatus | None = None,
        category: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[Task]:
        statement: Select[tuple[Task]] = select(Task).where(Task.owner_id == owner_id)
        if status:
            statement = statement.where(Task.status == status.value)
        if category:
            statement = statement.where(func.lower(Task.category) == category.lower())
        if query:
            statement = statement.where(Task.text.ilike(f"%{query}%"))

        statement = statement.order_by(Task.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update_status(
        self,
        owner_id: int,
        task_id: int,
        status: TaskStatus,
    ) -> Task | None:
        task = await self.get_owned(owner_id, task_id)
        if task is None:
            return None

        task.status = status.value
        task.done_at = datetime.now(timezone.utc) if status == TaskStatus.done else None
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def due_for_reminder(
        self,
        minutes_before: int,
        now: datetime | None = None,
    ) -> list[Task]:
        now = now or datetime.now(timezone.utc)
        reminder_edge = now + timedelta(minutes=minutes_before)
        result = await self.session.execute(
            select(Task)
            .where(Task.status != TaskStatus.done.value)
            .where(Task.deadline_at.is_not(None))
            .where(Task.reminded_at.is_(None))
            .where(Task.deadline_at <= reminder_edge)
            .order_by(Task.deadline_at.asc()),
        )
        return list(result.scalars().all())

    async def mark_reminded(self, task_id: int) -> None:
        task = await self.session.get(Task, task_id)
        if task is None:
            return
        task.reminded_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def weekly_stats(
        self,
        owner_id: int,
        now: datetime | None = None,
    ) -> dict[str, int]:
        now = now or datetime.now(timezone.utc)
        week_start = now - timedelta(days=7)

        created = await self.session.scalar(
            select(func.count(Task.id)).where(
                Task.owner_id == owner_id,
                Task.created_at >= week_start,
            ),
        )
        done = await self.session.scalar(
            select(func.count(Task.id)).where(
                Task.owner_id == owner_id,
                Task.done_at >= week_start,
            ),
        )
        overdue = await self.session.scalar(
            select(func.count(Task.id)).where(
                Task.owner_id == owner_id,
                Task.status != TaskStatus.done.value,
                Task.deadline_at < now,
            ),
        )
        return {
            "created": int(created or 0),
            "done": int(done or 0),
            "overdue": int(overdue or 0),
        }

    async def user_ids(self) -> list[int]:
        result = await self.session.execute(
            select(Task.owner_id).distinct().order_by(Task.owner_id),
        )
        return [int(item) for item in result.scalars().all()]

    async def total_stats(self) -> dict[str, int]:
        total = await self.session.scalar(select(func.count(Task.id)))
        done = await self.session.scalar(
            select(func.count(Task.id)).where(Task.status == TaskStatus.done.value),
        )
        overdue = await self.session.scalar(
            select(func.count(Task.id)).where(
                Task.status != TaskStatus.done.value,
                Task.deadline_at < datetime.now(timezone.utc),
            ),
        )
        return {
            "total": int(total or 0),
            "done": int(done or 0),
            "overdue": int(overdue or 0),
        }
