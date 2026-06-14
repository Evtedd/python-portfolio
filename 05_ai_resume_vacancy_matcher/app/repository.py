import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Application, ApplicationStatus, MatchResult, Vacancy
from app.schemas import DashboardStats, MatchAnalysis, VacancyData


class MatchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_match(
        self,
        resume_text: str,
        vacancy_data: VacancyData,
        analysis: MatchAnalysis,
    ) -> MatchResult:
        vacancy = Vacancy(
            source_id=vacancy_data.source_id,
            title=vacancy_data.title,
            company=vacancy_data.company,
            url=vacancy_data.url,
            text=vacancy_data.text,
        )
        self.session.add(vacancy)
        self.session.flush()

        result = MatchResult(
            vacancy_id=vacancy.id,
            resume_text=resume_text,
            score=analysis.score,
            matched_skills=json.dumps(analysis.matched_skills, ensure_ascii=False),
            missing_skills=json.dumps(analysis.missing_skills, ensure_ascii=False),
            cover_letter=analysis.cover_letter,
            reasoning=analysis.reasoning,
            is_remote=analysis.is_remote,
            is_suspicious=analysis.is_suspicious,
        )
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def list_matches(self) -> list[MatchResult]:
        return list(
            self.session.scalars(
                select(MatchResult)
                .options(selectinload(MatchResult.vacancy))
                .order_by(MatchResult.created_at.desc()),
            ).all(),
        )

    def mark_application(
        self,
        match_result_id: int,
        status: ApplicationStatus,
    ) -> Application:
        application = Application(match_result_id=match_result_id, status=status.value)
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application

    def stats(self) -> DashboardStats:
        total = self.session.scalar(select(func.count(MatchResult.id))) or 0
        average = self.session.scalar(select(func.avg(MatchResult.score))) or 0
        applied = (
            self.session.scalar(
                select(func.count(Application.id)).where(
                    Application.status == ApplicationStatus.applied.value,
                ),
            )
            or 0
        )
        return DashboardStats(
            total_matches=int(total),
            average_score=float(round(average, 2)),
            applied_count=int(applied),
        )
