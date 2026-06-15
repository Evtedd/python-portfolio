from app.content import ContentBuilder
from app.schemas import ProductArrivalIn


def test_content_builder_adds_brand_and_tags() -> None:
    product = ProductArrivalIn(
        product_id="sku1",
        name="Рюкзак",
        url="https://shop.example/sku1",
        image_urls=["https://cdn.example/sku1.jpg"],
        brand="North",
        category="Сумки",
        price=5900,
    )

    content = ContentBuilder().build(product)

    assert "North" in content.caption
    assert "#сумки" in content.hashtags
    assert content.image_urls == ["https://cdn.example/sku1.jpg"]
