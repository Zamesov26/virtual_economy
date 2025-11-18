import json
from backend.repositories.inventory_repository import InventoryRepository
from backend.dto.inventory_dto import InventoryItemDTO, InventoryResponseDTO


class InventoryService:
    CACHE_EX = 30  # 30 sec cache for example

    def __init__(self, session, redis):
        self.session = session
        self.inventory_repo = InventoryRepository(session)
        self.redis = redis

    async def get_inventory(self, user_id: int) -> InventoryResponseDTO:
        cache_key = f"user:{user_id}:inventory"

        # 1) Попытка получить из кэша
        cached = await self.redis.get(cache_key)
        if cached:
            return InventoryResponseDTO.model_validate(json.loads(cached))

        # 2) Забираем из БД
        inventory = await self.inventory_repo.get_by_user(user_id)

        consumables_map = {}
        non_consumables = []

        for item in inventory:
            product = item.product

            if product.type == "consumable":
                # группировка qty
                if product.id not in consumables_map:
                    consumables_map[product.id] = InventoryItemDTO(
                        product_id=product.id,
                        quantity=item.quantity,
                        purchased_at=item.purchased_at,
                    )
                else:
                    consumables_map[product.id].quantity += item.quantity
            else:
                # обычные вещи — поштучно
                non_consumables.append(
                    InventoryItemDTO(
                        product_id=product.id,
                        quantity=item.quantity,
                        purchased_at=item.purchased_at,
                    )
                )

        dto = InventoryResponseDTO(
            consumables=list(consumables_map.values()),
            non_consumables=non_consumables,
        )

        # 3) кладём в кэш
        await self.redis.set(
            cache_key,
            dto.model_dump_json(),
            ex=self.CACHE_EX,
        )

        return dto