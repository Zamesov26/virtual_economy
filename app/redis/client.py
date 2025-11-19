from typing import TYPE_CHECKING

from redis.asyncio import Redis

if TYPE_CHECKING:
    from app.redis.settings import RedisSettings


async def create_redis(settings: "RedisSettings") -> Redis:
    return Redis.from_url(
        settings.url,
        decode_responses=settings.decode_responses,
    )


async def close_redis(redis: Redis):
    if redis:
        await redis.close()
