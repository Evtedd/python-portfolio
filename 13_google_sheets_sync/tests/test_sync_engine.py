from app.config import SyncTask
from app.sheets_client import InMemorySheetsClient
from app.sync.engine import SyncEngine


class MemoryRepository:
    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    async def start_run(self, task_name: str):
        return object()

    async def finish_run(self, run, status: str, processed: int, failed: int, error: str | None = None) -> None:
        self.status = status

    async def upsert_row(self, task: SyncTask, row: dict) -> str:
        key = row[task.key_column]
        action = "updated" if key in self.rows else "created"
        self.rows[key] = row
        return action

    async def rows_for_task(self, task_name: str) -> list[dict]:
        return list(self.rows.values())

    async def commit(self) -> None:
        return None


async def test_sync_engine_skips_broken_rows() -> None:
    task = SyncTask(
        name="products",
        spreadsheet_id="demo",
        range_name="products!A:Z",
        table_name="products",
        key_column="sku",
        columns={"sku": "sku", "name": "name"},
    )
    sheets = InMemorySheetsClient({"demo:products!A:Z": [{"sku": "A1", "name": "One"}, {"sku": "", "name": "Broken"}]})
    repo = MemoryRepository()

    result = await SyncEngine(sheets, repo).run_task(task)

    assert result.processed == 1
    assert result.failed == 1
    assert repo.rows["A1"]["name"] == "One"
