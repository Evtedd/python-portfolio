import httpx

from app.config import Settings
from app.publishers.base import Publisher
from app.schemas import PublishRequest, PublishResult


class PinterestPublisher(Publisher):
    platform = "pinterest"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(
            base_url="https://api.pinterest.com/v5",
            timeout=settings.request_timeout,
            headers={"Authorization": f"Bearer {settings.pinterest_access_token}"} if settings.pinterest_access_token else {},
        )

    async def publish(self, request: PublishRequest) -> PublishResult:
        if self.settings.dry_run or not self.settings.pinterest_access_token:
            return PublishResult(platform=self.platform, external_id=f"dry-{request.product_id}", dry_run=True)
        if not request.content.image_urls:
            raise ValueError("Pinterest pin needs an image")
        response = await self.client.post(
            "/pins",
            json={
                "board_id": self.settings.pinterest_board_id,
                "title": request.content.caption.splitlines()[0][:100],
                "description": request.content.caption,
                "link": request.content.product_url,
                "media_source": {
                    "source_type": "image_url",
                    "url": request.content.image_urls[0],
                },
            },
        )
        response.raise_for_status()
        return PublishResult(platform=self.platform, external_id=str(response.json()["id"]))
