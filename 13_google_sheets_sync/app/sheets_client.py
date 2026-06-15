import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.config import Settings


class SheetsClient(ABC):
    @abstractmethod
    async def read_rows(self, spreadsheet_id: str, range_name: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def write_rows(self, spreadsheet_id: str, range_name: str, rows: list[dict[str, Any]]) -> None:
        ...


class InMemorySheetsClient(SheetsClient):
    def __init__(self, rows_by_range: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.rows_by_range = rows_by_range or {
            "demo:products!A:Z": [{"sku": "SKU1", "name": "Товар", "price": "1200"}]
        }

    async def read_rows(self, spreadsheet_id: str, range_name: str) -> list[dict[str, Any]]:
        return list(self.rows_by_range.get(f"{spreadsheet_id}:{range_name}", []))

    async def write_rows(self, spreadsheet_id: str, range_name: str, rows: list[dict[str, Any]]) -> None:
        self.rows_by_range[f"{spreadsheet_id}:{range_name}"] = list(rows)


class GoogleSheetsClient(SheetsClient):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def read_rows(self, spreadsheet_id: str, range_name: str) -> list[dict[str, Any]]:
        service = self._service()
        response = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = response.get("values", [])
        if not values:
            return []
        headers = [str(value) for value in values[0]]
        return [dict(zip(headers, row)) for row in values[1:]]

    async def write_rows(self, spreadsheet_id: str, range_name: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        headers = list(rows[0].keys())
        values = [headers] + [[row.get(header, "") for header in headers] for row in rows]
        service = self._service()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": values},
        ).execute()

    def _service(self):
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        if self.settings.google_credentials_json:
            info = json.loads(self.settings.google_credentials_json)
            credentials = service_account.Credentials.from_service_account_info(info, scopes=self._scopes())
        else:
            credentials = service_account.Credentials.from_service_account_file(
                str(Path(self.settings.google_credentials_path)),
                scopes=self._scopes(),
            )
        return build("sheets", "v4", credentials=credentials)

    @staticmethod
    def _scopes() -> list[str]:
        return ["https://www.googleapis.com/auth/spreadsheets"]


def build_sheets_client(settings: Settings) -> SheetsClient:
    if settings.google_fake_mode:
        return InMemorySheetsClient()
    return GoogleSheetsClient(settings)
