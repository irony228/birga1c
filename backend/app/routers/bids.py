from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Bid, BidStatus, Order, OrderStatus, RoleEnum, User
from app.schemas import BidCreate, BidResponse, BidStatusEnum, BidWithWorkerResponse
from app.auth import get_current_user

router = APIRouter(prefix="/bids", tags=["Bids (Отклики)"])

@router.post("/{order_id}", response_model=BidResponse)
# Создаёт отклик на заказ (только исполнитель), если заказ открыт.
async def create_bid(
    order_id: int, 
    bid: BidCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.worker:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Только программисты 1С могут оставлять отклики"
        )
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Заказ уже в работе или закрыт")
    if order.customer_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя откликаться на свой заказ")

    existing_bid = await db.execute(
        select(Bid).where(
            Bid.order_id == order_id,
            Bid.worker_id == current_user.id,
            Bid.status == BidStatus.pending,
        )
    )
    if existing_bid.scalars().first():
        raise HTTPException(status_code=400, detail="У вас уже есть активный отклик на этот заказ")

    new_bid = Bid(
        order_id=order_id,
        worker_id=current_user.id,
        price=bid.price,
        comment=bid.comment,
        status=BidStatus.pending,
    )
    db.add(new_bid)
    await db.commit()
    await db.refresh(new_bid)
    return new_bid

@router.get("/{order_id}", response_model=list[BidWithWorkerResponse])
# Список откликов по заказу — только владелец заказа (заказчик).
async def get_bids_for_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != RoleEnum.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Список откликов доступен только заказчику",
        )
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")

    result = await db.execute(
        select(Bid, User.name, User.email)
        .join(User, Bid.worker_id == User.id)
        .where(Bid.order_id == order_id)
        .order_by(Bid.created_at.desc())
    )
    rows = result.all()
    return [
        BidWithWorkerResponse(
            id=bid.id,
            order_id=bid.order_id,
            worker_id=bid.worker_id,
            worker_name=name,
            worker_email=email,
            price=bid.price,
            comment=bid.comment,
            status=BidStatusEnum(bid.status.value),
            created_at=bid.created_at,
        )
        for bid, name, email in rows
    ]


@router.post("/{bid_id}/reject", response_model=BidResponse)
# Отклоняет отклик по заказу (только владелец заказа).
async def reject_bid(
    bid_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bid_result = await db.execute(select(Bid).where(Bid.id == bid_id))
    bid = bid_result.scalars().first()
    if not bid:
        raise HTTPException(status_code=404, detail="Отклик не найден")

    order_result = await db.execute(select(Order).where(Order.id == bid.order_id))
    order = order_result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец заказа может отклонить отклик")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Отклонять можно только пока заказ открыт")
    if bid.status != BidStatus.pending:
        raise HTTPException(status_code=400, detail="Отклонить можно только активный отклик")

    bid.status = BidStatus.rejected
    await db.commit()
    await db.refresh(bid)
    return bid