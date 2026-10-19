from pydantic import BaseModel, ConfigDict
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

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    unit: UnitRead # Вложенная схема, чтобы сразу отдавать единицу измерения
    model_config = ConfigDict(from_attributes=True)