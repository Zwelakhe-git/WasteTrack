from typing import Annotated, List
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.config import settings
from app.models.waste_record import WasteRecord
from app.models.product import Product, ProductStatus
from app.models.reason import Reason
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.waste import WasteRecordCreate, WasteRecordRead, WasteRecordUpdate
from app.core.deps import get_current_user
from app.utils.utils import parse_client_time

router = APIRouter(prefix="/waste", tags=["Waste Records"])


# Проверка ключа терминала (для сотрудников кухни без логина)
async def verify_terminal_key(x_terminal_key: str = Header(...)):
    if x_terminal_key != settings.TERMINAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid terminal API key"
        )
    return x_terminal_key


async def _load_record(db: AsyncSession, record_id: int) -> WasteRecord | None:
    result = await db.execute(
        select(WasteRecord)
        .options(selectinload(WasteRecord.product).selectinload(Product.unit),
                 selectinload(WasteRecord.reason))
        .where(WasteRecord.id == record_id)
    )
    return result.scalars().first()


@router.post("/", response_model=WasteRecordRead, status_code=status.HTTP_201_CREATED)
async def create_waste_record(
    waste_in: WasteRecordCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    terminal_key: Annotated[str, Depends(verify_terminal_key)]  # Защита ключом, а не JWT
):
    """Создаёт списание. Если запись с тем же продуктом, причиной и часом уже есть,
    обновляет её количество (одна запись на связку «продукт + причина + час»)."""
    product = await db.get(Product, waste_in.product_id)
    reason = await db.get(Reason, waste_in.reason_id)
    restaurant = await db.get(Restaurant, waste_in.restaurant_id)

    if not product or product.status != ProductStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Product not found or frozen")
    if not reason or reason.status != ProductStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Reason not found or frozen")
    if not restaurant:
        raise HTTPException(status_code=400, detail="Restaurant not found")

    created_at = parse_client_time(waste_in.created_at)

    record = None
    if created_at is not None:
        record = (await db.execute(
            select(WasteRecord).where(
                WasteRecord.created_at == created_at,
                WasteRecord.reason_id == waste_in.reason_id,
                WasteRecord.product_id == waste_in.product_id,
                WasteRecord.restaurant_id == waste_in.restaurant_id
            )
        )).scalars().first()

    if record:
        record.quantity = waste_in.quantity
    else:
        record = WasteRecord(
            product_id=waste_in.product_id,
            reason_id=waste_in.reason_id,
            restaurant_id=waste_in.restaurant_id,
            quantity=waste_in.quantity,
            # себестоимость на момент списания; пока цена не задана — пусто,
            # заполнится, когда менеджер укажет цену в справочнике
            unit_cost=product.cost if product.cost and product.cost > 0 else None,
            comment=waste_in.comment,
            photo_urls=waste_in.photo_urls,
            created_by_id=None  # Сотрудник кухни анонимен
        )
        if created_at is not None:
            record.created_at = created_at
        db.add(record)
    await db.commit()

    return await _load_record(db, record.id)


@router.patch("/{record_id}", response_model=WasteRecordRead)
async def update_waste_record(
    record_id: int,
    waste_in: WasteRecordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    terminal_key: Annotated[str, Depends(verify_terminal_key)]
):
    """Изменение количества в существующей записи по её id."""
    record = await db.get(WasteRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    record.quantity = waste_in.quantity
    await db.commit()
    return await _load_record(db, record_id)


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
    terminal_key: Annotated[str, Depends(verify_terminal_key)],
    restaurant_id: int,
    date: str  # YYYY-MM-DD, локальная дата ресторана
):
    """Записи за день для таблицы терминала «продукт × час»."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")
    start_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    query = (
        select(WasteRecord)
        .options(selectinload(WasteRecord.reason))
        .where(
            WasteRecord.restaurant_id == restaurant_id,
            WasteRecord.created_at >= start_dt,
            WasteRecord.created_at < end_dt
        )
    )
    result = await db.execute(query)
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "product_id": r.product_id,
            "reason_id": r.reason_id,
            "reason_name": r.reason.name if r.reason else "",
            "hour": r.created_at.astimezone(timezone.utc).hour,
            "quantity": float(r.quantity)
        }
        for r in records
    ]


@router.delete("/{record_id}")
async def delete_waste_record(
    record_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    terminal_key: Annotated[str, Depends(verify_terminal_key)]  # Защищаем ключом терминала
):
    """Отмена записи (когда сотрудник вводит 0 для выбранной причины)"""
    record = await db.get(WasteRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    await db.delete(record)
    await db.commit()
    return {"status": "deleted"}
