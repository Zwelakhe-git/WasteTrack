from typing import Annotated
from datetime import timedelta
import io

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.waste_record import WasteRecord
from app.models.user import User
from app.models.reason import Reason
from app.models.product import Product, Unit
from app.schemas.analytics import AnalyticsSummary, ReasonStat, ProductStat
from app.utils.utils import get_current_manager_or_admin, wall_clock_now

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Себестоимость единицы: зафиксированная в записи, а для старых записей — текущая из продукта
UNIT_COST = func.coalesce(WasteRecord.unit_cost, Product.cost)
# Сумма потерь по записи, руб.
RECORD_COST = WasteRecord.quantity * UNIT_COST


def _period_filter(days: int, restaurant_id: int | None) -> list:
    # Время считаем «по часам ресторана» — так же, как терминал сохраняет списания
    start_date = wall_clock_now() - timedelta(days=days)
    filters = [WasteRecord.created_at >= start_date]
    if restaurant_id:
        filters.append(WasteRecord.restaurant_id == restaurant_id)
    return filters


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_manager_or_admin)],
    restaurant_id: int | None = None,
    days: int = 7  # По умолчанию аналитика за последние 7 дней
):
    base_filter = _period_filter(days, restaurant_id)

    # 1. Общее количество записей и общая сумма потерь
    total_query = (
        select(
            func.count(WasteRecord.id).label("total_records"),
            func.coalesce(func.sum(RECORD_COST), 0).label("total_cost"),
        )
        .join(Product, WasteRecord.product_id == Product.id)
        .where(*base_filter)
    )
    total_data = (await db.execute(total_query)).mappings().first()

    # 2. Причины списаний по сумме потерь
    # (количество в разных единицах складывать нельзя, поэтому сравниваем в рублях)
    reasons_query = (
        select(
            Reason.name.label("reason_name"),
            func.coalesce(func.sum(RECORD_COST), 0).label("total_cost"),
            func.count(WasteRecord.id).label("records_count"),
        )
        .join(Reason, WasteRecord.reason_id == Reason.id)
        .join(Product, WasteRecord.product_id == Product.id)
        .where(*base_filter)
        .group_by(Reason.name)
        .order_by(func.sum(RECORD_COST).desc())
    )
    top_reasons = [ReasonStat(**row) for row in (await db.execute(reasons_query)).mappings().all()]

    # 3. Топ-10 продуктов по сумме потерь
    products_query = (
        select(
            Product.name.label("product_name"),
            Unit.name.label("unit_name"),
            func.sum(WasteRecord.quantity).label("total_quantity"),
            func.coalesce(func.sum(RECORD_COST), 0).label("total_cost"),
            func.count(WasteRecord.id).label("records_count"),
        )
        .join(Product, WasteRecord.product_id == Product.id)
        .join(Unit, Product.unit_id == Unit.id)
        .where(*base_filter)
        .group_by(Product.id, Product.name, Unit.name)
        .order_by(func.sum(RECORD_COST).desc(), func.sum(WasteRecord.quantity).desc())
        .limit(10)
    )
    top_products = [ProductStat(**row) for row in (await db.execute(products_query)).mappings().all()]

    return AnalyticsSummary(
        total_records=total_data["total_records"] or 0,
        total_cost=total_data["total_cost"] or 0,
        top_reasons=top_reasons,
        top_products=top_products,
    )


@router.get("/export")
async def export_waste_records(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_manager_or_admin)],
    restaurant_id: int | None = None,
    days: int = 30
):
    query = (
        select(
            WasteRecord.created_at,
            Product.name.label("product"),
            Reason.name.label("reason"),
            WasteRecord.quantity,
            Unit.name.label("unit"),
            UNIT_COST.label("unit_cost"),
            RECORD_COST.label("total_cost"),
            WasteRecord.comment,
        )
        .join(Product, WasteRecord.product_id == Product.id)
        .join(Unit, Product.unit_id == Unit.id)
        .join(Reason, WasteRecord.reason_id == Reason.id)
        .where(*_period_filter(days, restaurant_id))
        .order_by(WasteRecord.created_at)
    )
    rows = (await db.execute(query)).mappings().all()

    columns = ['Дата и время', 'Продукт', 'Причина', 'Количество', 'Ед. изм.',
               'Себестоимость ед., руб.', 'Сумма, руб.', 'Комментарий']
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=columns)
    else:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        for col in ('quantity', 'unit_cost', 'total_cost'):
            df[col] = df[col].astype(float)
        df.columns = columns

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Списания')
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=wastetrack_report_{days}d.xlsx"}
    )
