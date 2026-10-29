from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.config import settings
from app.models.waste_record import WasteRecord
from app.models.product import Product
from app.models.reason import Reason
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.waste import WasteRecordCreate, WasteRecordRead
from app.core.deps import get_current_user

router = APIRouter(prefix="/waste", tags=["Waste Records"])

# Проверка ключа терминала (для сотрудников кухни без логина)
async def verify_terminal_key(x_terminal_key: str = Header(...)):
    if x_terminal_key != settings.TERMINAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid terminal API key"
        )
    return x_terminal_key

@router.post("/", response_model=WasteRecordRead, status_code=status.HTTP_201_CREATED)
async def create_waste_record(
    waste_in: WasteRecordCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    terminal_key: Annotated[str, Depends(verify_terminal_key)] # Защита ключом, а не JWT
):
    # Проверяем существование продукта, причины и ресторана
    product = await db.get(Product, waste_in.product_id)
    reason = await db.get(Reason, waste_in.reason_id)
    restaurant = await db.get(Restaurant, waste_in.restaurant_id)

    if not product or product.status != "active":
        raise HTTPException(status_code=400, detail="Product not found or frozen")
    if not reason or reason.status != "active":
        raise HTTPException(status_code=400, detail="Reason not found or frozen")
    if not restaurant:
        raise HTTPException(status_code=400, detail="Restaurant not found")

    new_record = WasteRecord(
        product_id=waste_in.product_id,
        reason_id=waste_in.reason_id,
        restaurant_id=waste_in.restaurant_id,
        quantity=waste_in.quantity,
        comment=waste_in.comment,
        photo_urls=waste_in.photo_urls,
        created_by_id=None # Сотрудник кухни анонимен
    )
    db.add(new_record)
    await db.commit()

    # Загружаем созданную запись со связями для ответа
    result = await db.execute(
        select(WasteRecord)
        .options(selectinload(WasteRecord.product).selectinload(Product.unit),
                 selectinload(WasteRecord.reason))
        .where(WasteRecord.id == new_record.id)
    )
    return result.scalars().first()

@router.get("/", response_model=List[WasteRecordRead])
async def get_waste_records(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    restaurant_id: int | None = None
):
    """Эндпоинт для менеджера: просмотр истории списаний"""
    query = select(WasteRecord).options(
        selectinload(WasteRecord.product).selectinload(Product.unit),
        selectinload(WasteRecord.reason)
    )
    if restaurant_id:
        query = query.where(WasteRecord.restaurant_id == restaurant_id)
        
    result = await db.execute(query.order_by(WasteRecord.created_at.desc()))
    return result.scalars().all()


@router.get("/grid")
async def get_waste_grid(
    db: Annotated[AsyncSession, Depends(get_db)],
    restaurant_id: int,
    date: str  # формат YYYY-MM-DD
):
    """
    Возвращает сгруппированные по часам данные о списаниях за конкретный день.
    """
    # Парсим дату и делаем границы дня
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    start_dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    # Группируем по product_id и часу создания записи
    query = (
        select(
            WasteRecord.product_id,
            extract('hour', WasteRecord.created_at).label('hour'),
            func.sum(WasteRecord.quantity).label('total_quantity')
        )
        .where(
            WasteRecord.restaurant_id == restaurant_id,
            WasteRecord.created_at >= start_dt,
            WasteRecord.created_at < end_dt
        )
        .group_by(WasteRecord.product_id, extract('hour', WasteRecord.created_at))
    )
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    # Возвращаем в удобном для фронтенда формате
    return [
        {
            "product_id": row["product_id"],
            "hour": int(row["hour"]),
            "total_quantity": float(row["total_quantity"])
        }
        for row in rows
    ]

@router.delete("/{record_id}")
async def delete_waste_record(
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Удаление ошибочной записи (если менеджер нажал 0)"""
    result = await db.execute(select(WasteRecord).where(WasteRecord.id == record_id))
    record = result.scalars().first()
    if record:
        await db.delete(record)
        await db.commit()
        return {"status": "deleted"}
    return {"status": "not found"}
