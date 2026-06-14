import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot import router
from app.config import settings
from app.hh_client.client import HHClient
from app.scheduler import VacancyScheduler
from app.telegram import TelegramNotifier


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    hh_client = HHClient()
    scheduler = VacancyScheduler(hh_client, TelegramNotifier(bot))
    stop_event = asyncio.Event()
    poller = asyncio.create_task(scheduler.run_forever(stop_event))

    try:
        await dispatcher.start_polling(bot)
    finally:
        stop_event.set()
        await poller
        await hh_client.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
