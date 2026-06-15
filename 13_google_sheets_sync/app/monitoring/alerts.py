import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def sync_failed(self, task_name: str, message: str) -> None:
        logger.error("sync failed", extra={"task": task_name, "message": message})
        if not self.settings.alert_telegram_token or not self.settings.alert_telegram_chat_id:
            return
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.telegram.org/bot{self.settings.alert_telegram_token}/sendMessage",
                json={"chat_id": self.settings.alert_telegram_chat_id, "text": f"Сбой синхронизации {task_name}: {message}"},
            )
