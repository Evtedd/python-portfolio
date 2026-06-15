from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings


def build_scheduler(settings: Settings, run_once) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_once, "interval", seconds=settings.sync_interval_seconds, id="sync-all", replace_existing=True)
    return scheduler
