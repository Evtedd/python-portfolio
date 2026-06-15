from app.mapping import product_to_card
from app.sources import RawProduct


def test_product_maps_to_wb_card() -> None:
    product = RawProduct(
        vendor_code="SKU1",
        subject_id=123,
        subject_name="Футболка",
        brand="North",
        title="Футболка базовая",
        name="Футболка",
        description="Хлопок",
        price=1200,
        color="черный",
        barcode="4600000000012",
        size="M",
    )

    card = product_to_card(product)

    assert card.vendor_code == "SKU1"
    assert card.subject_id == 123
    assert card.sizes[0].price == 1200
    assert any(item.name == "Цвет" and item.value == "черный" for item in card.characteristics)
