from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.schemas import FlowDefinition


def add_schedule_jobs(scheduler: AsyncIOScheduler, flows: list[FlowDefinition], run_flow) -> None:
    for flow in flows:
        if flow.enabled and flow.trigger.type == "schedule" and flow.trigger.cron:
            scheduler.add_job(run_flow, "cron", id=flow.name, replace_existing=True, args=[flow.name])
