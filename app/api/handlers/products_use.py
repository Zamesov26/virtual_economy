from fastapi import Depends, Query, APIRouter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.services.product_service import ProductUseService


router = APIRouter(tags=["Products"])

@router.post("/products/{product_id}/use")
async def use_consumable(
    product_id: int,
    user_id: int = Query(...),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = ProductUseService(session, redis)
    result = await service.use_product(user_id, product_id)
    return result
