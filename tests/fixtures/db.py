import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base

# TODO config
TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_wallet_db"
)


@pytest.fixture(scope="session")
async def engine():
    """Создаём движок и структуру таблиц один раз за все тесты."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
def session_maker(engine):
    """Создаём sessionmaker для тестов."""
    return async_sessionmaker(
        engine, expire_on_commit=False, autoflush=False, autocommit=False
    )


@pytest.fixture(autouse=True)
async def clear_db(session_maker):
    async with session_maker() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
