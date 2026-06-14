from dataclasses import dataclass, field


@dataclass
class OrchestrationState:
    goal: str
    plan: list[str] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    draft: str = ""
    revision: int = 0
    step_count: int = 0
    approved: bool = False
    stop_reason: str | None = None

    def next_step(self) -> str | None:
        if len(self.completed_steps) >= len(self.plan):
            return None
        return self.plan[len(self.completed_steps)]
