import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.db.base import Base
from app.db.session import SessionFactory, engine
from app.embeddings.providers import get_embedding_provider
from app.llm.providers import get_llm_provider
from app.services import QAService

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Задайте вопрос по базе знаний.")


@router.message()
async def answer_question(message: Message) -> None:
    question = (message.text or "").strip()
    if not question:
        await message.answer("Пришлите текстовый вопрос.")
        return

    async with SessionFactory() as session:
        service = QAService(session, get_embedding_provider(), get_llm_provider())
        answer, sources = await service.ask(question)

    source_lines = [
        f"{item.document}, фрагмент {item.index}" + (f", стр. {item.page}" if item.page else "")
        for item in sources
    ]
    suffix = "\n\nИсточники:\n" + "\n".join(source_lines) if source_lines else ""
    await message.answer(answer + suffix)


async def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to run the bot")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
