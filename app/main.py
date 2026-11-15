from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ساخت جدول‌ها موقع روشن شدن سرور
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Auth API",
    description="سیستم احراز هویت با JWT",
    version="0.1.0",
    lifespan=lifespan,
)

# وصل کردن روتر
app.include_router(users.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}