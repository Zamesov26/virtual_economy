from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Inventory


class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self, user_id: int, product_id: int, with_for_update=False
    ) -> Inventory | None:
        stmt = select(Inventory).where(
            Inventory.user_id == user_id, Inventory.product_id == product_id
        )
        if with_for_update:
            stmt = stmt.with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, user_id: int, product_id: int) -> bool:
        stmt = select(
            select(1)
            .where(Inventory.user_id == user_id, Inventory.product_id == product_id)
            .exists()
        )
        return (await self.session.execute(stmt)).scalar()

    async def add(self, user_id: int, product_id: int, quantity: int = 1):
        inv = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        self.session.add(inv)

    async def get_by_user(self, user_id: int) -> list[Inventory]:
        stmt = (
            select(Inventory)
            .where(Inventory.user_id == user_id)
            .options(selectinload(Inventory.product))
        )
        return list(await self.session.scalars(stmt))
