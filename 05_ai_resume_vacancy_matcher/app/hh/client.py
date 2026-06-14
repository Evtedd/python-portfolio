import re

import httpx

from app.config import settings
from app.schemas import VacancyData


class HHClient:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(
            base_url=settings.hh_base_url,
            timeout=20,
            headers={"User-Agent": "resume-vacancy-matcher/1.0"},
        )

    def fetch_vacancy(self, vacancy_id: str) -> VacancyData:
        response = self.client.get(f"/vacancies/{vacancy_id}")
        response.raise_for_status()
        data = response.json()
        description = strip_html(data.get("description") or "")
        return VacancyData(
            source_id=str(data["id"]),
            title=data["name"],
            company=(data.get("employer") or {}).get("name"),
            url=data.get("alternate_url"),
            text=description,
        )


def strip_html(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()
