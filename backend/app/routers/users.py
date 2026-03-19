from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, Token
from app.auth import get_password_hash, verify_password, create_access_token
from app.auth import get_current_user 

router = APIRouter(prefix="/users", tags=["Users (Регистрация и профиль)"])


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
# Пополняет баланс текущего пользователя.
async def top_up_balance(
    amount: float, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть больше нуля")
    
    current_user.balance += amount
    await db.commit()
    await db.refresh(current_user)
    return current_user