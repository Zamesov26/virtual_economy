import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


@pytest.mark.anyio
class TestAddFunds:
    async def _create_user(self, session: AsyncSession, balance=0):
        user = User(username="test", email="t@test.com", balance=balance)
        session.add(user)
        return user

    async def test_success(self, client: AsyncClient, session_maker, redis_mock):
        async with session_maker() as session:
            user = await self._create_user(session, balance=50)
            await session.commit()

        response = await client.post(
            f"/api/v1/users/{user.id}/add-funds",
            headers={"Idempotency-Key": "key-123"},
            json={"amount": 100},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["new_balance"] == 150

    async def test_unprocessable_entity_missing_idempotency_key(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)

        response = await client.post(
            f"/api/v1/users/{user.id}/add-funds", json={"amount": 100}
        )

        assert response.status_code == 422

    async def test_unprocessable_entity_when_amount_negative(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)

        response = await client.post(
            f"/api/v1/users/{user.id}/add-funds",
            headers={"Idempotency-Key": "key-123"},
            json={"amount": -10},
        )

        assert response.status_code == 422  # validation error DTO

    async def test_unprocessable_entity_when_amount_exceeds_limit(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session)

        response = await client.post(
            f"/api/v1/users/{user.id}/add-funds",
            headers={"Idempotency-Key": "key-123"},
            json={"amount": 999999},
        )

        assert response.status_code == 422  # Pydantic схема отклоняет

    async def test_conflict_when_idempotency_duplicate(
        self, client: AsyncClient, session_maker, redis_mock
    ):
        async with session_maker() as session:
            user = await self._create_user(session, balance=0)
            await session.commit()

        response1 = await client.post(
            f"/api/v1/users/{user.id}/add-funds",
            headers={"Idempotency-Key": "dup-1"},
            json={"amount": 100},
        )
        assert response1.status_code == 200

        response2 = await client.post(
            f"/api/v1/users/{user.id}/add-funds",
            headers={"Idempotency-Key": "dup-1"},
            json={"amount": 100},
        )
        assert response2.status_code == 409
        assert response2.json()["error"]["message"] == "Duplicate top-up request"

    async def test_not_found_when_user_not_exists(
        self, client: AsyncClient, redis_mock
    ):
        response = await client.post(
            "/api/v1/users/999999/add-funds",
            headers={"Idempotency-Key": "key-404"},
            json={"amount": 50},
        )

        assert response.status_code == 404
