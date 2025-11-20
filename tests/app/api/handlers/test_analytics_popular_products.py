import json
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete

from app.database.models import Product, TransactionStatus, User
from app.database.models.transaction import Transaction


@pytest.mark.anyio
class TestPopularProducts:
    async def _create_user(self, session, name="u"):
        user = User(username=name, email=f"{name}@test.com", balance=0)
        session.add(user)
        return user

    async def _create_product(self, session, name="p", id_: int | None = None):
        data = {
            "name": name,
        }
        if id_:
            data["id"] = id_
        product = Product(**data, price=10, type="consumable", is_active=True)
        session.add(product)
        return product

    async def _create_transaction(
        self,
        session,
        user_id,
        product_id,
        days_ago=0,
        status: TransactionStatus = TransactionStatus.COMPLETED,
    ):
        created = datetime.now(UTC) - timedelta(days=days_ago)
        txn = Transaction(
            user_id=user_id,
            product_id=product_id,
            amount=1,
            status=status,
            created_at=created,
        )
        session.add(txn)
        return txn

    async def test_success(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            p1 = await self._create_product(session, "A")
            p2 = await self._create_product(session, "B")

            await session.flush()
            await self._create_transaction(session, user.id, p1.id)
            await self._create_transaction(session, user.id, p1.id)
            await self._create_transaction(session, user.id, p1.id)

            await self._create_transaction(session, user.id, p2.id)
            await session.commit()

        response = await client.get("/api/v1/analytics/popular-products")
        assert response.status_code == 200

        data = response.json()
        assert data == [
            {"product_id": p1.id, "count": 3},
            {"product_id": p2.id, "count": 1},
        ]

    async def test_success_without_old_transactions(
        self, client, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)
            p1 = await self._create_product(session)
            await session.flush()

            await self._create_transaction(session, user.id, p1.id, days_ago=10)
            await self._create_transaction(session, user.id, p1.id, days_ago=1)
            await session.commit()

        response = await client.get("/api/v1/analytics/popular-products")
        assert response.status_code == 200

        assert response.json() == [{"product_id": p1.id, "count": 1}]

    async def test_success_only_completed_transactions(
        self, client, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)
            p = await self._create_product(session)
            await session.flush()

            await self._create_transaction(
                session, user.id, p.id, status=TransactionStatus.FAILED
            )
            await self._create_transaction(
                session, user.id, p.id, status=TransactionStatus.PENDING
            )
            await self._create_transaction(
                session, user.id, p.id, status=TransactionStatus.COMPLETED
            )
            await session.commit()

        response = await client.get("/api/v1/analytics/popular-products")
        assert response.status_code == 200

        assert response.json() == [{"product_id": p.id, "count": 1}]

    async def test_success_top_5_only(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            await session.flush()

            product_transaction = (
                (1, 1),
                (2, 5),
                (3, 12),
                (4, 6),
                (5, 7),
                (6, 8),
                (7, 11),
            )

            for idx, t_count in product_transaction:
                product = await self._create_product(session, name=f"P{idx}", id_=idx)
                for _ in range(t_count):
                    await self._create_transaction(session, user.id, product.id)
            await session.commit()

        response = await client.get("/api/v1/analytics/popular-products")
        assert response.status_code == 200

        data = response.json()

        assert data == [
            {"product_id": 3, "count": 12},
            {"product_id": 7, "count": 11},
            {"product_id": 6, "count": 8},
            {"product_id": 5, "count": 7},
            {"product_id": 4, "count": 6},
        ]

    async def test_success_cache(self, client, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session)
            p = await self._create_product(session)
            await session.flush()

            await self._create_transaction(session, user.id, p.id)
            await session.commit()

        r1 = await client.get("/api/v1/analytics/popular-products")
        assert r1.status_code == 200
        expected = r1.json()

        async with session_maker() as session:
            await session.execute(delete(Transaction))
            await session.commit()

        r2 = await client.get("/api/v1/analytics/popular-products")
        assert r2.status_code == 200
        assert r2.json() == expected

        cache = await redis_mock.get("analytics:popular-products")
        assert json.loads(cache) == [{"product_id": p.id, "count": 1}]
