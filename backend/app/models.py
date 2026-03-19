from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class RoleEnum(enum.Enum):
    customer = "customer"
    worker = "worker"


class OrderStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class BidStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100))
    role = Column(Enum(RoleEnum), nullable=False)
    balance = Column(Float, default=0.0)  
    frozen_balance = Column(Float, default=0.0)  

    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    bids = relationship("Bid", back_populates="worker")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  

    title = Column(String(200), nullable=False)
    config_type = Column(String(100), nullable=False)  
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.open)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    worker = relationship("User", foreign_keys=[worker_id])
    bids = relationship("Bid", back_populates="order")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    worker_id = Column(Integer, ForeignKey("users.id"))
    price = Column(Float, nullable=False)
    comment = Column(Text)
    status = Column(Enum(BidStatus), default=BidStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="bids")
    worker = relationship("User", back_populates="bids")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())