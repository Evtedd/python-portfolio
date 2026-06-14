from app.agents.critic import CriticAgent
from app.agents.executor import ExecutorAgent
from app.agents.planner import PlannerAgent
from app.config import settings
from app.core.state import OrchestrationState
from app.models import RunStatus
from app.repository import RunRepository


class OrchestrationEngine:
    def __init__(
        self,
        planner: PlannerAgent,
        executor: ExecutorAgent,
        critic: CriticAgent,
        repository: RunRepository | None = None,
    ) -> None:
        self.planner = planner
        self.executor = executor
        self.critic = critic
        self.repository = repository

    async def run(self, goal: str, run_id: int | None = None, max_steps: int | None = None) -> OrchestrationState:
        state = OrchestrationState(goal=goal)
        limit = max_steps or settings.max_steps
        state.plan = await self.planner.plan(goal)
        await self._event(run_id, state.step_count, "planner", "plan", {"steps": state.plan})

        while state.step_count < limit:
            step = state.next_step()
            if step is None:
                decision = await self.critic.review(state)
                await self._event(
                    run_id,
                    state.step_count,
                    "critic",
                    "review",
                    {"approved": decision.approved, "feedback": decision.feedback},
                )
                if decision.approved:
                    state.approved = True
                    state.stop_reason = "approved"
                    break
                if state.revision >= settings.max_revisions:
                    state.stop_reason = "revision_limit"
                    break
                state.revision += 1
                state.completed_steps.clear()
                continue

            state.step_count += 1
            output = await self.executor.execute(state, step)
            state.completed_steps.append(step)
            state.draft = f"{state.draft}\n{output}".strip()
            await self._event(
                run_id,
                state.step_count,
                "executor",
                "step_result",
                {"step": step, "output": output},
            )

        if state.stop_reason is None:
            state.stop_reason = "step_limit"
        return state

    async def _event(
        self,
        run_id: int | None,
        step: int,
        actor: str,
        event_type: str,
        payload: dict,
    ) -> None:
        if self.repository is not None and run_id is not None:
            await self.repository.add_event(run_id, step, actor, event_type, payload)


def status_from_state(state: OrchestrationState) -> RunStatus:
    if state.approved:
        return RunStatus.completed
    if state.stop_reason == "step_limit":
        return RunStatus.stopped
    return RunStatus.completed if state.draft else RunStatus.failed
