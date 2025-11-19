import json

import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy import select

from app.database.models import Inventory, Product, User
from app.database.models.product import ProductType


@pytest.mark.anyio
async def test_purchase_consumable(client: AsyncClient, session_maker, redis_mock):
    async with session_maker() as session:
        user = User(username="alex", email="alex@test.com", balance=500)
        product = Product(
            id=1, name="Boost", price=100, type=ProductType.CONSUMABLE, is_active=True
        )
        session.add_all([user, product])
        await session.commit()
        await session.refresh(user)
        await session.refresh(product)

    response = await client.post(
        f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
    )
    assert response.status_code == 200

    async with session_maker() as session:
        items = list(
            await session.scalars(select(Inventory).where(Inventory.user_id == user.id))
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
@pytest.mark.anyio
async def test_purchase_permanent(client: AsyncClient, session_maker, redis_mock):
    async with session_maker() as session:
        user = User(username="tom", email="tom@test.com", balance=1000)
        product = Product(
            name="Premium", price=500, type=ProductType.PERMANENT, is_active=True
        )
        session.add_all([user, product])
        await session.commit()
        await session.refresh(user)
        await session.refresh(product)

    response = await client.post(
        f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
    )
    assert response.status_code == 200

    async with session_maker() as session:
        items = list(
            await session.scalars(select(Inventory).where(Inventory.user_id == user.id))
        )
        assert len(items) == 1
        user_db = await session.get(User, user.id)
        assert user_db.balance == 500

    key = f"user:{user.id}:inventory"
    radis_cache = await redis_mock.get(key)
    assert json.loads(radis_cache) == {
        "consumables": [],
        "permanents": [
            {"product_id": product.id, "purchased_at": "2025-11-18T17:08:30.016582Z"}
        ],
    }


@pytest.mark.anyio
async def test_conflict_when_not_enough_balance(
    client: AsyncClient, session_maker, redis_mock
):
    async with session_maker() as session:
        user = User(username="low", email="low@test.com", balance=50)
        product = Product(
            name="Boost", price=100, type=ProductType.CONSUMABLE, is_active=True
        )
        session.add_all([user, product])
        await session.commit()
        await session.refresh(user)
        await session.refresh(product)

    response = await client.post(
        f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Not enough funds"


@pytest.mark.anyio
async def test_conflict_when_permanent_product_already_exists(
    client: AsyncClient, session_maker, redis_mock
):
    async with session_maker() as session:
        user = User(username="kate", email="kate@test.com", balance=1000)
        product = Product(
            name="VIP", price=200, type=ProductType.PERMANENT, is_active=True
        )
        session.add_all([user, product])
        await session.commit()
        await session.refresh(user)
        await session.refresh(product)

        inv = Inventory(user_id=user.id, product_id=product.id, quantity=1)
        session.add(inv)
        await session.commit()

    response = await client.post(
        f"api/v1/products/{product.id}/purchase", params={"user_id": user.id}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Permanent product already owned"


@pytest.mark.anyio
async def test_not_found_when_user_not_exists(
    client: AsyncClient, session_maker, redis_mock
):
    async with session_maker() as session:
        product = Product(
            name="Boost", price=100, type=ProductType.CONSUMABLE, is_active=True
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)

    response = await client.post(
        f"api/v1/products/{product.id}/purchase", params={"user_id": 999}
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_not_found_when_product_not_exists(
    client: AsyncClient, session_maker, redis_mock
):
    async with session_maker() as session:
        user = User(username="max", email="max@test.com", balance=500)
        session.add(user)
        await session.commit()

    response = await client.post(
        "api/v1/products/777/purchase", params={"user_id": user.id}
    )

    assert response.status_code == 404
