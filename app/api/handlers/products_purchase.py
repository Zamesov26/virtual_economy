from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.services.purchase_service import PurchaseService

router = APIRouter(tags=["Products"])


@router.post("/products/{product_id}/purchase")
async def purchase(
    product_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = PurchaseService(session, redis)
    result = await service.purchase(user_id, product_id)
    return result
