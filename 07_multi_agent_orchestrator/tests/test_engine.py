import pytest

from app.agents.critic import CriticAgent
from app.agents.executor import ExecutorAgent
from app.agents.planner import PlannerAgent
from app.core.engine import OrchestrationEngine
from app.llm.providers import FakeLLMProvider
from app.memory.store import VectorMemory
from app.tools.defaults import build_default_registry


pytestmark = pytest.mark.asyncio


async def test_fake_cycle_finishes_with_result():
    llm = FakeLLMProvider()
    registry = build_default_registry(VectorMemory())
    engine = OrchestrationEngine(
        PlannerAgent(llm),
        ExecutorAgent(llm, registry),
        CriticAgent(llm),
    )

    state = await engine.run("calculate a tiny result", max_steps=5)

    assert state.approved
    assert "python_code" in state.draft


async def test_engine_stops_by_step_limit():
    llm = FakeLLMProvider()
    engine = OrchestrationEngine(
        PlannerAgent(llm),
        ExecutorAgent(llm, build_default_registry(VectorMemory())),
        CriticAgent(llm),
    )

    state = await engine.run("calculate a tiny result", max_steps=1)

    assert state.stop_reason == "step_limit"
