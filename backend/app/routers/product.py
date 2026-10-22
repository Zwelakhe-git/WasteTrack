from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product, Unit, ProductStatus
from app.schemas.product import ProductCreate, ProductRead, UnitRead
from app.core.deps import get_current_user
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/products", tags=["Products"])

# Зависимость: Админ ИЛИ Менеджер
async def get_current_manager_or_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Manager or Admin required")
    return current_user

@router.get("/units", response_model=List[UnitRead])
async def get_units(db: Annotated[AsyncSession, Depends(get_db)]):
    """Получить список всех единиц измерения (кг, г, шт, л, мл)"""
    result = await db.execute(select(Unit))
    return result.scalars().all()

@router.get("/", response_model=List[ProductRead])
async def get_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: ProductStatus | None = None
):
    query = select(Product).options(selectinload(Product.unit)) # <--- Добавили selectinload
    if status:
        query = query.where(Product.status == status)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_manager_or_admin)]
):
    unit = await db.get(Unit, product_in.unit_id)
    if not unit:
        raise HTTPException(status_code=400, detail="Unit not found")

    new_product = Product(**product_in.model_dump())
    db.add(new_product)
    await db.commit()
    
    # ВМЕСТО await db.refresh(new_product) делаем так:
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.unit)) # <--- Говорим сразу подгрузить Unit
        .where(Product.id == new_product.id)
    )
    return result.scalars().first()