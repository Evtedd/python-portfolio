from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketStatus


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1, max_length=10000)


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    status: TicketStatus | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    comments: list[CommentRead] = []
