from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Inventory


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, product_id: int) -> Inventory | None:
        result = await self.session.execute(
            select(Inventory).where(
                Inventory.user_id == user_id,
                Inventory.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def exists(self, user_id: int, product_id: int) -> bool:
        return (await self.get(user_id, product_id)) is not None

    async def add(self, user_id: int, product_id: int, quantity: int = 1):
        inv = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        self.session.add(inv)

    async def list_for_user(self, user_id: int) -> list[Inventory]:
        result = await self.session.execute(
            select(Inventory).where(Inventory.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[Inventory]:
        stmt = (
            select(Inventory)
            .where(Inventory.user_id == user_id)
            .options(selectinload(Inventory.product))
        )
        return list(await self.session.scalars(stmt))
