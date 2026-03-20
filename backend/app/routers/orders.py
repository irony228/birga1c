from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Bid, BidStatus, Notification, Order, OrderStatus, RoleEnum, User
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
# Возвращает список заказов по роли и цели
async def get_orders(
    scope: str = Query(..., description="customer_open|customer_in_progress|customer_closed|worker_open_available|worker_in_progress|worker_bidded_active"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 3 списка для заказчика
    if scope == "customer_open":
        if current_user.role != RoleEnum.customer:
            raise HTTPException(status_code=403, detail="Список доступен только заказчику")
        query = select(Order).where(
            Order.customer_id == current_user.id,
            Order.status == OrderStatus.open,
        )
    elif scope == "customer_in_progress":
        if current_user.role != RoleEnum.customer:
            raise HTTPException(status_code=403, detail="Список доступен только заказчику")
        query = select(Order).where(
            Order.customer_id == current_user.id,
            Order.status == OrderStatus.in_progress,
        )
    elif scope == "customer_closed":
        if current_user.role != RoleEnum.customer:
            raise HTTPException(status_code=403, detail="Список доступен только заказчику")
        query = select(Order).where(
            Order.customer_id == current_user.id,
            Order.status == OrderStatus.closed,
        )
    # 3 списка для исполнителя
    elif scope == "worker_open_available":
        if current_user.role != RoleEnum.worker:
            raise HTTPException(status_code=403, detail="Список доступен только исполнителю")
        # Открытые заказы, где у исполнителя нет активного отклика.
        subq = select(Bid.order_id).where(
            Bid.worker_id == current_user.id,
            Bid.status.in_([BidStatus.pending, BidStatus.accepted]),
        )
        query = select(Order).where(
            Order.status == OrderStatus.open,
            Order.id.not_in(subq),
        )
    elif scope == "worker_in_progress":
        if current_user.role != RoleEnum.worker:
            raise HTTPException(status_code=403, detail="Список доступен только исполнителю")
        query = select(Order).where(
            Order.worker_id == current_user.id,
            Order.status == OrderStatus.in_progress,
        )
    elif scope == "worker_bidded_active":
        if current_user.role != RoleEnum.worker:
            raise HTTPException(status_code=403, detail="Список доступен только исполнителю")
        query = (
            select(Order)
            .join(Bid, Bid.order_id == Order.id)
            .where(
                Bid.worker_id == current_user.id,
                Bid.status == BidStatus.pending,
                Order.status != OrderStatus.closed,
            )
        )
    else:
        raise HTTPException(status_code=400, detail="Неизвестный scope")

    result = await db.execute(query.order_by(Order.created_at.desc()))
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponse)
# Один заказ: только владелец-заказчик.
async def get_order_by_id(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != RoleEnum.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Просматривать карточку заказа таким образом может только заказчик",
        )
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")
    return order


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

    
    bid_result = await db.execute(
        select(Bid).where(Bid.id == bid_id, Bid.order_id == order_id, Bid.status == BidStatus.pending)
    )
    bid = bid_result.scalars().first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Отклик не найден или уже неактивен")

    
    
    if current_user.balance < order.budget:
        raise HTTPException(status_code=400, detail="Недостаточно средств на балансе. Пополните счет.")

    
    current_user.balance -= order.budget
    current_user.frozen_balance += order.budget

    
    order.status = OrderStatus.in_progress
    order.worker_id = bid.worker_id
    bid.status = BidStatus.accepted

    other_bids_result = await db.execute(
        select(Bid).where(
            Bid.order_id == order_id,
            Bid.id != bid.id,
            Bid.status == BidStatus.pending,
        )
    )
    for other_bid in other_bids_result.scalars().all():
        other_bid.status = BidStatus.rejected

    await db.commit()
    return {"message": "Исполнитель выбран, средства заморожены", "order_status": order.status.value}

@router.post("/{order_id}/complete")
# Завершает заказ: размораживает деньги у заказчика, зачисляет исполнителю, закрывает заказ.
# Инициировать могут: владелец-заказчик или назначенный исполнитель.
async def complete_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.status != OrderStatus.in_progress:
        raise HTTPException(status_code=400, detail="Заказ еще не в работе или уже закрыт")

    customer_result = await db.execute(select(User).where(User.id == order.customer_id))
    customer = customer_result.scalars().first()
    worker_result = await db.execute(select(User).where(User.id == order.worker_id))
    worker = worker_result.scalars().first()

    if not customer or not worker:
        raise HTTPException(status_code=404, detail="Заказчик или исполнитель не найден")

    is_customer_owner = current_user.role == RoleEnum.customer and customer.id == current_user.id
    is_assigned_worker = current_user.role == RoleEnum.worker and worker.id == current_user.id
    if not (is_customer_owner or is_assigned_worker):
        raise HTTPException(
            status_code=403,
            detail="Завершить заказ может только заказчик или назначенный исполнитель",
        )

    customer.frozen_balance -= order.budget
    worker.balance += order.budget
    order.status = OrderStatus.closed

    if is_assigned_worker:
        db.add(
            Notification(
                user_id=customer.id,
                message=(
                    f"Исполнитель завершил заказ «{order.title}». "
                    f"С заморозки списано {order.budget} руб. в пользу исполнителя."
                ),
            )
        )
        db.add(
            Notification(
                user_id=worker.id,
                message=(
                    f"Заказ «{order.title}» отмечен как выполненный. "
                    f"На баланс зачислено {order.budget} руб."
                ),
            )
        )
    else:
        db.add(
            Notification(
                user_id=worker.id,
                message=(
                    f"Заказ '{order.title}' успешно завершен! "
                    f"На ваш баланс зачислено {order.budget} руб."
                ),
            )
        )

    await db.commit()
    await db.refresh(worker)
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