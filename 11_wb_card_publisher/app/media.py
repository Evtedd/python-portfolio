from app.wb_client import WBClient, WBProductCard


class MediaService:
    def __init__(self, wb_client: WBClient) -> None:
        self.wb_client = wb_client

    async def upload_for_card(self, card: WBProductCard) -> None:
        await self.wb_client.upload_media(card.vendor_code, card.media_urls)
