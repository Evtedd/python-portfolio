import json

from sqlalchemy.orm import Session

from app.hh.client import HHClient
from app.llm.client import MatchAnalyzer
from app.models import MatchResult
from app.parsing.resume import parse_resume
from app.parsing.vacancy import extract_hh_id
from app.repository import MatchRepository
from app.schemas import MatchRead, VacancyData


class MatchService:
    def __init__(
        self,
        session: Session,
        analyzer: MatchAnalyzer,
        hh_client: HHClient,
    ) -> None:
        self.repository = MatchRepository(session)
        self.analyzer = analyzer
        self.hh_client = hh_client

    def match(
        self,
        resume_filename: str,
        resume_content: bytes,
        vacancy_input: str | None,
        vacancy_text: str | None,
    ) -> MatchRead:
        resume_text = parse_resume(resume_filename, resume_content)
        vacancy = self.resolve_vacancy(vacancy_input, vacancy_text)
        analysis = self.analyzer.analyze(resume_text, vacancy)
        result = self.repository.save_match(resume_text, vacancy, analysis)
        return to_match_read(result)

    def resolve_vacancy(
        self,
        vacancy_input: str | None,
        vacancy_text: str | None,
    ) -> VacancyData:
        if vacancy_input:
            hh_id = extract_hh_id(vacancy_input)
            if hh_id:
                return self.hh_client.fetch_vacancy(hh_id)

        if vacancy_text and vacancy_text.strip():
            first_line = vacancy_text.strip().splitlines()[0][:255]
            return VacancyData(title=first_line or "Вакансия", text=vacancy_text.strip())

        raise ValueError("Provide HH vacancy link/id or vacancy text")


def to_match_read(result: MatchResult) -> MatchRead:
    return MatchRead(
        id=result.id,
        vacancy_id=result.vacancy_id,
        score=result.score,
        matched_skills=json.loads(result.matched_skills),
        missing_skills=json.loads(result.missing_skills),
        cover_letter=result.cover_letter,
        reasoning=result.reasoning,
        is_remote=result.is_remote,
        is_suspicious=result.is_suspicious,
        created_at=result.created_at,
    )
