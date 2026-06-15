import logging

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.connectors.registry import build_default_registry
from app.core.engine import FlowEngine
from app.db.session import get_session
from app.repository import FlowRepository
from app.schemas import FlowDefinition, RunResult
from app.triggers.webhook import WebhookTrigger

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Self hosted automation")


def require_key(
    settings: Settings = Depends(get_settings),
    x_api_key: str | None = Header(default=None),
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    with open("app/web/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict:
    return {"ok": True, "fake_mode": settings.fake_mode}


@app.post("/flows", dependencies=[Depends(require_key)])
async def save_flow(flow: FlowDefinition, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    repository = FlowRepository(session)
    await repository.save_flow(flow)
    await repository.commit()
    return {"status": "saved", "name": flow.name}


@app.get("/flows", response_model=list[FlowDefinition], dependencies=[Depends(require_key)])
async def list_flows(session: AsyncSession = Depends(get_session)) -> list[FlowDefinition]:
    return await FlowRepository(session).list_flows()


@app.post("/flows/{name}/run", response_model=RunResult, dependencies=[Depends(require_key)])
async def run_flow(
    name: str,
    event: dict,
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> RunResult:
    repository = FlowRepository(session)
    flow = await repository.get_flow(name)
    if flow is None:
        raise HTTPException(status_code=404, detail="Flow not found")
    result = await FlowEngine(build_default_registry(settings)).run(flow, event)
    await repository.save_run(flow.name, event, result)
    await repository.commit()
    return result


@app.post("/webhooks/{key}")
async def webhook(
    key: str,
    event: dict,
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> list[RunResult]:
    repository = FlowRepository(session)
    flows = await WebhookTrigger(repository).match(key)
    engine = FlowEngine(build_default_registry(settings))
    results = []
    for flow in flows:
        result = await engine.run(flow, event)
        await repository.save_run(flow.name, event, result)
        results.append(result)
    await repository.commit()
    return results
