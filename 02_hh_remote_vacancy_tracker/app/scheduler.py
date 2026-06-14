import asyncio
import logging

from app.config import settings
from app.db.session import SessionFactory
from app.filters import VacancyFilter
from app.hh_client.client import HHClient
from app.repository import VacancyRepository
from app.telegram import TelegramNotifier

logger = logging.getLogger(__name__)


class VacancyScheduler:
    def __init__(self, hh_client: HHClient, notifier: TelegramNotifier) -> None:
        self.hh_client = hh_client
        self.notifier = notifier
        self.filter = VacancyFilter(
            settings.whitelist_keywords,
            settings.blacklist_keywords,
        )

    async def run_once(self) -> tuple[int, int]:
        found_count = 0
        matched_count = 0

        async with SessionFactory() as session:
            repository = VacancyRepository(session)
            async for item in self.hh_client.iter_vacancies():
                found_count += 1
                if not self.filter.matches(item):
                    continue

                matched_count += 1
                vacancy = await repository.save_if_new(item)
                if vacancy is None:
                    continue

                await self.notifier.send_vacancy(vacancy)
                await repository.mark_notified(vacancy.id)

            await repository.save_run(found_count, matched_count)

        logger.info("HH poll finished: found=%s matched=%s", found_count, matched_count)
        return found_count, matched_count

    async def run_forever(self, stop_event: asyncio.Event) -> None:
        while not stop_event.is_set():
            try:
                await self.run_once()
            except Exception:
                logger.exception("HH polling failed")

            try:
                await asyncio.wait_for(stop_event.wait(), settings.poll_interval_seconds)
            except TimeoutError:
                continue
