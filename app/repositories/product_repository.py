from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, product_id: int, with_is_active=True):
        stmt = select(Product).where(Product.id == product_id)
        if with_is_active:
            stmt = stmt.where(Product.is_active)

        return await self.session.scalar(stmt)
