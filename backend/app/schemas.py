from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from enum import Enum
from datetime import datetime
from typing import Optional

class RoleEnum(str, Enum):
    customer = "customer"
    worker = "worker"


class BidStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: RoleEnum

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_limit(cls, v: str) -> str:
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

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class OrderCreate(BaseModel):
    title: str
    config_type: str
    description: str
    budget: float

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    worker_id: Optional[int] = None
    title: str
    config_type: str
    description: str
    budget: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BidCreate(BaseModel):
    price: float
    comment: str

class BidResponse(BaseModel):
    id: int
    order_id: int
    worker_id: int
    price: float
    comment: str
    status: BidStatusEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BidWithWorkerResponse(BaseModel):
    """Отклик с данными исполнителя (для страницы заказа заказчика)."""
    id: int
    order_id: int
    worker_id: int
    worker_name: Optional[str] = None
    worker_email: Optional[str] = None
    price: float
    comment: Optional[str] = None
    status: BidStatusEnum
    created_at: datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)