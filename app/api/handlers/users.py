from datetime import datetime

from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel, Field, ConfigDict
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.deps import get_session
from app.redis.deps import get_redis
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


class AddFundsDTO(BaseModel):
    amount: int = Field(..., gt=0, le=10_000)
    
class UserBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True )

    user_id: int = Field(validation_alias="id")
    new_balance: int = Field(validation_alias="balance")
   
   
class InventoryItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    purchased_at: datetime


class InventoryResponseDTO(BaseModel):
    consumables: list[InventoryItemDTO]
    non_consumables: list[InventoryItemDTO]


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