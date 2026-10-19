from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product, Unit, ProductStatus
from app.schemas.product import ProductCreate, ProductRead, UnitRead
from app.core.deps import get_current_user

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
    current_user: Annotated[User, Depends(get_current_manager_or_admin)],
    status: ProductStatus | None = None # Можно фильтровать по статусу (например, только active)
):
    query = select(Product)
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
    # Проверяем, существует ли такая единица измерения
    unit = await db.get(Unit, product_in.unit_id)
    if not unit:
        raise HTTPException(status_code=400, detail="Unit not found")

    new_product = Product(**product_in.model_dump())
    db.add(new_product)
    await db.commit()
    # Обновляем, чтобы подтянуть связанную Unit для ответа
    await db.refresh(new_product)
    return new_product