import json

from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    CACHE_KEY = "analytics:popular-products"
    CACHE_EX = 60 * 60

    def __init__(self, session, redis):
        self.session = session
        self.redis = redis
        self.repo = AnalyticsRepository(session)

    async def get_popular(self):
        cached = await self.redis.get(self.CACHE_KEY)
        if cached:
            return json.loads(cached)

        rows = await self.repo.get_popular_products()

        result = [
            {"product_id": product_id, "count": total} for product_id, total in rows
        ]

        await self.redis.set(
            self.CACHE_KEY,
            json.dumps(result),
            ex=self.CACHE_EX,
        )

        return result
