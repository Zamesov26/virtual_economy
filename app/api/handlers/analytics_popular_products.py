from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/popular-products")
async def get_popular_products(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = AnalyticsService(session, redis)
    return await service.get_popular()
