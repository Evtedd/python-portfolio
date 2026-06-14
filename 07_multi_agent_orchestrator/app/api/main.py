import asyncio
import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.critic import CriticAgent
from app.agents.executor import ExecutorAgent
from app.agents.planner import PlannerAgent
from app.core.engine import OrchestrationEngine, status_from_state
from app.db.base import Base
from app.db.session import engine, get_session
from app.llm.providers import get_llm_provider
from app.memory.store import VectorMemory
from app.repository import RunRepository
from app.schemas import RunCreate, RunRead
from app.tools.defaults import build_default_registry

app = FastAPI(title="Multi agent AI Orchestrator", version="1.0.0")


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.post("/runs", response_model=RunRead)
async def create_run(
    payload: RunCreate,
    session: AsyncSession = Depends(get_session),
) -> RunRead:
    repository = RunRepository(session)
    run = await repository.create(payload.goal)
    memory = VectorMemory()
    llm = get_llm_provider()
    tools = build_default_registry(memory)
    orchestrator = OrchestrationEngine(
        PlannerAgent(llm),
        ExecutorAgent(llm, tools),
        CriticAgent(llm),
        repository,
    )
    state = await orchestrator.run(payload.goal, run_id=run.id, max_steps=payload.max_steps)
    await repository.finish(run.id, status_from_state(state), state.draft, state.step_count)
    stored = await repository.get(run.id)
    return stored


@app.get("/runs/{run_id}", response_model=RunRead)
async def get_run(run_id: int, session: AsyncSession = Depends(get_session)) -> RunRead:
    run = await RunRepository(session).get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/runs/{run_id}/stream")
async def stream_events(run_id: int, session: AsyncSession = Depends(get_session)) -> StreamingResponse:
    async def event_source():
        last_id = 0
        repository = RunRepository(session)
        while True:
            run = await repository.get(run_id)
            if run is None:
                yield "event: error\ndata: Run not found\n\n"
                break
            events = await repository.events_after(run_id, last_id)
            for event in events:
                last_id = event.id
                yield f"data: {json.dumps({'id': event.id, 'payload': event.payload})}\n\n"
            if run.status != "running" and not events:
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(event_source(), media_type="text/event-stream")
