from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class WasteRecordCreate(BaseModel):
    product_id: int
    reason_id: int
    restaurant_id: int
    quantity: Decimal
    comment: str | None = None
    photo_urls: list[str] | None = None
    # restaurant_id сюда НЕ входит, он берется из сессии

class WasteRecordRead(BaseModel):
    id: int
    product_id: int
    reason_id: int
    restaurant_id: int
    created_by_id: int | None = None
    quantity: Decimal
    comment: str | None = None
    photo_urls: list[str] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)