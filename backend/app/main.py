from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import AsyncSessionLocal
from app.init_db import create_first_admin, create_initial_units
from app.routers import auth, restaurant, product, waste, analytics

import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при запуске
    async with AsyncSessionLocal() as session:
        await create_first_admin(session)
        await create_initial_units(session)
    yield
    # Действия при остановке (если нужны)
    pass

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.APP_DEBUG,
    lifespan=lifespan  # Подключаем обработчик
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

app.include_router(auth.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(restaurant.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(waste.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")