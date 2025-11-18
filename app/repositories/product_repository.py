from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, product_id: int):
        return await self.session.get(Product, product_id)
