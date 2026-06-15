import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings


class RawProduct(BaseModel):
    vendor_code: str
    subject_id: int
    subject_name: str
    brand: str
    title: str
    name: str
    description: str
    price: int
    color: str
    country: str = "Россия"
    barcode: str
    size: str = "0"
    media_urls: list[str] = Field(default_factory=list)
    extra_characteristics: dict[str, Any] = Field(default_factory=dict)


class ProductSource(ABC):
    @abstractmethod
    async def fetch(self) -> list[RawProduct]:
        ...


class CsvProductSource(ProductSource):
    def __init__(self, path: Path) -> None:
        self.path = path

    async def fetch(self) -> list[RawProduct]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8-sig", newline="") as file:
            rows = []
            for row in csv.DictReader(file):
                rows.append(_row_to_product(row))
            return rows


class DatabaseProductSource(ProductSource):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def fetch(self) -> list[RawProduct]:
        result = await self.session.execute(text("select * from source_products where active = true"))
        return [_row_to_product(dict(row._mapping)) for row in result]


class GoogleSheetsProductSource(ProductSource):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self) -> list[RawProduct]:
        if not self.settings.google_sheet_id or not self.settings.google_credentials_json:
            return []
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials_info = json.loads(self.settings.google_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
        service = build("sheets", "v4", credentials=credentials)
        response = service.spreadsheets().values().get(
            spreadsheetId=self.settings.google_sheet_id,
            range=self.settings.google_range,
        ).execute()
        rows = response.get("values", [])
        if not rows:
            return []
        headers = rows[0]
        return [_row_to_product(dict(zip(headers, values))) for values in rows[1:]]


def build_source(settings: Settings, session: AsyncSession) -> ProductSource:
    if settings.source_type == "db":
        return DatabaseProductSource(session)
    if settings.source_type == "sheets":
        return GoogleSheetsProductSource(settings)
    return CsvProductSource(settings.csv_path)


def _row_to_product(row: dict[str, Any]) -> RawProduct:
    media = row.get("media_urls") or row.get("media") or ""
    media_urls = [part.strip() for part in str(media).split("|") if part.strip()]
    extras_raw = row.get("extra_characteristics") or "{}"
    extras = json.loads(extras_raw) if isinstance(extras_raw, str) and extras_raw.strip().startswith("{") else {}
    return RawProduct(
        vendor_code=str(row["vendor_code"]).strip(),
        subject_id=int(row["subject_id"]),
        subject_name=str(row["subject_name"]).strip(),
        brand=str(row["brand"]).strip(),
        title=str(row.get("title") or row.get("name") or "").strip(),
        name=str(row.get("name") or row.get("title") or "").strip(),
        description=str(row.get("description") or "").strip(),
        price=int(float(row.get("price") or 0)),
        color=str(row.get("color") or "").strip(),
        country=str(row.get("country") or "Россия").strip(),
        barcode=str(row["barcode"]).strip(),
        size=str(row.get("size") or "0").strip(),
        media_urls=media_urls,
        extra_characteristics=extras,
    )
