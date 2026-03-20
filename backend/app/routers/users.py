from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, Token, TopUpRequest
from app.auth import get_password_hash, verify_password, create_access_token
from app.auth import get_current_user 

router = APIRouter(prefix="/users", tags=["Users (Регистрация и профиль)"])


@router.get("/me", response_model=UserResponse)
# Текущий пользователь (баланс, роль и т.д.) — по JWT.
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse)
# Регистрирует пользователя в системе.
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    
    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        name=user.name,
        role=user.role.value
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
# Логинит пользователя и выдаёт JWT-токен.
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()

    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    
    access_token = create_access_token(
        data={"sub": db_user.email, "id": db_user.id, "role": db_user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/top-up", response_model=UserResponse)
# Пополняет баланс без ЮKassa только если ALLOW_FAKE_TOPUP=true.
async def top_up_balance(
    body: TopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.allow_fake_topup:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Используйте пополнение через ЮKassa в профиле.",
        )
    amount = body.amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть больше нуля")

    current_user.balance += amount
    await db.commit()
    await db.refresh(current_user)
    return current_user