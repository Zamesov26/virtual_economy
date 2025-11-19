from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis

from app.redis.deps import get_redis


def simple_rate_limit(limit: int, window: int):
    async def dependency(
        request: Request,
        redis: Redis = Depends(get_redis),
    ):
        ip = request.client.host
        path = request.url.path

        key = f"rl:{ip}:{path}"

        current = await redis.incr(key)

        if current == 1:
            await redis.expire(key, window)

        if current > limit:
            raise HTTPException(
                429, f"Rate limit exceeded: max {limit} requests per {window} seconds"
            )

    return dependency
