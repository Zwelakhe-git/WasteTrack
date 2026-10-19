from pydantic import BaseModel, ConfigDict
from app.models.product import ProductStatus

class ReasonBase(BaseModel):
    name: str
    description: str | None = None
    status: ProductStatus = ProductStatus.ACTIVE

class ReasonCreate(ReasonBase):
    pass

class ReasonRead(ReasonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)