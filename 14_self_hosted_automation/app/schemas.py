from typing import Any

from pydantic import BaseModel, Field


class TriggerSpec(BaseModel):
    type: str
    key: str | None = None
    cron: str | None = None
    url: str | None = None


class ActionStep(BaseModel):
    name: str
    connector: str
    settings: dict[str, Any] = Field(default_factory=dict)
    input: dict[str, Any] = Field(default_factory=dict)
    retries: int = 2


class FlowDefinition(BaseModel):
    name: str
    enabled: bool = True
    trigger: TriggerSpec
    steps: list[ActionStep]


class StepResult(BaseModel):
    name: str
    status: str
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RunResult(BaseModel):
    flow_name: str
    status: str
    steps: list[StepResult] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
