from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int):
        return await self.session.get(User, user_id)

    async def get_for_update(self, user_id: int):
        stmt = select(User).where(User.id == user_id).with_for_update()
        return await self.session.scalar(stmt)
