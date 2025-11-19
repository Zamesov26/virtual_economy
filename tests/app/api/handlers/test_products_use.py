import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.database.models import Inventory, Product, User
from app.database.models.product import ProductType


@pytest.mark.anyio
class TestUseConsumable:
    async def _create_user(self, session):
        user = User(username="bob", email="bob@test.com", balance=100)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def _create_product(
        self, session, type_: ProductType = ProductType.CONSUMABLE
    ):
        product = Product(
            name="Potion",
            price=10,
            type=type_,
            is_active=True,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    async def _add_inventory(self, session, user_id, product_id, quantity):
        item = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    # -------------------------------------------------------------
    # 1) Успешное использование товара (quantity > 1)
    # -------------------------------------------------------------
    async def test_success(self, client: AsyncClient, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(session, ProductType.CONSUMABLE)
            await self._add_inventory(session, user.id, product.id, quantity=3)

        response = await client.post(
            f"/api/v1/products/{product.id}/use",
            params={"user_id": user.id},
        )
        assert response.status_code == 200
        assert response.json() == {"product_id": product.id, "remaining": 2}

        # verify DB
        async with session_maker() as session:
            item = await session.scalar(
                select(Inventory).where(
                    Inventory.user_id == user.id, Inventory.product_id == product.id
                )
            )
            assert item.quantity == 2

        # cache invalidated
        assert await redis_mock.get(f"user:{user.id}:inventory") is None

    # -------------------------------------------------------------
    # 2) Использование, когда quantity == 1 → запись удаляется
    # -------------------------------------------------------------
    async def test_success_when_use_last_item(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(session)
            await self._add_inventory(session, user.id, product.id, quantity=1)

        response = await client.post(
            f"/api/v1/products/{product.id}/use",
            params={"user_id": user.id},
        )
        assert response.status_code == 200
        assert response.json() == {"product_id": product.id, "remaining": 0}

        async with session_maker() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(Inventory)
                .where(Inventory.user_id == user.id, Inventory.product_id == product.id)
            )
            assert count == 0 or count is None

        assert await redis_mock.get(f"user:{user.id}:inventory") is None

    # -------------------------------------------------------------
    # 3) Использование товара, которого нет у пользователя
    # -------------------------------------------------------------
    async def test_use_missing_item(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(session)

        response = await client.post(
            f"/api/v1/products/{product.id}/use",
            params={"user_id": user.id},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "User does not have this item"

    # -------------------------------------------------------------
    # 4) Попытка использовать товар с quantity == 0
    # -------------------------------------------------------------
    async def test_use_zero_quantity(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(session)
            await self._add_inventory(session, user.id, product.id, quantity=0)

        response = await client.post(
            f"/api/v1/products/{product.id}/use",
            params={"user_id": user.id},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Item quantity is zero"

    # -------------------------------------------------------------
    # 5) Попытка использовать PERMANENT товар (не consumable)
    # -------------------------------------------------------------
    async def test_use_non_consumable(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(session, ProductType.PERMANENT)
            await self._add_inventory(session, user.id, product.id, quantity=1)

        response = await client.post(
            f"/api/v1/products/{product.id}/use",
            params={"user_id": user.id},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Product is not consumable"

    # -------------------------------------------------------------
    # 6) Продукт не найден
    # -------------------------------------------------------------
    async def test_not_found_when_product_not_exists(self, client, redis_mock):
        response = await client.post(
            "/api/v1/products/999/use",
            params={"user_id": 1},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"
