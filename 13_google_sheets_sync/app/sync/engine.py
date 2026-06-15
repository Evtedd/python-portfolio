import logging

from pydantic import BaseModel, Field

from app.config import SyncTask
from app.repository import SyncRepository
from app.sheets_client import SheetsClient
from app.transforms import map_row
from app.validation import RowError, validate_row

logger = logging.getLogger(__name__)


class TaskResult(BaseModel):
    task_name: str
    processed: int = 0
    failed: int = 0
    errors: list[str] = Field(default_factory=list)


class SyncEngine:
    def __init__(self, sheets_client: SheetsClient, repository: SyncRepository) -> None:
        self.sheets_client = sheets_client
        self.repository = repository

    async def run_task(self, task: SyncTask) -> TaskResult:
        run = await self.repository.start_run(task.name)
        result = TaskResult(task_name=task.name)
        try:
            source_rows = await self.sheets_client.read_rows(task.spreadsheet_id, task.range_name)
            for number, raw_row in enumerate(source_rows, start=2):
                mapped = map_row(task, raw_row)
                error = validate_row(mapped, task.key_column, number)
                if error:
                    self._add_error(result, error)
                    continue
                await self.repository.upsert_row(task, mapped)
                result.processed += 1
            if task.bidirectional:
                rows = await self.repository.rows_for_task(task.name)
                await self.sheets_client.write_rows(task.spreadsheet_id, task.range_name, rows)
            status = "success" if result.failed == 0 else "partial"
            await self.repository.finish_run(run, status, result.processed, result.failed)
            await self.repository.commit()
            return result
        except Exception as exc:
            logger.exception("sync task failed", extra={"task": task.name})
            await self.repository.finish_run(run, "failed", result.processed, result.failed, str(exc))
            await self.repository.commit()
            raise

    @staticmethod
    def _add_error(result: TaskResult, error: RowError) -> None:
        result.failed += 1
        result.errors.append(f"row {error.row_number}: {error.message}")
