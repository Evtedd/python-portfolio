from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, get_session
from app.hh.client import HHClient
from app.llm.client import get_analyzer
from app.models import ApplicationStatus
from app.repository import MatchRepository
from app.schemas import DashboardStats, MatchRead
from app.services import MatchService, to_match_read

app = FastAPI(
    title="AI Resume & Vacancy Matcher",
    description="Resume parsing, HH vacancy fetching, matching score and cover letters.",
    version="1.0.0",
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/match", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def match_resume(
    resume: UploadFile = File(...),
    vacancy_input: str | None = Form(default=None),
    vacancy_text: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> MatchRead:
    content = await resume.read()
    service = MatchService(session, get_analyzer(), HHClient())
    try:
        return service.match(
            resume_filename=resume.filename or "resume.txt",
            resume_content=content,
            vacancy_input=vacancy_input,
            vacancy_text=vacancy_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get("/matches", response_model=list[MatchRead])
def matches(session: Session = Depends(get_session)) -> list[MatchRead]:
    repository = MatchRepository(session)
    return [to_match_read(item) for item in repository.list_matches()]


@app.post("/matches/{match_id}/applications/{application_status}", status_code=status.HTTP_201_CREATED)
def mark_application(
    match_id: int,
    application_status: ApplicationStatus,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    MatchRepository(session).mark_application(match_id, application_status)
    return {"status": application_status.value}


@app.get("/stats", response_model=DashboardStats)
def stats(session: Session = Depends(get_session)) -> DashboardStats:
    return MatchRepository(session).stats()
