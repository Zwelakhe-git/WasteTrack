from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Номер точки

    # Связи
    users: Mapped[list["User"]] = relationship(back_populates="restaurant")
    waste_records: Mapped[list["WasteRecord"]] = relationship(back_populates="restaurant")