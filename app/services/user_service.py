from fastapi import HTTPException
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository


class UserService:
    IDEMPOTENCY_TTL = 60 * 60 * 24

    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.user_repository: UserRepository = UserRepository(session=session)
        self.redis = redis

    async def add_funds(self, user_id: int, amount: int, idem_key: str):
        if await self.redis.exists(f"idempotency:{idem_key}"):
            raise HTTPException(status_code=409, detail="Duplicate top-up request")

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be > 0")

        async with self.session.begin():
            user = await self.user_repository.get(user_id, with_for_update=True)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.balance += amount
            self.session.add(user)
            await self.session.commit()

        await self.redis.set(f"idempotency:{idem_key}", "1", ex=self.IDEMPOTENCY_TTL)

        return user
