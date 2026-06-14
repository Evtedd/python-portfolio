from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VacancyData(BaseModel):
    source_id: str | None = None
    title: str
    company: str | None = None
    url: str | None = None
    text: str


class MatchAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    cover_letter: str
    reasoning: str
    is_remote: bool
    is_suspicious: bool


class MatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vacancy_id: int
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    cover_letter: str
    reasoning: str
    is_remote: bool
    is_suspicious: bool
    created_at: datetime


class DashboardStats(BaseModel):
    total_matches: int
    average_score: float
    applied_count: int
