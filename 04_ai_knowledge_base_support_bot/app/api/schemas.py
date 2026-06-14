from datetime import datetime

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    chunks_count: int
    created_at: datetime


class QuestionIn(BaseModel):
    question: str


class SourceRead(BaseModel):
    document: str
    chunk: int
    page: int | None
    score: float


class AnswerOut(BaseModel):
    answer: str
    sources: list[SourceRead]
