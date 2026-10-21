from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.waste_record import WasteRecord
from app.models.user import User
from app.models.reason import Reason
from app.models.product import Product
from app.schemas.analytics import AnalyticsSummary, ReasonStat, ProductStat
from app.routers.product import get_current_manager_or_admin # Переиспользуем проверку роли

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_manager_or_admin)],
    restaurant_id: int | None = None,
    days: int = 7 # По умолчанию аналитика за последние 7 дней
):
    # Определяем временной промежуток
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Базовый фильтр
    base_filter = [WasteRecord.created_at >= start_date]
    if restaurant_id:
        base_filter.append(WasteRecord.restaurant_id == restaurant_id)

    # 1. Общее количество записей и общий объем списаний
    total_query = select(
        func.count(WasteRecord.id).label("total_records"),
        func.coalesce(func.sum(WasteRecord.quantity), 0).label("total_quantity")
    ).where(*base_filter)
    
    total_res = await db.execute(total_query)
    total_data = total_res.mappings().first()

    # 2. Топ причин списаний
    reasons_query = (
        select(
            Reason.name.label("reason_name"),
            func.sum(WasteRecord.quantity).label("total_quantity"),
            func.count(WasteRecord.id).label("records_count")
        )
        .join(Reason, WasteRecord.reason_id == Reason.id)
        .where(*base_filter)
        .group_by(Reason.name)
        .order_by(func.sum(WasteRecord.quantity).desc())
    )
    reasons_res = await db.execute(reasons_query)
    top_reasons = [ReasonStat(**row) for row in reasons_res.mappings().all()]

    # 3. Топ продуктов
    products_query = (
        select(
            Product.name.label("product_name"),
            func.sum(WasteRecord.quantity).label("total_quantity"),
            func.count(WasteRecord.id).label("records_count")
        )
        .join(Product, WasteRecord.product_id == Product.id)
        .where(*base_filter)
        .group_by(Product.name)
        .order_by(func.sum(WasteRecord.quantity).desc())
        .limit(10) # Топ-10 продуктов
    )
    products_res = await db.execute(products_query)
    top_products = [ProductStat(**row) for row in products_res.mappings().all()]

    return AnalyticsSummary(
        total_records=total_data["total_records"] or 0,
        total_quantity=total_data["total_quantity"] or 0,
        top_reasons=top_reasons,
        top_products=top_products
    )