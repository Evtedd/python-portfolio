import logging

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog import CatalogService
from app.config import Settings
from app.mapping import product_to_card
from app.media import MediaService
from app.repository import ProductCardRepository
from app.sources import build_source
from app.validation import CardValidator
from app.wb_client import WBClient, WBProductCard

logger = logging.getLogger(__name__)


class PublishReport(BaseModel):
    loaded: int = 0
    skipped_duplicates: int = 0
    valid: int = 0
    sent: int = 0
    dry_run: bool
    task_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class CardPublishingService:
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.settings = settings
        self.session = session
        self.wb_client = WBClient(settings)
        self.repository = ProductCardRepository(session)
        catalog = CatalogService(self.wb_client)
        self.validator = CardValidator(catalog)
        self.media = MediaService(self.wb_client)

    async def run(self) -> PublishReport:
        source = build_source(self.settings, self.session)
        products = await source.fetch()
        report = PublishReport(loaded=len(products), dry_run=self.settings.dry_run)
        cards = [product_to_card(product) for product in products]
        existing = await self.repository.existing_vendor_codes([card.vendor_code for card in cards])
        fresh_cards = [card for card in cards if card.vendor_code not in existing]
        report.skipped_duplicates = len(cards) - len(fresh_cards)
        valid_cards: list[WBProductCard] = []
        for card in fresh_cards:
            issues = await self.validator.validate(card)
            if issues:
                message = "; ".join(f"{issue.field}: {issue.message}" for issue in issues)
                await self.repository.save_status(card, "invalid", error=message)
                report.errors.append(f"{card.vendor_code}: {message}")
                continue
            valid_cards.append(card)
        report.valid = len(valid_cards)
        if self.settings.dry_run:
            for card in valid_cards:
                await self.repository.save_status(card, "dry_run")
            await self.repository.commit()
            return report
        for chunk in _chunks(valid_cards, self.settings.batch_size):
            for card in chunk:
                await self.media.upload_for_card(card)
            result = await self.wb_client.create_cards(chunk)
            report.task_ids.append(result.task_id)
            report.sent += result.accepted
            for card in chunk:
                status = "submitted" if not result.errors else "failed"
                await self.repository.save_status(card, status, task_id=result.task_id, error="; ".join(result.errors))
        await self.repository.commit()
        logger.info("WB card publishing run finished", extra=report.model_dump())
        return report


def _chunks(cards: list[WBProductCard], size: int) -> list[list[WBProductCard]]:
    return [cards[index : index + size] for index in range(0, len(cards), size)]
