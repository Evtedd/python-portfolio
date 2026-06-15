import logging

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.session import get_session
from app.service import CardPublishingService, PublishReport

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="WB card publisher")


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, bool | str]:
    return {"ok": True, "dry_run": settings.dry_run, "source_type": settings.source_type}


@app.post("/runs", response_model=PublishReport)
async def run_import(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> PublishReport:
    service = CardPublishingService(settings, session)
    return await service.run()
