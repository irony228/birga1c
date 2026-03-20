import base64
import json
from typing import Any

import httpx

YOOKASSA_API_BASE = "https://api.yookassa.ru/v3"


def _basic_auth(shop_id: str, secret_key: str) -> str:
    token = base64.b64encode(f"{shop_id}:{secret_key}".encode()).decode()
    return f"Basic {token}"


async def create_payment(
    *,
    shop_id: str,
    secret_key: str,
    idempotence_key: str,
    amount_value: str,
    currency: str,
    return_url: str,
    description: str,
    metadata: dict[str, str],
    capture: bool = True,
) -> dict[str, Any]:
    payload = {
        "amount": {"value": amount_value, "currency": currency},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": capture,
        "description": description,
        "metadata": metadata,
    }
    headers = {
        "Authorization": _basic_auth(shop_id, secret_key),
        "Content-Type": "application/json",
        "Idempotence-Key": idempotence_key,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{YOOKASSA_API_BASE}/payments", headers=headers, content=json.dumps(payload))
        r.raise_for_status()
        return r.json()


async def get_payment(*, shop_id: str, secret_key: str, payment_id: str) -> dict[str, Any]:
    headers = {"Authorization": _basic_auth(shop_id, secret_key)}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(f"{YOOKASSA_API_BASE}/payments/{payment_id}", headers=headers)
        r.raise_for_status()
        return r.json()
