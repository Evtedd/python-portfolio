from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


class ExecutorDecision(BaseModel):
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)


class CriticDecision(BaseModel):
    approved: bool
    feedback: str
