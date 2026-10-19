import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.models.product import Unit

logger = logging.getLogger(__name__)

async def create_first_admin(db: AsyncSession) -> None:
    # Проверяем, есть ли хоть один пользователь
    result = await db.execute(select(User).limit(1))
    user_exists = result.scalars().first()

    if not user_exists:
        logger.info("База пуста. Создаем первого администратора (admin/admin123)...")
        
        admin = User(
            login="admin",
            password_hash=get_password_hash("admin123"),
            display_name="Главный Администратор",
            role=UserRole.ADMIN,
            restaurant_id=None  # Админ не привязан к конкретному ресторану
        )
        
        db.add(admin)
        await db.commit()
        logger.info("Администратор успешно создан!")
    else:
        logger.info("Пользователи уже существуют. Инициализация не требуется.")

async def create_initial_units(db: AsyncSession) -> None:
    result = await db.execute(select(Unit).limit(1))
    if not result.scalars().first():
        logger.info("Создаем базовые единицы измерения...")
        units = [
            Unit(name="кг"), Unit(name="г"), Unit(name="шт"), 
            Unit(name="л"), Unit(name="мл"), Unit(name="порция")
        ]
        db.add_all(units)
        await db.commit()
        logger.info("Единицы измерения созданы.")