from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryConsumableItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int


class InventoryPermanentsItem(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        ser_json_encoders={
            datetime: lambda dt: dt.isoformat(),
        },
    )

    product_id: int
    purchased_at: datetime


class InventorySchema(BaseModel):
    consumables: list[InventoryConsumableItem]
    permanents: list[InventoryPermanentsItem]
