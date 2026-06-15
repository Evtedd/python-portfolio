from app.config import Settings
from app.publishers.instagram import InstagramPublisher
from app.schemas import PostContent, PublishRequest


async def test_instagram_dry_run_returns_external_id() -> None:
    publisher = InstagramPublisher(Settings(dry_run=True))
    request = PublishRequest(
        product_id="sku1",
        platform="instagram",
        content=PostContent(caption="A", hashtags=[], image_urls=["https://cdn.example/a.jpg"], product_url="https://shop.example/a"),
    )

    result = await publisher.publish(request)

    assert result.dry_run is True
    assert result.external_id == "dry-sku1"
