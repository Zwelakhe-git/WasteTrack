from fastapi import Depends, HTTPException
from typing import Annotated
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from datetime import datetime

async def get_current_manager_or_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Manager or Admin required")
    return current_user

def parse_js_iso(iso_string: str) -> datetime:
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
