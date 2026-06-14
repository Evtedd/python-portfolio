from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings
from app.db.session import SessionFactory
from app.repositories.tasks import TaskRepository

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin_users"))
async def admin_users(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Forbidden.")
        return

    async with SessionFactory() as session:
        users = await TaskRepository(session).user_ids()

    await message.answer("Users:\n" + "\n".join(map(str, users)) if users else "No users.")


@router.message(Command("admin_stats"))
async def admin_stats(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("Forbidden.")
        return

    async with SessionFactory() as session:
        data = await TaskRepository(session).total_stats()

    await message.answer(
        "Total stats:\n"
        f"Tasks: {data['total']}\n"
        f"Done: {data['done']}\n"
        f"Overdue: {data['overdue']}",
    )
