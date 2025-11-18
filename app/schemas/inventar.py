from pydantic import BaseModel, Field, ConfigDict


class InventoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int = Field(...)
    quantity: int = Field(...)
