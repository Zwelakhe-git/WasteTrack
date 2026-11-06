from pydantic import BaseModel
from decimal import Decimal


class ReasonStat(BaseModel):
    reason_name: str
    total_cost: Decimal        # сумма потерь, руб.
    records_count: int


class ProductStat(BaseModel):
    product_name: str
    unit_name: str
    total_quantity: Decimal    # в единицах продукта (шт, кг, л ...)
    total_cost: Decimal        # сумма потерь, руб.
    records_count: int


class AnalyticsSummary(BaseModel):
    total_records: int
    total_cost: Decimal        # общая сумма потерь, руб.
    top_reasons: list[ReasonStat]
    top_products: list[ProductStat]
