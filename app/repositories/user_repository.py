from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, with_for_update=False):
        stmt = select(User).where(User.id == user_id)
        if with_for_update:
            stmt = stmt.with_for_update()

        return await self.session.scalar(stmt)

    # TODO подумать может обьединить с get через параметр
    async def get_by_email(self, email: str, with_for_update=False):
        stmt = select(User).where(User.email == email.lower())
        if with_for_update:
            stmt = stmt.with_for_update()

        return await self.session.scalar(stmt)

    # TODO подумать может обьединить с get через параметр
    async def get_by_username(self, username: str, with_for_update=False):
        stmt = select(User).where(User.username == username.lower())
        if with_for_update:
            stmt = stmt.with_for_update()

        return await self.session.scalar(stmt)

    async def create(self, username: str, email: str, password_hash: str):
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            balance=0,
        )
        self.session.add(user)
        return user
