import pytest

from app.redis.deps import get_redis


@pytest.fixture
async def redis_mock():
    """Фейковый Redis для тестов."""

    class FakeRedis:
        def __init__(self):
            self.storage = {}

        async def set(self, key, value, ex=None):
            self.storage[key] = value

        async def get(self, key):
            return self.storage.get(key)

        async def delete(self, key):
            self.storage.pop(key, None)

    return FakeRedis()


@pytest.fixture
def override_redis(redis_mock):
    """Подменяем Depends(get_redis)."""
    from app.main import app

    app.dependency_overrides[get_redis] = lambda: redis_mock
    yield
    app.dependency_overrides.pop(get_redis, None)
