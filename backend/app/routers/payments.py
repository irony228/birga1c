import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.auth import get_current_user
from app.database import get_db
from app.models import User, YooKassaPayment
from app.schemas import TopUpRequest, YooKassaTopUpResponse
from app.yookassa_client import create_payment, get_payment

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Payments", "ЮKassa"])


def _money_str(value: float) -> str:
    q = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(q, "f")


def _amounts_match(stored: float, yk_value: str) -> bool:
    try:
        yk_dec = Decimal(yk_value)
        st_dec = Decimal(str(stored)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return yk_dec == st_dec
    except (ValueError, ArithmeticError):
        return False


@router.post(
    "/payments/yookassa/top-up",
    response_model=YooKassaTopUpResponse,
)
async def yookassa_create_topup(
    body: TopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Платежи не настроены (YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY)",
        )
    amount = float(body.amount)
    if amount < 1.0:
        raise HTTPException(status_code=400, detail="Минимальная сумма пополнения 1 ₽")
    if amount > 1_000_000:
        raise HTTPException(status_code=400, detail="Слишком большая сумма")

    amount_str = _money_str(amount)
    idempotency_key = str(uuid.uuid4())
    return_url = f"{settings.public_frontend_url}/profile?yookassa=return"

    row = YooKassaPayment(
        user_id=current_user.id,
        amount=float(Decimal(amount_str)),
        idempotency_key=idempotency_key,
        status="pending",
    )
    db.add(row)
    await db.flush()
    try:
        yk = await create_payment(
            shop_id=settings.yookassa_shop_id,
            secret_key=settings.yookassa_secret_key,
            idempotence_key=idempotency_key,
            amount_value=amount_str,
            currency="RUB",
            return_url=return_url,
            description=f"Пополнение баланса, пользователь {current_user.id}",
            metadata={
                "user_id": str(current_user.id),
                "topup_id": str(row.id),
            },
        )
    except Exception as exc:
        await db.rollback()
        logger.exception("YooKassa create_payment failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Не удалось создать платёж в ЮKassa. Попробуйте позже.",
        ) from exc

    row.yookassa_payment_id = yk.get("id")
    await db.commit()

    confirmation = yk.get("confirmation") or {}
    url = confirmation.get("confirmation_url")
    if not url:
        raise HTTPException(status_code=502, detail="ЮKassa не вернула ссылку на оплату")

    return YooKassaTopUpResponse(confirmation_url=url, internal_payment_id=row.id)


@router.post("/webhooks/yookassa")
async def yookassa_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Уведомления ЮKassa: https://yookassa.ru/developers/using-api/webhooks"""
    try:
        body = await request.json()
    except Exception:
        return Response(status_code=200)

    event = body.get("event") or ""
    obj = body.get("object") or {}
    payment_id = obj.get("id")
    if not payment_id:
        return Response(status_code=200)

    if event == "payment.canceled":
        result = await db.execute(
            select(YooKassaPayment)
            .where(YooKassaPayment.yookassa_payment_id == payment_id)
            .with_for_update()
        )
        row = result.scalars().first()
        if row and row.status == "pending":
            row.status = "canceled"
            await db.commit()
        return Response(status_code=200)

    if event != "payment.succeeded":
        return Response(status_code=200)

    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        logger.error("YooKassa webhook: keys not configured")
        raise HTTPException(status_code=500, detail="not configured")

    try:
        remote = await get_payment(
            shop_id=settings.yookassa_shop_id,
            secret_key=settings.yookassa_secret_key,
            payment_id=payment_id,
        )
    except Exception as exc:
        logger.exception("YooKassa get_payment failed for webhook: %s", exc)
        raise HTTPException(status_code=500, detail="verify failed") from exc

    if remote.get("status") != "succeeded":
        return Response(status_code=200)

    amount_block = remote.get("amount") or {}
    yk_amount = amount_block.get("value")
    if yk_amount is None:
        return Response(status_code=200)

    meta = remote.get("metadata") or {}
    meta_topup = meta.get("topup_id")
    meta_user = meta.get("user_id")

    result = await db.execute(
        select(YooKassaPayment)
        .where(YooKassaPayment.yookassa_payment_id == payment_id)
        .with_for_update()
    )
    row = result.scalars().first()
    if not row:
        logger.warning("YooKassa webhook: unknown payment_id=%s", payment_id)
        return Response(status_code=200)

    if meta_topup and str(row.id) != str(meta_topup):
        logger.warning("YooKassa webhook: topup_id mismatch payment_id=%s", payment_id)
        return Response(status_code=200)
    if meta_user and str(row.user_id) != str(meta_user):
        logger.warning("YooKassa webhook: user_id mismatch payment_id=%s", payment_id)
        return Response(status_code=200)

    if not _amounts_match(row.amount, str(yk_amount)):
        logger.warning("YooKassa webhook: amount mismatch payment_id=%s", payment_id)
        return Response(status_code=200)

    if row.status == "succeeded":
        return Response(status_code=200)

    ures = await db.execute(select(User).where(User.id == row.user_id).with_for_update())
    user = ures.scalars().first()
    if not user:
        return Response(status_code=200)

    user.balance += row.amount
    row.status = "succeeded"
    await db.commit()
    return Response(status_code=200)
