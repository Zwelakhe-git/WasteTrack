from decimal import Decimal
from sqlalchemy import Numeric, String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

class WasteRecord(Base, TimestampMixin):
    __tablename__ = "waste_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    reason_id: Mapped[int] = mapped_column(ForeignKey("reasons.id"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True) # Может быть NULL, если списал сотрудник без входа

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False) # до 2 знаков после запятой
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Сохраняем список URL фото в формате JSON-массива
    photo_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Связи
    product: Mapped["Product"] = relationship(back_populates="waste_records")
    reason: Mapped["Reason"] = relationship(back_populates="waste_records")
    restaurant: Mapped["Restaurant"] = relationship(back_populates="waste_records")
    creator: Mapped["User | None"] = relationship(back_populates="waste_records")