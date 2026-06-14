from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    kind: str
    content_type: str
    status: str
    error: str | None
    created_at: datetime


class SearchRequest(BaseModel):
    query: str
    top_k: int | None = None


class SearchResultRead(BaseModel):
    asset_id: int
    filename: str
    kind: str
    segment_id: int
    text: str
    score: float
    page: int | None = None
    start_seconds: float | None = None
    end_seconds: float | None = None
    preview_path: str | None = None


class SummaryRequest(BaseModel):
    asset_id: int | None = None
    query: str | None = None


class SummaryRead(BaseModel):
    answer: str
    sources: list[SearchResultRead]
