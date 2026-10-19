from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantRead
from app.core.deps import get_current_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Зависимость для проверки, что текущий юзер - админ
async def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin required."
        )
    return current_user

@router.get("/", response_model=List[RestaurantRead])
async def get_restaurants(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)] # Читать могут все авторизованные
):
    result = await db.execute(select(Restaurant))
    return result.scalars().all()

@router.post("/", response_model=RestaurantRead, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_in: RestaurantCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)] # Только админ
):
    # Проверка на уникальность номера ресторана
    existing = await db.execute(select(Restaurant).where(Restaurant.number == restaurant_in.number))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Restaurant with this number already exists")
        
    new_restaurant = Restaurant(**restaurant_in.model_dump())
    db.add(new_restaurant)
    await db.commit()
    await db.refresh(new_restaurant)
    return new_restaurant