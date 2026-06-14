from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.config import settings
from app.models.vacancy import Vacancy, VacancyStatus


def vacancy_keyboard(vacancy: Vacancy) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Откликнулся",
                    callback_data=f"vacancy_status:{vacancy.id}:{VacancyStatus.applied.value}",
                ),
                InlineKeyboardButton(
                    text="Позже",
                    callback_data=f"vacancy_status:{vacancy.id}:{VacancyStatus.later.value}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Не подходит",
                    callback_data=f"vacancy_status:{vacancy.id}:{VacancyStatus.rejected.value}",
                ),
            ],
        ],
    )


class TelegramNotifier:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def send_vacancy(self, vacancy: Vacancy) -> None:
        salary = vacancy.salary or "зарплата не указана"
        text = (
            f"{vacancy.title}\n"
            f"{vacancy.company}\n"
            f"{salary}\n"
            f"{vacancy.url}"
        )
        await self.bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            reply_markup=vacancy_keyboard(vacancy),
            disable_web_page_preview=True,
        )
