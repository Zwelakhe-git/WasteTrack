from pydantic import BaseModel
from decimal import Decimal

class ReasonStat(BaseModel):
    reason_name: str
    total_quantity: Decimal
    records_count: int

class ProductStat(BaseModel):
    product_name: str
    total_quantity: Decimal
    records_count: int

class AnalyticsSummary(BaseModel):
    total_records: int
    total_quantity: Decimal
    top_reasons: list[ReasonStat]
    top_products: list[ProductStat]