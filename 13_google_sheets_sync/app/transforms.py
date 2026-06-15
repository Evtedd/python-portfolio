from typing import Any

from app.config import SyncTask


def map_row(task: SyncTask, row: dict[str, Any]) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for sheet_column, target_column in task.columns.items():
        value = row.get(sheet_column)
        mapped[target_column] = normalize_value(value)
    return mapped


def normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.replace(".", "", 1).isdigit():
            return float(stripped) if "." in stripped else int(stripped)
        return stripped
    return value
