from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False) # например, "create", "update", "delete"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # например, "product", "reason"
    entity_id: Mapped[int] = mapped_column(nullable=False)
    
    # Сохраняем старые и новые значения в JSON (для отслеживания изменений)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="audit_logs")