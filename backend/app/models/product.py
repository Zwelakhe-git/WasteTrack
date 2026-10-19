from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin

class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False) # кг, г, шт, л, мл

    products: Mapped[list["Product"]] = relationship(back_populates="unit")

class ProductStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[ProductStatus] = mapped_column(Enum(ProductStatus, values_callable=lambda obj: [e.value for e in obj]), default=ProductStatus.ACTIVE, nullable=False)
    
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)

    # Связи
    unit: Mapped["Unit"] = relationship(back_populates="products")
    waste_records: Mapped[list["WasteRecord"]] = relationship(back_populates="product")