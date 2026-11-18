from sqlalchemy import String, Boolean, Enum as SQLEnum, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
from app.models.product import ProductStatus # Используем тот же Enum для статуса (active/frozen)

class Reason(Base, TimestampMixin):
    __tablename__ = "reasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(SQLEnum(ProductStatus, values_callable=lambda obj: [e.value for e in obj]), default=ProductStatus.ACTIVE, nullable=False)
    # Причина требует обязательного комментария при списании (например, «Прочее»)
    requires_comment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())

    # Связи
    waste_records: Mapped[list["WasteRecord"]] = relationship(back_populates="reason")
