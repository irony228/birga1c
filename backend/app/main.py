from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users  # <-- Подключаем файл с роутами
from app.routers import users, orders, bids # <-- добавили orders

app = FastAPI(title="Биржа 1С")

# Обязательно регистрируем роутер в приложении!
app.include_router(users.router)
app.include_router(orders.router) # <-- зарегистрировали
app.include_router(bids.router)

@app.on_event("startup")
async def startup():
    # Создание таблиц (если они еще не созданы)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "API Биржи 1С работает!"}