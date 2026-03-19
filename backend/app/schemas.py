from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from enum import Enum

# Дублируем Enum для Pydantic, чтобы фронтенд мог присылать строки
class RoleEnum(str, Enum):
    customer = "customer"
    worker = "worker"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: RoleEnum

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_limit(cls, v: str) -> str:
        # bcrypt ограничивает длину пароля 72 байтами (UTF-8).
        # Если пароль длиннее, passlib/bcrypt кинет ValueError.
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password must be <= 72 bytes for bcrypt")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password must be <= 72 bytes for bcrypt")
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: RoleEnum
    balance: float
    frozen_balance: float

    # Разрешаем Pydantic читать данные из моделей SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str