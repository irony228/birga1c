from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Notification, User
from app.schemas import NotificationResponse
from app.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications (Уведомления)"])

@router.get("/", response_model=list[NotificationResponse])
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получаем все уведомления текущего пользователя, новые сверху
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()

@router.post("/{notif_id}/read")
async def mark_as_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Помечаем прочитанным
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
    )
    notif = result.scalars().first()
    if notif:
        notif.is_read = True
        await db.commit()
    return {"message": "Уведомление прочитано"}