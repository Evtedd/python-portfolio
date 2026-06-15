import httpx

from app.config import Settings
from app.publishers.base import Publisher
from app.schemas import PublishRequest, PublishResult


class InstagramPublisher(Publisher):
    platform = "instagram"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(base_url="https://graph.facebook.com/v20.0", timeout=settings.request_timeout)

    async def publish(self, request: PublishRequest) -> PublishResult:
        if self.settings.dry_run or not self.settings.instagram_access_token:
            return PublishResult(platform=self.platform, external_id=f"dry-{request.product_id}", dry_run=True)
        image_urls = request.content.image_urls
        if not image_urls:
            raise ValueError("Instagram post needs at least one image")
        if len(image_urls) == 1:
            creation_id = await self._create_media_container(image_urls[0], request.content.caption)
        else:
            children = [await self._create_media_container(url, request.content.caption, is_carousel_item=True) for url in image_urls]
            creation_id = await self._create_carousel(children, request.content.caption)
        published_id = await self._publish_container(creation_id)
        return PublishResult(platform=self.platform, external_id=published_id)

    async def _create_media_container(self, image_url: str, caption: str, is_carousel_item: bool = False) -> str:
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.settings.instagram_access_token,
        }
        if is_carousel_item:
            payload["is_carousel_item"] = "true"
        response = await self.client.post(f"/{self.settings.instagram_account_id}/media", data=payload)
        response.raise_for_status()
        return str(response.json()["id"])

    async def _create_carousel(self, children: list[str], caption: str) -> str:
        response = await self.client.post(
            f"/{self.settings.instagram_account_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(children),
                "caption": caption,
                "access_token": self.settings.instagram_access_token,
            },
        )
        response.raise_for_status()
        return str(response.json()["id"])

    async def _publish_container(self, creation_id: str) -> str:
        response = await self.client.post(
            f"/{self.settings.instagram_account_id}/media_publish",
            data={"creation_id": creation_id, "access_token": self.settings.instagram_access_token},
        )
        response.raise_for_status()
        return str(response.json()["id"])
