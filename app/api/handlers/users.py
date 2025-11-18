from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel, Field, ConfigDict
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.schemas.inventar import InventorySchema
from app.services.inventory_service import InventoryService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


class AddFundsDTO(BaseModel):
    amount: int = Field(..., gt=0, le=10_000)


class UserBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int = Field(validation_alias="id")
    new_balance: int = Field(validation_alias="balance")


@router.post("/{user_id}/add-funds", response_model=UserBalanceResponse)
async def add_funds(
    user_id: int,
    data: AddFundsDTO,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = UserService(session, redis)

    user = await service.add_funds(
        user_id=user_id,
        amount=data.amount,
        idem_key=idempotency_key,
    )

    res = UserBalanceResponse.model_validate(user).model_dump()
    return res


@router.get("/{user_id}/inventory", response_model=InventorySchema)
async def get_inventory(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    service = InventoryService(session, redis)
    return await service.get_inventory(user_id)
