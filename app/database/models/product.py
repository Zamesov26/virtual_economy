import enum
from typing import TYPE_CHECKING

from sqlalchemy import Text, Integer, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.inventory import Inventory
    from app.database.models.transaction import Transaction


class ProductType(str, enum.Enum):
    CONSUMABLE = "consumable"
    PERMANENT = "permanent"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False)

    type: Mapped[ProductType] = mapped_column(
        SAEnum(
            ProductType,
            name="product_type_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=ProductType.CONSUMABLE,
        server_default="consumable",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    inventory_items: Mapped[list["Inventory"]] = relationship(back_populates="product")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="product")
