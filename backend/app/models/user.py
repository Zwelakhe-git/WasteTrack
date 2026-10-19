import enum
from sqlalchemy import String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

class UserRole(str, enum.Enum):
    MANAGER = "manager"
    ADMIN = "admin"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), default=UserRole.MANAGER, nullable=False)
    
    restaurant_id: Mapped[int | None] = mapped_column(ForeignKey("restaurants.id"), nullable=True)
    
    # Связи
    restaurant: Mapped["Restaurant"] = relationship(back_populates="users")
    waste_records: Mapped[list["WasteRecord"]] = relationship(back_populates="creator")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
