from fastapi import HTTPException
from passlib.hash import argon2

from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, username: str, email: str, password: str):
        if await self.user_repo.get_by_email(email):
            raise HTTPException(409, "Email already registered")

        if await self.user_repo.get_by_username(username):
            raise HTTPException(409, "Username already taken")

        hashed = argon2.hash(password)

        user = await self.user_repo.create(
            username=username.lower(),
            email=email.lower(),
            password_hash=hashed,
        )
        await self.session.commit()

        return user
