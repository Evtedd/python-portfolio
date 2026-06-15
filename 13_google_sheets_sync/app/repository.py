import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SyncTask
from app.models import AuditLog, SyncRun, SyncedRow


class SyncRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def start_run(self, task_name: str) -> SyncRun:
        run = SyncRun(task_name=task_name, status="running")
        self.session.add(run)
        await self.session.flush()
        return run

    async def finish_run(self, run: SyncRun, status: str, processed: int, failed: int, error: str | None = None) -> None:
        run.status = status
        run.processed = processed
        run.failed = failed
        run.error = error
        run.finished_at = datetime.now(timezone.utc)

    async def upsert_row(self, task: SyncTask, row: dict) -> str:
        external_key = str(row[task.key_column])
        checksum = _checksum(row)
        existing = await self.session.execute(
            select(SyncedRow).where(SyncedRow.task_name == task.name, SyncedRow.external_key == external_key)
        )
        current = existing.scalar_one_or_none()
        action = "unchanged"
        if current is None:
            action = "created"
        elif current.checksum != checksum:
            action = "updated"
        if action != "unchanged":
            self.session.add(
                AuditLog(
                    task_name=task.name,
                    external_key=external_key,
                    action=action,
                    before=current.payload if current else None,
                    after=row,
                )
            )
        statement = insert(SyncedRow).values(
            task_name=task.name,
            table_name=task.table_name,
            external_key=external_key,
            checksum=checksum,
            payload=row,
        )
        statement = statement.on_conflict_do_update(
            index_elements=[SyncedRow.task_name, SyncedRow.external_key],
            set_={"checksum": checksum, "payload": row},
        )
        await self.session.execute(statement)
        return action

    async def rows_for_task(self, task_name: str) -> list[dict]:
        result = await self.session.execute(select(SyncedRow.payload).where(SyncedRow.task_name == task_name))
        return list(result.scalars().all())

    async def last_success(self) -> datetime | None:
        result = await self.session.execute(
            select(SyncRun.finished_at).where(SyncRun.status == "success").order_by(SyncRun.finished_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        await self.session.commit()


def _checksum(row: dict) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
