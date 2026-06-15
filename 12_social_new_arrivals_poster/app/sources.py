from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ProductArrivalIn


class DatabaseArrivalSource:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def unpublished(self) -> list[ProductArrivalIn]:
        result = await self.session.execute(text("select * from product_feed where is_new = true"))
        products: list[ProductArrivalIn] = []
        for row in result:
            data = dict(row._mapping)
            products.append(ProductArrivalIn.model_validate(data))
        return products
