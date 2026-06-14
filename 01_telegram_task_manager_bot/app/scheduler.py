import asyncio
import logging

from aiogram import Bot

from app.config import settings
from app.db.session import SessionFactory
from app.repositories.tasks import TaskRepository

logger = logging.getLogger(__name__)


async def reminder_loop(bot: Bot, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            async with SessionFactory() as session:
                repository = TaskRepository(session)
                tasks = await repository.due_for_reminder(settings.reminder_minutes_before)
                for task in tasks:
                    if task.deadline_at is None:
                        continue
                    await bot.send_message(
                        task.owner_id,
                        f"Reminder: task #{task.id} is due at "
                        f"{task.deadline_at:%d.%m.%Y %H:%M}\n{task.text}",
                    )
                    await repository.mark_reminded(task.id)
        except Exception:
            logger.exception("Reminder loop failed")

        try:
            await asyncio.wait_for(stop_event.wait(), settings.reminder_poll_seconds)
        except TimeoutError:
            continue
