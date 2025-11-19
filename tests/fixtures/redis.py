import time

import pytest

from app.redis.deps import get_redis


class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.expire_times = {}

    def _cleanup_expired(self, key: str):
        """Удаляет ключ, если TTL вышел."""
        if key in self.expire_times:
            if time.time() >= self.expire_times[key]:
                self.storage.pop(key, None)
                self.expire_times.pop(key, None)

    async def incr(self, key: str):
        self._cleanup_expired(key)

        value = self.storage.get(key)
        if value is None:
            self.storage[key] = 1
        else:
            self.storage[key] = value + 1

        return self.storage[key]

    async def expire(self, key: str, seconds: int):
        self._cleanup_expired(key)
        if key in self.storage:
            self.expire_times[key] = time.time() + seconds
            return True
        return False

    async def get(self, key: str):
        self._cleanup_expired(key)
        return self.storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.storage[key] = value
        if ex:
            self.expire_times[key] = time.time() + ex

    async def delete(self, *keys):
        for key in keys:
            self.storage.pop(key, None)
            self.expire_times.pop(key, None)

    async def exists(self, key: str):
        self._cleanup_expired(key)
        return 1 if key in self.storage else 0

    async def scan(self, cursor=0, match="*", count=10):
        import fnmatch

        keys = [k for k in self.storage.keys() if fnmatch.fnmatch(k, match)]
        return 0, keys


@pytest.fixture
async def redis_mock():
    """Фейковый Redis для тестов."""
    fake = FakeRedis()

    from app.main import app

    app.dependency_overrides[get_redis] = lambda: fake

    yield fake

    app.dependency_overrides.pop(get_redis, None)
