from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.product import ProductStatus


class UnitRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    category: str
    unit_id: int
    status: ProductStatus = ProductStatus.ACTIVE
    # Себестоимость одной единицы измерения, руб.
    cost: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """Частичное обновление: передаются только изменяемые поля."""
    name: str | None = None
    category: str | None = None
    unit_id: int | None = None
    status: ProductStatus | None = None
    cost: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class ProductRead(ProductBase):
    id: int
    unit: UnitRead  # Вложенная схема, чтобы сразу отдавать единицу измерения
    model_config = ConfigDict(from_attributes=True)
