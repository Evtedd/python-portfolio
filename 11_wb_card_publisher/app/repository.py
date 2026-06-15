from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProductCardRecord
from app.wb_client import WBProductCard


class ProductCardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def existing_vendor_codes(self, vendor_codes: list[str]) -> set[str]:
        if not vendor_codes:
            return set()
        result = await self.session.execute(
            select(ProductCardRecord.vendor_code).where(ProductCardRecord.vendor_code.in_(vendor_codes))
        )
        return set(result.scalars().all())

    async def save_status(
        self,
        card: WBProductCard,
        status: str,
        task_id: str | None = None,
        error: str | None = None,
    ) -> None:
        payload = card.model_dump(by_alias=True)
        statement = insert(ProductCardRecord).values(
            vendor_code=card.vendor_code,
            status=status,
            task_id=task_id,
            payload=payload,
            error=error,
        )
        statement = statement.on_conflict_do_update(
            index_elements=[ProductCardRecord.vendor_code],
            set_={"status": status, "task_id": task_id, "payload": payload, "error": error},
        )
        await self.session.execute(statement)

    async def commit(self) -> None:
        await self.session.commit()
