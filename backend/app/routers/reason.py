from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.reason import Reason
from app.schemas.reason import ReasonRead

router = APIRouter(prefix="/reasons", tags=["Reasons"])

@router.get("/", response_model=List[ReasonRead])
async def get_active_reasons(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Reason).where(Reason.status == "active"))
    return result.scalars().all()