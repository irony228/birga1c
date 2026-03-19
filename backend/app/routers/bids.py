from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Bid, Order, User, RoleEnum, OrderStatus
from app.schemas import BidCreate, BidResponse
from app.auth import get_current_user

router = APIRouter(prefix="/bids", tags=["Bids (Отклики)"])

@router.post("/{order_id}", response_model=BidResponse)
async def create_bid(
    order_id: int, 
    bid: BidCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, что откликается исполнитель
    if current_user.role != RoleEnum.worker:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Только программисты 1С могут оставлять отклики"
        )
    
    # Ищем заказ и проверяем, что он открыт
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Заказ уже в работе или закрыт")

    # Создаем отклик
    new_bid = Bid(
        order_id=order_id,
        worker_id=current_user.id,
        price=bid.price,
        comment=bid.comment
    )
    db.add(new_bid)
    await db.commit()
    await db.refresh(new_bid)
    return new_bid

@router.get("/{order_id}", response_model=list[BidResponse])
async def get_bids_for_order(order_id: int, db: AsyncSession = Depends(get_db)):
    # Получить все отклики к конкретному заказу
    result = await db.execute(select(Bid).where(Bid.order_id == order_id))
    return result.scalars().all()