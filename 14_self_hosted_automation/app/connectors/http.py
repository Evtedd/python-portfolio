from typing import Any

import httpx

from app.connectors.base import Connector


class HttpConnector(Connector):
    name = "http"

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        method = str(settings.get("method", "POST")).upper()
        url = str(settings["url"])
        timeout = float(settings.get("timeout", 20))
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, json=payload, headers=settings.get("headers") or {})
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            body: Any = response.json() if "json" in content_type else response.text
            return {"status_code": response.status_code, "body": body}


class TelegramConnector(Connector):
    name = "telegram"

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        token = str(settings["token"])
        chat_id = str(settings["chat_id"])
        text = str(payload.get("text") or payload.get("message") or "")
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text},
            )
            response.raise_for_status()
            return {"message_id": response.json()["result"]["message_id"]}
