from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import datetime


class WasteRecordCreate(BaseModel):
    product_id: int
    reason_id: int
    restaurant_id: int
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    comment: str | None = None
    photo_urls: list[str] | None = None
    # Локальное время ресторана, например '2026-11-06 10:00:00'
    created_at: str | None = None


class WasteRecordUpdate(BaseModel):
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


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
