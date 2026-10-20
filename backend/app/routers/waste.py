from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

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