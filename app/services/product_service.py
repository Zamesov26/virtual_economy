from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product import ProductType
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
            product = await self.product_repo.get(product_id)
            if not product:
                raise HTTPException(404, "Product not found")

            if product.type != ProductType.CONSUMABLE:
                raise HTTPException(400, "Product is not consumable")

            item = await self.inventory_repo.get_consumable_for_update(
                user_id, product_id
            )

            if not item:
                raise HTTPException(400, "User does not have this item")

            if item.quantity <= 0:
                raise HTTPException(400, "Item quantity is zero")

            item.quantity -= 1

            if item.quantity == 0:
                await self.session.delete(item)
            else:
                await self.inventory_repo.save(item)

        await self.redis.delete(f"user:{user_id}:inventory")

        return {"product_id": product_id, "remaining": max(item.quantity, 0)}
