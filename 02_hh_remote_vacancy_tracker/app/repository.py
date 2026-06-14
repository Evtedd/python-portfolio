from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.hh_client.schemas import HHVacancyItem
from app.models.vacancy import SearchRun, Vacancy, VacancyStatus


class VacancyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_if_new(self, item: HHVacancyItem) -> Vacancy | None:
        exists = await self.session.scalar(
            select(Vacancy.id).where(Vacancy.hh_id == item.id),
        )
        if exists:
            return None

        vacancy = Vacancy(
            hh_id=item.id,
            title=item.name,
            company=item.employer.name,
            salary=item.salary.humanize() if item.salary else None,
            url=str(item.alternate_url),
            area=item.area.name if item.area else None,
            description=item.searchable_text,
            status=VacancyStatus.new.value,
            published_at=item.published_at,
        )
        self.session.add(vacancy)
        await self.session.commit()
        await self.session.refresh(vacancy)
        return vacancy

    async def mark_notified(self, vacancy_id: int) -> None:
        vacancy = await self.session.get(Vacancy, vacancy_id)
        if vacancy is None:
            return
        vacancy.notified_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def update_status(
        self,
        vacancy_id: int,
        status: VacancyStatus,
    ) -> Vacancy | None:
        vacancy = await self.session.get(Vacancy, vacancy_id)
        if vacancy is None:
            return None
        vacancy.status = status.value
        await self.session.commit()
        await self.session.refresh(vacancy)
        return vacancy

    async def save_run(self, found_count: int, matched_count: int) -> None:
        self.session.add(SearchRun(found_count=found_count, matched_count=matched_count))
        await self.session.commit()

    async def stats(self) -> dict[str, int]:
        found = await self.session.scalar(select(func.coalesce(func.sum(SearchRun.found_count), 0)))
        matched = await self.session.scalar(
            select(func.coalesce(func.sum(SearchRun.matched_count), 0)),
        )
        applied = await self.session.scalar(
            select(func.count(Vacancy.id)).where(Vacancy.status == VacancyStatus.applied.value),
        )
        return {
            "found": int(found or 0),
            "matched": int(matched or 0),
            "applied": int(applied or 0),
        }
