import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers import admin, common
from app.scheduler import reminder_loop


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(common.router)
    dispatcher.include_router(admin.router)

    stop_event = asyncio.Event()
    reminders = asyncio.create_task(reminder_loop(bot, stop_event))
    try:
        await dispatcher.start_polling(bot)
    finally:
        stop_event.set()
        await reminders
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
