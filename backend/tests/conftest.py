"""Общие фикстуры тестов WasteTrack.

Тесты работают с отдельной базой данных PostgreSQL `<имя основной базы>_test`
на том же сервере: она создаётся автоматически, таблицы пересоздаются при
запуске тестов и очищаются перед каждым тестом. Основная база не затрагивается.

Запуск (в контейнере приложения):
    docker compose exec app pytest -v
Без медленного теста производительности:
    docker compose exec app pytest -v -m "not perf"
"""
import os

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# --- подменяем базу данных ДО импорта приложения -------------------------
from app.config import settings  # noqa: E402

MAIN_SYNC_URL = make_url(settings.DATABASE_URL_SYNC)
TEST_DB_NAME = f"{MAIN_SYNC_URL.database}_test"
TEST_SYNC_URL = MAIN_SYNC_URL.set(database=TEST_DB_NAME)
TEST_ASYNC_URL = make_url(settings.DATABASE_URL).set(database=TEST_DB_NAME)

from tests.helpers import PASSWORD, TERMINAL_KEY, login  # noqa: E402
settings.TERMINAL_API_KEY = TERMINAL_KEY

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.core.security import get_password_hash  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
import app.models as _all_models  # noqa: E402,F401  — регистрирует все модели в Base.metadata
from app.models.product import Product, ProductStatus, Unit  # noqa: E402
from app.models.reason import Reason  # noqa: E402
from app.models.restaurant import Restaurant  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


# --- база данных ----------------------------------------------------------
@pytest.fixture(scope="session")
def sync_engine():
    """Создаёт тестовую базу (если её нет) и чистую схему таблиц."""
    admin_engine = create_engine(MAIN_SYNC_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB_NAME}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    engine = create_engine(TEST_SYNC_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(sync_engine):
    """Перед каждым тестом — пустые таблицы и счётчики id с единицы."""
    names = ", ".join(t.name for t in Base.metadata.sorted_tables)
    with sync_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    yield


@pytest_asyncio.fixture
async def session_factory(sync_engine):
    # NullPool: соединение не переживает тест и не привязано к чужому event loop
    engine = create_async_engine(TEST_ASYNC_URL, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# --- тестовые данные --------------------------------------------------------
@pytest_asyncio.fixture
async def seed(db):
    """Ресторан, единицы, продукты, причины и пользователи с известными паролями."""
    restaurant = Restaurant(name="Тестовый ресторан", number="T-001", address="ул. Тестовая, 1")
    sht, kg = Unit(name="шт"), Unit(name="кг")
    db.add_all([restaurant, sht, kg])
    await db.flush()

    patty = Product(name="Котлета для Воппера", category="мясо", unit_id=sht.id, cost=140)
    bun = Product(name="Булочка гамбургер", category="булки", unit_id=sht.id, cost=15)
    cheese = Product(name="Сыр", category="молочное", unit_id=kg.id, cost=0)
    expired = Reason(name="Истек срок хранения")
    dropped = Reason(name="Упало на пол")
    other = Reason(name="Прочее", requires_comment=True)
    admin = User(login="admin_t", password_hash=get_password_hash(PASSWORD),
                 display_name="Админ", role=UserRole.ADMIN)
    manager = User(login="manager_t", password_hash=get_password_hash(PASSWORD),
                   display_name="Менеджер", role=UserRole.MANAGER, restaurant_id=restaurant.id)
    db.add_all([patty, bun, cheese, expired, dropped, other, admin, manager])
    await db.commit()

    return {
        "restaurant": restaurant.id,
        "patty": patty.id, "bun": bun.id, "cheese": cheese.id,
        "expired": expired.id, "dropped": dropped.id, "other": other.id,
    }


@pytest_asyncio.fixture
async def manager_headers(client, seed):
    r = await login(client, "manager_t")
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest_asyncio.fixture
async def admin_headers(client, seed):
    r = await login(client, "admin_t")
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
