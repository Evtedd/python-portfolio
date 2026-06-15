from typing import Any

from app.connectors.base import Connector


class MemoryConnector(Connector):
    name = "memory"

    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        item = {"settings": settings, "payload": payload}
        self.items.append(item)
        return {"ok": True, **payload}


class DbLogConnector(Connector):
    name = "db_log"

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {"saved": True, "message": payload.get("message") or payload}


class EmailConnector(Connector):
    name = "email"

    async def run(self, settings: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        return {"queued": True, "to": settings.get("to"), "subject": payload.get("subject", "")}
