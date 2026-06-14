import asyncio
import logging
from collections.abc import AsyncIterator

import httpx

from app.config import settings
from app.hh_client.schemas import HHVacancyItem, HHVacancyResponse

logger = logging.getLogger(__name__)


class HHClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self.http_client = http_client or httpx.AsyncClient(
            base_url="https://api.hh.ru",
            timeout=settings.http_timeout_seconds,
            headers={"User-Agent": "hh-remote-vacancy-tracker/1.0"},
        )
        self._owns_client = http_client is None

    async def close(self) -> None:
        if self._owns_client:
            await self.http_client.aclose()

    async def search_page(self, page: int) -> HHVacancyResponse:
        params = {
            "text": settings.hh_text,
            "area": settings.hh_area,
            "schedule": "remote",
            "per_page": settings.hh_per_page,
            "page": page,
        }
        for attempt in range(3):
            try:
                response = await self.http_client.get("/vacancies", params=params)
                response.raise_for_status()
                return HHVacancyResponse.model_validate(response.json())
            except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                if attempt == 2:
                    raise
                delay = 1.5 * (attempt + 1)
                logger.warning("HH request failed: %s. Retrying in %.1fs", exc, delay)
                await asyncio.sleep(delay)

        raise RuntimeError("HH request retry loop ended unexpectedly")

    async def iter_vacancies(self) -> AsyncIterator[HHVacancyItem]:
        first_page = await self.search_page(0)
        for item in first_page.items:
            yield item

        for page in range(1, first_page.pages):
            await asyncio.sleep(0.25)
            next_page = await self.search_page(page)
            for item in next_page.items:
                yield item
