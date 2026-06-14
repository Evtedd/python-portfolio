from datetime import datetime, timedelta, timezone

import pytest

from app.models.task import TaskStatus


pytestmark = pytest.mark.asyncio


async def test_create_and_filter_tasks(task_service):
    owner_id = 100
    await task_service.add_from_message(owner_id, "Fix report due:2026.06.20 #work")
    await task_service.add_from_message(owner_id, "Buy coffee #home")

    work_tasks = await task_service.repository.list_for_user(
        owner_id,
        category="work",
    )

    assert len(work_tasks) == 1
    assert work_tasks[0].text == "Fix report"
    assert work_tasks[0].deadline_at is not None


async def test_status_and_weekly_stats(task_service):
    owner_id = 101
    task = await task_service.add_from_message(owner_id, "Ship release #work")
    await task_service.change_status(owner_id, task.id, TaskStatus.done)

    stats = await task_service.repository.weekly_stats(owner_id)

    assert stats["created"] == 1
    assert stats["done"] == 1
    assert stats["overdue"] == 0


async def test_reminder_query(task_service):
    owner_id = 102
    task = await task_service.repository.create(
        owner_id=owner_id,
        text="Call customer",
        deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
    )

    reminders = await task_service.repository.due_for_reminder(minutes_before=30)

    assert [item.id for item in reminders] == [task.id]
