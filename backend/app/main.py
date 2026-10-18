from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    debug=settings.APP_DEBUG,
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
