from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.db.session import SessionFactory
from app.models.vacancy import VacancyStatus
from app.repository import VacancyRepository

router = Router()


@router.message(Command("stats"))
async def stats(message: Message) -> None:
    async with SessionFactory() as session:
        data = await VacancyRepository(session).stats()

    await message.answer(
        "Статистика:\n"
        f"Найдено: {data['found']}\n"
        f"Подошло по фильтрам: {data['matched']}\n"
        f"Откликов: {data['applied']}",
    )


@router.callback_query(lambda call: call.data and call.data.startswith("vacancy_status:"))
async def update_vacancy_status(call: CallbackQuery) -> None:
    _, vacancy_id, status = call.data.split(":")
    async with SessionFactory() as session:
        vacancy = await VacancyRepository(session).update_status(
            vacancy_id=int(vacancy_id),
            status=VacancyStatus(status),
        )

    if vacancy is None:
        await call.answer("Вакансия не найдена.", show_alert=True)
        return

    await call.answer("Статус обновлён.")
