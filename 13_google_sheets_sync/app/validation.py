from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RowError:
    row_number: int
    message: str


def validate_row(row: dict[str, Any], key_column: str, row_number: int) -> RowError | None:
    if not row.get(key_column):
        return RowError(row_number, f"Нет ключа {key_column}")
    return None
