from fastapi import Depends, HTTPException
from typing import Annotated
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.core.deps import get_current_user
from app.models.user import User, UserRole


async def get_current_manager_or_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Manager or Admin required")
    return current_user


def parse_js_iso(iso_string: str) -> datetime:
    return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))


def parse_client_time(value: str | None) -> datetime | None:
    """Время с терминала: локальное время ресторана без часового пояса
    (например, '2026-11-06 10:00:00'). Сохраняем его как есть, помечая UTC,
    чтобы час в таблице терминала совпадал с часом, когда сделано списание."""
    if not value:
        return None
    dt = parse_js_iso(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def wall_clock_now() -> datetime:
    """Текущее время ресторана в том же формате, в каком терминал сохраняет списания.
    Использовать вместо datetime.utcnow() при расчёте периодов аналитики."""
    local = datetime.now(timezone.utc) + timedelta(hours=settings.APP_TZ_OFFSET_HOURS)
    return local.replace(tzinfo=timezone.utc)
