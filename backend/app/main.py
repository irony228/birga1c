from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine, Base
from app.routers import users, orders, bids, notifications

app = FastAPI(title="Биржа 1С")

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(bids.router)
app.include_router(notifications.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("ALTER TABLE bids ADD COLUMN IF NOT EXISTS status ENUM('pending','accepted','rejected') NOT NULL DEFAULT 'pending'")
        )

@app.get("/")
async def root():
    return {"message": "API Биржи 1С работает корректно"}