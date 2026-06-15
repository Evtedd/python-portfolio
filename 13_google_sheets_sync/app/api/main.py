import logging

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_session
from app.monitoring.alerts import AlertService
from app.repository import SyncRepository
from app.sheets_client import build_sheets_client
from app.sync.engine import SyncEngine, TaskResult

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Google Sheets sync")


@app.get("/health")
async def health(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> dict:
    last_success = await SyncRepository(session).last_success()
    return {"ok": True, "fake_mode": settings.google_fake_mode, "last_success": last_success}


@app.post("/sync", response_model=list[TaskResult])
async def run_sync(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> list[TaskResult]:
    repository = SyncRepository(session)
    engine = SyncEngine(build_sheets_client(settings), repository)
    alerts = AlertService(settings)
    results: list[TaskResult] = []
    for task in settings.sync_tasks:
        try:
            results.append(await engine.run_task(task))
        except Exception as exc:
            await alerts.sync_failed(task.name, str(exc))
            results.append(TaskResult(task_name=task.name, failed=1, errors=[str(exc)]))
    return results
