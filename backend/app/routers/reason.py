from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.reason import Reason
from app.schemas.reason import ReasonRead, ReasonCreate
from app.models.user import User
from app.utils.utils import get_current_manager_or_admin

router = APIRouter(prefix="/reasons", tags=["Reasons"])

@router.get("/", response_model=List[ReasonRead])
async def get_active_reasons(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Reason).where(Reason.status == "active"))
    return result.scalars().all()

@router.post("/", response_model=ReasonRead, status_code=status.HTTP_201_CREATED)
async def create_reason(
    reason_in: ReasonCreate, 
    db: Annotated[AsyncSession, Depends(get_db)], 
    current_user: Annotated[User, Depends(get_current_manager_or_admin)]):
    new_reason = Reason(**reason_in.model_dump())
    db.add(new_reason)
    await db.commit()
    await db.refresh(new_reason)
    return new_reason