from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.schemas.inventar import InventorySchema
from app.services.inventory_service import InventoryService

router = APIRouter(tags=["Users"])


@router.get("/users/{user_id}/inventory", response_model=InventorySchema)
async def get_inventory(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = InventoryService(session, redis)
    return await service.get_inventory(user_id)
