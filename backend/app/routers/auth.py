from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token
from app.schemas.user import UserRead
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Ищем пользователя по логину
    result = await db.execute(select(User).where(User.login == form_data.username))
    user = result.scalars().first()

    # Проверяем, существует ли пользователь и верный ли пароль
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect login or password"
        )
    
    # Генерируем токен
    return Token(
        access_token=create_access_token(subject=user.id)
    )

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)] # Нам нужно импортировать get_current_user
):
    return current_user