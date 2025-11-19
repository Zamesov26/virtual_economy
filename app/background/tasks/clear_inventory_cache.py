import logging
import time

import redis

from app.background.celery_app import celery_app
from app.redis.settings import RedisSettings

logger = logging.getLogger(__name__)
redis_settings = RedisSettings()
redis = redis.Redis.from_url(redis_settings.url)


@celery_app.task
def clear_inventory_cache():
    start = time.perf_counter()
    logger.info("🔥 Starting inventory cache cleanup…")

    cursor = 0
    pattern = "user:*:inventory"
    deleted = 0

    while True:
        cursor, keys = redis.scan(cursor=cursor, match=pattern, count=100)

        if keys:
            redis.delete(*keys)
            deleted += len(keys)

        if cursor == 0:
            break

    elapsed = round(time.perf_counter() - start, 3)

    logger.info(
        f"✅ Inventory cache cleanup finished. Deleted={deleted} keys. Took {elapsed}s."
    )

    return {"status": "ok", "deleted": deleted}
