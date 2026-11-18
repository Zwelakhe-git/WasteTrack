from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from datetime import datetime


def _clean_comment(value: str | None) -> str | None:
    # Пустой комментарий или одни пробелы считаем отсутствием комментария
    if value is None:
        return None
    value = value.strip()
    return value or None


class WasteRecordCreate(BaseModel):
    product_id: int
    reason_id: int
    restaurant_id: int
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    comment: str | None = Field(default=None, max_length=500)
    photo_urls: list[str] | None = None
    # Локальное время ресторана, например '2026-11-06 10:00:00'
    created_at: str | None = None

    @field_validator("comment")
    @classmethod
    def strip_comment(cls, v: str | None) -> str | None:
        return _clean_comment(v)


class WasteRecordUpdate(BaseModel):
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("comment")
    @classmethod
    def strip_comment(cls, v: str | None) -> str | None:
        return _clean_comment(v)



class WasteRecordRead(BaseModel):
    id: int
    product_id: int
    reason_id: int
    restaurant_id: int
    created_by_id: int | None = None
    quantity: Decimal
    unit_cost: Decimal | None = None
    comment: str | None = None
    photo_urls: list[str] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
