from dataclasses import dataclass

from app.catalog import CatalogService
from app.wb_client import WBProductCard


@dataclass(frozen=True)
class ValidationIssue:
    vendor_code: str
    field: str
    message: str


class CardValidator:
    def __init__(self, catalog: CatalogService) -> None:
        self.catalog = catalog

    async def validate(self, card: WBProductCard) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not card.vendor_code:
            issues.append(self._issue(card, "vendorCode", "Артикул продавца обязателен"))
        if len(card.title) > 60:
            issues.append(self._issue(card, "title", "Название длиннее 60 символов"))
        if len(card.description) > 2000:
            issues.append(self._issue(card, "description", "Описание длиннее 2000 символов"))
        if not card.sizes or not card.sizes[0].skus:
            issues.append(self._issue(card, "sizes", "Нужен хотя бы один баркод"))
        required = await self.catalog.required_characteristics(card.subject_id)
        filled = {item.name.lower() for item in card.characteristics if item.value not in ("", None, [])}
        for characteristic in required:
            name = str(characteristic.get("name", "")).lower()
            if name and name not in filled:
                issues.append(self._issue(card, name, "Не заполнена обязательная характеристика"))
        colors = await self.catalog.known_colors()
        color_values = [str(item.value).lower() for item in card.characteristics if item.name.lower() == "цвет"]
        if color_values and color_values[0] not in colors:
            issues.append(self._issue(card, "color", "Цвет не найден в справочнике WB"))
        return issues

    @staticmethod
    def _issue(card: WBProductCard, field: str, message: str) -> ValidationIssue:
        return ValidationIssue(card.vendor_code, field, message)
