from typing import Any

from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product import ProductType
from app.database.models.transaction import Transaction, TransactionStatus
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.inventory_service import InventoryService


class PurchaseService:
    CACHE_TTL = 300  # 5 минут

    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.redis = redis

        self.user_repo = UserRepository(session)
        self.product_repo = ProductRepository(session)
        self.inventory_repo = InventoryRepository(session)
        self.inventory_service = InventoryService(session, redis)

    async def purchase(self, user_id: int, product_id: int) -> dict[str, Any]:
        """Основная операция покупки товара пользователем."""
        async with self.session.begin():

            user = await self.user_repo.get(user_id, with_for_update=True)
            if not user:
                raise HTTPException(404, "User not found")

            product = await self.product_repo.get(product_id)
            if not product or not product.is_active:
                raise HTTPException(404, "Product not found or inactive")

            if user.balance < product.price:
                raise HTTPException(409, "Not enough funds")

            user.balance -= product.price
            self.session.add(user)

            if product.type == ProductType.CONSUMABLE:
                await self._process_consumable(user_id, product_id)

            elif product.type == ProductType.PERMANENT:
                await self._process_permanent(user_id, product_id)

            txn = Transaction(
                user_id=user_id,
                product_id=product_id,
                amount=product.price,
                status=TransactionStatus.PENDING,
            )
            self.session.add(txn)

            txn.status = TransactionStatus.COMPLETED

            await self.session.flush()
            await self.inventory_service.get_inventory(user_id)
            await self.session.commit()

        return {
            "status": "ok",
            "user_id": user_id,
            "product_id": product_id,
            "amount_spent": product.price,
        }

    async def _process_consumable(self, user_id: int, product_id: int):
        """Увеличивает quantity consumable товара."""
        inv = await self.inventory_repo.get(user_id, product_id, with_for_update=True)

        if inv:
            inv.quantity += 1
        else:
            await self.inventory_repo.add(user_id, product_id, quantity=1)

    async def _process_permanent(self, user_id: int, product_id: int):
        """Проверяет и добавляет permanent товар."""
        exists = await self.inventory_repo.exists(user_id, product_id)
        if exists:
            raise HTTPException(409, "Permanent product already owned")

        await self.inventory_repo.add(user_id, product_id, quantity=1)

    @staticmethod
    def _inventory_cache_key(user_id: int) -> str:
        return f"user:{user_id}:inventory"
