from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product import ProductType
from app.exceptions.inventory import InventoryNotFoundError, InventoryEmptyError
from app.exceptions.product import (
    ProductNotConsumableError,
    ProductNotFoundError,
)
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository


class ProductUseService:
    def __init__(self, session: AsyncSession, redis):
        self.session = session
        self.redis = redis
        self.inventory_repo = InventoryRepository(session)
        self.product_repo = ProductRepository(session)

    async def use_product(self, user_id: int, product_id: int):
        async with self.session.begin():
            # может быть так, что товар не доступен, но есть в инвентаре
            product = await self.product_repo.get(product_id, with_is_active=False)
            if not product:
                raise ProductNotFoundError()

            if product.type != ProductType.CONSUMABLE:
                raise ProductNotConsumableError()

            item = await self.inventory_repo.get(
                user_id, product_id, with_for_update=True
            )

            if not item:
                raise InventoryNotFoundError()

            if item.quantity <= 0:
                raise InventoryEmptyError()

            item.quantity -= 1

            if item.quantity == 0:
                await self.session.delete(item)
            else:
                self.session.add(item)
            await self.session.commit()

        await self.redis.delete(f"user:{user_id}:inventory")

        return {"product_id": product_id, "remaining": max(item.quantity, 0)}
