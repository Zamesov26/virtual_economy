import json

from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventar import (
    InventoryConsumableItem,
    InventoryPermanentsItem,
    InventorySchema,
)


class InventoryService:
    CACHE_EX = 60 * 60 * 5

    def __init__(self, session, redis):
        self.session = session
        self.inventory_repo = InventoryRepository(session)
        self.redis = redis

    async def get_inventory(self, user_id: int) -> InventorySchema:
        cache_key = f"user:{user_id}:inventory"

        cached = await self.redis.get(cache_key)
        if cached:
            return InventorySchema.model_validate(json.loads(cached))

        inventory = await self.inventory_repo.get_by_user(user_id)

        consumables = []
        permanents = []

        for item in inventory:
            product = item.product

            if product.type == "consumable":
                consumables.append(item)
            else:
                permanents.append(item)

        dto = InventorySchema(
            consumables=consumables,
            permanents=permanents,
        )

        await self.redis.set(
            cache_key,
            dto.model_dump_json(),
            ex=self.CACHE_EX,
        )

        return dto
