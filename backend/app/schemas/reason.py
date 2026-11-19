from pydantic import BaseModel, ConfigDict, Field
from app.models.product import ProductStatus


class ReasonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: ProductStatus = ProductStatus.ACTIVE
    # При списании по этой причине сотрудник обязан написать комментарий
    requires_comment: bool = False


class ReasonCreate(ReasonBase):
    pass


class ReasonUpdate(BaseModel):
    """Частичное обновление: передаются только изменяемые поля."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    status: ProductStatus | None = None
    requires_comment: bool | None = None


class ReasonRead(ReasonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ReasonDelete(BaseModel):
    status: bool
    message: str