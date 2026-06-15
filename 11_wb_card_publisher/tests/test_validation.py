from app.validation import CardValidator
from app.wb_client import WBCharacteristic, WBProductCard, WBSize


class FakeCatalog:
    async def required_characteristics(self, subject_id: int) -> list[dict]:
        return [{"name": "Цвет", "required": True}]

    async def known_colors(self) -> set[str]:
        return {"черный"}


async def test_validator_accepts_complete_card() -> None:
    card = WBProductCard(
        vendorCode="SKU1",
        subjectID=1,
        subjectName="Футболка",
        brand="Brand",
        title="Brand футболка",
        description="Описание",
        characteristics=[WBCharacteristic(id=1, name="Цвет", value="черный")],
        sizes=[WBSize(techSize="M", price=1000, skus=["123"])],
    )

    issues = await CardValidator(FakeCatalog()).validate(card)

    assert issues == []
