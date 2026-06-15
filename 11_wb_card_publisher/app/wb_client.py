import asyncio
import logging
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.config import Settings

logger = logging.getLogger(__name__)


class WBCharacteristic(BaseModel):
    id: int
    name: str
    value: str | int | float | list[str]


class WBSize(BaseModel):
    tech_size: str = Field(alias="techSize")
    wb_size: str = Field(default="", alias="wbSize")
    price: int
    skus: list[str]


class WBProductCard(BaseModel):
    vendor_code: str = Field(alias="vendorCode")
    subject_id: int = Field(alias="subjectID")
    subject_name: str = Field(alias="subjectName")
    brand: str
    title: str
    description: str
    dimensions: dict[str, int] = Field(default_factory=lambda: {"length": 1, "width": 1, "height": 1})
    characteristics: list[WBCharacteristic]
    sizes: list[WBSize]
    media_urls: list[str] = Field(default_factory=list)


class WBBatchResult(BaseModel):
    task_id: str
    accepted: int
    errors: list[str] = Field(default_factory=list)


class WBTaskStatus(BaseModel):
    task_id: str
    status: str
    errors: list[str] = Field(default_factory=list)


class WBClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._client = client or httpx.AsyncClient(
            base_url=settings.wb_base_url,
            timeout=settings.request_timeout,
            headers={"Authorization": settings.wb_api_key} if settings.wb_api_key else {},
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def create_cards(self, cards: list[WBProductCard]) -> WBBatchResult:
        if self.settings.sandbox or not self.settings.wb_api_key:
            return WBBatchResult(task_id="sandbox-task", accepted=len(cards))
        payload = [card.model_dump(by_alias=True, exclude={"media_urls"}) for card in cards]
        data = await self._request("POST", "/content/v2/cards/upload", json=payload)
        return self._parse_batch_response(data, len(cards))

    async def upload_media(self, vendor_code: str, media_urls: list[str]) -> None:
        if not media_urls or self.settings.sandbox or not self.settings.wb_api_key:
            return
        await self._request(
            "POST",
            "/content/v2/media/save",
            json={"vendorCode": vendor_code, "data": media_urls},
        )

    async def task_status(self, task_id: str) -> WBTaskStatus:
        if self.settings.sandbox or not self.settings.wb_api_key:
            return WBTaskStatus(task_id=task_id, status="done")
        data = await self._request("GET", "/content/v2/cards/upload/status", params={"taskId": task_id})
        errors = self._extract_errors(data)
        status = str(data.get("data", {}).get("status", "unknown"))
        return WBTaskStatus(task_id=task_id, status=status, errors=errors)

    async def subject_characteristics(self, subject_id: int) -> list[dict[str, Any]]:
        if self.settings.sandbox or not self.settings.wb_api_key:
            return [{"id": 14177449, "name": "Цвет", "required": True}]
        data = await self._request("GET", "/content/v2/object/charcs", params={"subjectId": subject_id})
        return list(data.get("data", []))

    async def colors(self) -> list[dict[str, Any]]:
        if self.settings.sandbox or not self.settings.wb_api_key:
            return [{"name": "черный"}, {"name": "белый"}]
        data = await self._request("GET", "/content/v2/directory/colors")
        return list(data.get("data", []))

    async def countries(self) -> list[dict[str, Any]]:
        if self.settings.sandbox or not self.settings.wb_api_key:
            return [{"name": "Россия"}]
        data = await self._request("GET", "/content/v2/directory/countries")
        return list(data.get("data", []))

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await self._client.request(method, url, **kwargs)
                if response.status_code == 429:
                    await asyncio.sleep(1 + attempt * 2)
                    continue
                response.raise_for_status()
                data = response.json()
                if data.get("error"):
                    raise httpx.HTTPStatusError(str(data), request=response.request, response=response)
                return data
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                logger.warning("WB request failed", extra={"url": url, "attempt": attempt + 1})
                await asyncio.sleep(0.5 + attempt)
        raise RuntimeError(f"WB API request failed: {last_error}") from last_error

    @staticmethod
    def _parse_batch_response(data: dict[str, Any], fallback_count: int) -> WBBatchResult:
        payload = data.get("data") or data
        task_id = str(payload.get("taskId") or payload.get("id") or "")
        errors = WBClient._extract_errors(data)
        return WBBatchResult(task_id=task_id, accepted=0 if errors else fallback_count, errors=errors)

    @staticmethod
    def _extract_errors(data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for item in data.get("errors") or []:
            if isinstance(item, dict):
                errors.append(str(item.get("message") or item))
            else:
                errors.append(str(item))
        if data.get("errorText"):
            errors.append(str(data["errorText"]))
        return errors
