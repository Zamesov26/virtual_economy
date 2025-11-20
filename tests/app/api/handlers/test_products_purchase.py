import json

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Inventory, Product, User
from app.database.models.product import ProductType


@pytest.mark.anyio
class TestPurchaseConsumable:
    async def _create_user(self, session, name="u", balance=0):
        user = User(username=name, email=f"{name}@test.com", balance=balance)
        session.add(user)
        return user

    async def _create_product(
        self,
        session,
        name="p",
        id_: int | None = None,
        price=100,
        type_: ProductType = ProductType.CONSUMABLE,
        is_acitve=True,
    ):
        data = {
            "name": name,
        }
        if id_:
            data["id"] = id_
        product = Product(**data, price=price, type=type_, is_active=is_acitve)
        session.add(product)
        return product

    async def _add_inventory(self, session: AsyncSession, user_id, product_id, qty=1):
        item = Inventory(
            user_id=user_id,
            product_id=product_id,
            quantity=qty,
        )
        session.add(item)
        return item

    async def test_purchase_consumable(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, "alex", balance=500)
            product = await self._create_product(
                session, "Boost", id_=1, price=100, type_=ProductType.CONSUMABLE
            )
            await session.commit()

        response = await client.post(
            f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
        )
        assert response.status_code == 200

        async with session_maker() as session:
            items = list(
                await session.scalars(
                    select(Inventory).where(Inventory.user_id == user.id)
                )
            )
            assert len(items) == 1

            user_db = await session.get(User, user.id)
            assert user_db.balance == 400

        key = f"user:{user.id}:inventory"
        radis_cache = await redis_mock.get(key)
        assert json.loads(radis_cache) == {
            "consumables": [{"product_id": product.id, "quantity": 1}],
            "permanents": [],
        }

    @freeze_time("2025-11-18T17:08:30.016582+00:00")
    async def test_purchase_permanent(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, "tom", balance=1000)
            product = await self._create_product(
                session, "Premium", price=500, type_=ProductType.PERMANENT
            )
            await session.commit()

        response = await client.post(
            f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
        )
        assert response.status_code == 200

        async with session_maker() as session:
            items = list(
                await session.scalars(
                    select(Inventory).where(Inventory.user_id == user.id)
                )
            )
            assert len(items) == 1
            user_db = await session.get(User, user.id)
            assert user_db.balance == 500

        key = f"user:{user.id}:inventory"
        radis_cache = await redis_mock.get(key)
        assert json.loads(radis_cache) == {
            "consumables": [],
            "permanents": [
                {
                    "product_id": product.id,
                    "purchased_at": "2025-11-18T17:08:30.016582Z",
                }
            ],
        }

    async def test_conflict_when_not_enough_balance(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, "low", balance=50)
            product = await self._create_product(
                session, "Boost", price=100, type_=ProductType.CONSUMABLE
            )
            await session.commit()

        response = await client.post(
            f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Not enough funds"

    async def test_conflict_when_permanent_product_already_exists(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, "kate", balance=1000)
            product = await self._create_product(
                session, "VIP", price=200, type_=ProductType.PERMANENT
            )
            await session.flush()

            await self._add_inventory(
                session, user_id=user.id, product_id=product.id
            )
            await session.commit()

        response = await client.post(
            f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Permanent product already owned"

    async def test_not_found_when_user_not_exists(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            product = await self._create_product(session, "Boost")
            await session.commit()

        response = await client.post(
            f"api/v1/products/{product.id}/purchase", params={"user_id": 999}
        )

        assert response.status_code == 404

    async def test_not_found_when_product_not_exists(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, "max", balance=500)
            session.add(user)
            await session.commit()

        response = await client.post(
            "api/v1/products/777/purchase", params={"user_id": user.id}
        )

        assert response.status_code == 404
