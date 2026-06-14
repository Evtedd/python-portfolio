from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunCreate(BaseModel):
    goal: str = Field(min_length=3, max_length=5000)
    max_steps: int | None = Field(default=None, ge=1, le=50)


class TraceEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    step: int
    actor: str
    event_type: str
    payload: str
    created_at: datetime


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal: str
    status: str
    result: str | None
    step_count: int
    created_at: datetime
    events: list[TraceEventRead] = []
