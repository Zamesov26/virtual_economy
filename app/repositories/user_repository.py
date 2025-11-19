from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, with_for_update=False):
        stmt = select(User).where(User.id == user_id)
        if with_for_update:
            stmt.with_for_update()

        return await self.session.scalar(stmt)

    async def get_for_update(self, user_id: int):
        stmt = select(User).where(User.id == user_id).with_for_update()
        return await self.session.scalar(stmt)
