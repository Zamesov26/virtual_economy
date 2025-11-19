import json

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Inventory, Product, User
from app.database.models.product import ProductType


@pytest.mark.anyio
class TestUserInventory:

    async def _create_user(self, session: AsyncSession):
        user = User(username="test", email="t@test.com", balance=0)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def _create_product(self, session: AsyncSession, name, price, type):
        product = Product(
            name=name,
            price=price,
            type=type,
            is_active=True,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    async def _add_inventory(self, session: AsyncSession, user_id, product_id, qty=1):
        item = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=qty,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    async def test_inventory_from_db(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)

            p1 = await self._create_product(
                session, "Potion", 10, ProductType.CONSUMABLE
            )
            p2 = await self._create_product(session, "Sword", 20, ProductType.PERMANENT)

            inv1 = await self._add_inventory(session, user.id, p1.id, qty=2)
            inv2 = await self._add_inventory(session, user.id, p2.id, qty=1)

        response = await client.get(f"/api/v1/users/{user.id}/inventory")
        assert response.status_code == 200

        data = response.json()

        # consumables
        assert len(data["consumables"]) == 1
        assert data["consumables"][0]["product_id"] == p1.id
        assert data["consumables"][0]["quantity"] == 2

        # permanents
        assert len(data["permanents"]) == 1
        assert data["permanents"][0]["product_id"] == p2.id
        assert "purchased_at" in data["permanents"][0]

    @freeze_time("2025-11-18T17:08:30.016582+00:00")
    async def test_inventory_from_cache(self, client: AsyncClient, redis_mock):
        user_id = 123

        cached = {
            "consumables": [{"product_id": 10, "quantity": 5}],
            "permanents": [{"product_id": 20, "purchased_at": "2025-01-01T10:00:00"}],
        }

        await redis_mock.set(f"user:{user_id}:inventory", json.dumps(cached))

        response = await client.get(f"/api/v1/users/{user_id}/inventory")
        assert response.status_code == 200
        assert response.json() == cached

    async def test_inventory_cache_write(
        self, client: AsyncClient, session_maker, redis_mock: Redis
    ):
        async with session_maker() as session:
            user = await self._create_user(session)
            product = await self._create_product(
                session, "Potion", 10, ProductType.CONSUMABLE
            )
            await self._add_inventory(session, user.id, product.id, qty=3)

        cache_key = f"user:{user.id}:inventory"
        assert await redis_mock.get(cache_key) is None

        await client.get(f"/api/v1/users/{user.id}/inventory")

        cached_raw = await redis_mock.get(cache_key)
        assert cached_raw is not None

        cached = json.loads(cached_raw)

        assert cached["consumables"][0]["product_id"] == product.id
        assert cached["consumables"][0]["quantity"] == 3

    async def test_inventory_empty(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)

        response = await client.get(f"/api/v1/users/{user.id}/inventory")
        assert response.status_code == 200

        data = response.json()
        assert data["consumables"] == []
        assert data["permanents"] == []

    async def test_inventory_user_not_found(self, client: AsyncClient, redis_mock):
        response = await client.get("/api/v1/users/999999/inventory")

        # Если решишь позже вернуть 404 — можно поменять.
        assert response.status_code == 200
