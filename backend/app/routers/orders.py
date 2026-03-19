from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Order, User, RoleEnum, OrderStatus, Bid, Notification
from app.schemas import OrderCreate, OrderResponse
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders (Заказы)"])

@router.post("/", response_model=OrderResponse)
# Создаёт заказ (только заказчик) в статусе открыт.
async def create_order(
    order: OrderCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != RoleEnum.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Только заказчики могут создавать заказы"
        )
    
    new_order = Order(
        customer_id=current_user.id,
        title=order.title,
        config_type=order.config_type,
        description=order.description,
        budget=order.budget
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

@router.get("/", response_model=list[OrderResponse])
# Возвращает список заказов (лента).
async def get_orders(db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    return result.scalars().all()

@router.post("/{order_id}/accept/{bid_id}")
# Выбирает исполнителя: переводит деньги в заморозку и статус в в работе.
async def accept_bid(
    order_id: int, 
    bid_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalars().first()
    
    if not order or order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")
    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Исполнитель уже выбран или заказ закрыт")

    
    bid_result = await db.execute(select(Bid).where(Bid.id == bid_id, Bid.order_id == order_id))
    bid = bid_result.scalars().first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Отклик не найден")

    
    
    if current_user.balance < order.budget:
        raise HTTPException(status_code=400, detail="Недостаточно средств на балансе. Пополните счет.")

    
    current_user.balance -= order.budget
    current_user.frozen_balance += order.budget

    
    order.status = OrderStatus.in_progress
    order.worker_id = bid.worker_id

    await db.commit()
    return {"message": "Исполнитель выбран, средства заморожены", "order_status": order.status.value}

@router.post("/{order_id}/complete")
# Завершает заказ: размораживает деньги, закрывает заказ и создаёт уведомление.
async def complete_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order or order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")
    if order.status != OrderStatus.in_progress:
        raise HTTPException(status_code=400, detail="Заказ еще не в работе или уже закрыт")

    
    worker_result = await db.execute(select(User).where(User.id == order.worker_id))
    worker = worker_result.scalars().first()

    if not worker:
        raise HTTPException(status_code=404, detail="Исполнитель не найден")

    
    current_user.frozen_balance -= order.budget
    worker.balance += order.budget

    
    order.status = OrderStatus.closed

    
    notification = Notification(
        user_id=worker.id,
        message=f"Заказ '{order.title}' успешно завершен! На ваш баланс зачислено {order.budget} руб."
    )
    db.add(notification)

    await db.commit()
    return {"message": "Заказ завершен, средства переведены", "worker_new_balance": worker.balance}


@router.post("/{order_id}/cancel")
# Досрочно закрывает заказ в статусе открыт без движения денег.
async def cancel_open_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order or order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")
    if order.status != OrderStatus.open:
        raise HTTPException(
            status_code=400,
            detail="Досрочно можно закрыть только заказ в статусе open"
        )

    order.status = OrderStatus.closed
    await db.commit()
    return {"message": "Заказ досрочно закрыт", "order_status": order.status.value}