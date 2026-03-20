import argparse
import os
import sys
import json
from typing import Any, Dict, Optional

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# В окружении пользователя может быть прокси для requests.
# Для локального API (127.0.0.1) прокси может ломать запросы (503).
SESSION = requests.Session()
SESSION.trust_env = False


class ApiError(RuntimeError):
    pass


def _pretty_json(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)


def api_request(
    *,
    base_url: str,
    method: str,
    path: str,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
) -> Any:
    url = base_url.rstrip("/") + path

    headers: Dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_exc: Optional[BaseException] = None
    for attempt in range(1, 6):
        try:
            resp = SESSION.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=30,
            )
        except requests.RequestException as e:
            last_exc = e
            if attempt >= 5:
                raise ApiError(f"Network error after retries calling {method.upper()} {url}: {e}")
            continue

        if resp.status_code == 503 and attempt < 5:
            # Uvicorn --reload может на короткое время делать приложение недоступным.
            import time

            sleep_s = 1 * (2 ** (attempt - 1))
            print(f"[WARN] 503 на {method.upper()} {path}, retry через {sleep_s}s (попытка {attempt}/5)")
            time.sleep(sleep_s)
            continue

        content_type = resp.headers.get("content-type", "")
        body_text = resp.text

        if not resp.ok:
            # Пытаемся распарсить ответ как JSON, чтобы показать причину.
            try:
                body = resp.json()
                body_text = _pretty_json(body)
            except Exception:
                pass
            raise ApiError(f"[HTTP {resp.status_code}] {method.upper()} {url}\nResponse:\n{body_text}")

        if "application/json" in content_type.lower():
            try:
                return resp.json()
            except Exception:
                return body_text
        return body_text
    # Теоретически сюда не должны попасть, но оставим понятную ошибку.
    if last_exc:
        raise ApiError(f"Request failed for {method.upper()} {url}: {last_exc}")
    raise ApiError(f"Request failed for {method.upper()} {url}")


def register_and_login(base_url: str, *, email: str, role: str, password: str) -> str:
    # По требованию: регистрируем, затем логинимся.
    reg_payload = {"email": email, "password": password, "name": role, "role": role}
    try:
        api_request(base_url=base_url, method="POST", path="/users/register", json_body=reg_payload)
        print(f"[OK] Зарегистрирован: {email} ({role})")
    except ApiError as e:
        # На случай, если пользователь уже существует — пробуем логин.
        if "Этот email уже зарегистрирован" in str(e):
            print(f"[WARN] Пользователь уже существует, идем логиниться: {email}")
        else:
            raise

    login_payload = {"email": email, "password": password}
    login_resp = api_request(base_url=base_url, method="POST", path="/users/login", json_body=login_payload)
    token = login_resp.get("access_token")
    if not token:
        raise ApiError(f"Не удалось получить access_token после логина для {email}: {login_resp}")
    print(f"[OK] Логин: {email}")
    return token


def get_order_status(base_url: str, order_id: int) -> Optional[str]:
    orders = api_request(base_url=base_url, method="GET", path="/orders/")
    for o in orders:
        if int(o.get("id")) == int(order_id):
            return o.get("status")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Happy-path тест сценарий API Биржи 1С")
    parser.add_argument("--base-url", default=os.environ.get("API_BASE_URL", DEFAULT_BASE_URL))
    args = parser.parse_args()
    base_url: str = args.base_url

    password = "string"
    customer_email = "customer@test.com"
    worker_email = "worker@test.com"
    order_title = "Доработка 1С:УТ"

    print(f"Base URL: {base_url}")

    try:
        # Step 1: registration + login
        print("[STEP 1] Регистрация и логин")
        customer_token = register_and_login(base_url, email=customer_email, role="customer", password=password)
        worker_token = register_and_login(base_url, email=worker_email, role="worker", password=password)

        # Step 2: customer top-up
        print("[STEP 2] Пополнение баланса заказчика до 15000 руб")
        # Если БД не очищена, баланс может быть не 0.
        # У нас нет endpoint'а для получения профиля/баланса, поэтому калибруем пополнение:
        # делаем микротоп-ап на 1 руб, вычисляем текущий balance и докидываем ровно до 15000.
        probe_amount = 0.01
        probe_resp = api_request(
            base_url=base_url,
            method="POST",
            path="/users/top-up",
            token=customer_token,
            json_body={"amount": probe_amount},
        )
        probe_balance = float(probe_resp.get("balance"))
        current_balance = probe_balance - probe_amount

        target_balance = 15000.0
        if current_balance > target_balance:
            print(
                f"[WARN] Текущий balance уже выше target ({current_balance} > {target_balance}). "
                f"Уменьшить баланс API не позволяет — продолжаем, но проверку делаем >= target."
            )
            final_resp = probe_resp
            final_balance = float(final_resp.get("balance"))
            if final_balance < target_balance:
                raise ApiError(f"balance после probe ниже target: {final_balance}")
            print(f"[OK] Баланс заказчика: {final_balance}")
        else:
            # После probe баланс вырос на probe_amount. Чтобы итог был target_balance,
            # нужно пополнить на (target - balance_after_probe).
            needed = target_balance - probe_balance
            if needed > 0:
                final_resp = api_request(
                    base_url=base_url,
                    method="POST",
                    path="/users/top-up",
                    token=customer_token,
                    json_body={"amount": needed},
                )
            else:
                final_resp = probe_resp

            final_balance = float(final_resp.get("balance"))
            # Если probe немного перепрыгнул target, добиться точного равенства невозможно.
            if final_balance + 1e-6 < target_balance:
                raise ApiError(f"Ожидали balance>=15000, получили: {final_balance}")

        if current_balance <= target_balance:
            print(f"[OK] Баланс заказчика: {final_balance} (было ~{current_balance})")

        # Step 3: create order
        print("[STEP 3] Создание заказа")
        order_payload = {
            "title": order_title,
            "config_type": "УТ",
            "description": "Нужно настроить обмен",
            "budget": 10000,
        }
        order_resp = api_request(
            base_url=base_url,
            method="POST",
            path="/orders/",
            token=customer_token,
            json_body=order_payload,
        )
        order_id = order_resp.get("id")
        if not order_id:
            raise ApiError(f"Не получили order_id из ответа create_order: {order_resp}")
        print(f"[OK] Шаг 3: Заказ создан, ID: {order_id}")

        # Step 4: bid
        print("[STEP 4] Отклик на заказ")
        bid_payload = {"price": 9000, "comment": "Сделаю за 2 дня"}
        bid_resp = api_request(
            base_url=base_url,
            method="POST",
            path=f"/bids/{order_id}",
            token=worker_token,
            json_body=bid_payload,
        )
        bid_id = bid_resp.get("id")
        if not bid_id:
            raise ApiError(f"Не получили bid_id из ответа create_bid: {bid_resp}")
        print(f"[OK] Шаг 4: Отклик создан, ID: {bid_id}")

        # Step 5: accept bid
        print("[STEP 5] Выбор исполнителя (accept)")
        accept_resp = api_request(
            base_url=base_url,
            method="POST",
            path=f"/orders/{order_id}/accept/{bid_id}",
            token=customer_token,
        )
        order_status = accept_resp.get("order_status")
        if order_status != "in_progress":
            raise ApiError(f"Ожидали order_status=='in_progress', получили: {order_status}\n{accept_resp}")
        # Проверим статус заказа через /orders/
        actual_status = get_order_status(base_url, int(order_id))
        if actual_status != "in_progress":
            raise ApiError(f"GET /orders/ показал статус {actual_status}, ожидали in_progress")
        print("[OK] Шаг 5: Заказ принят, статус in_progress")

        # Step 6: complete
        print("[STEP 6] Завершение заказа (complete)")
        complete_resp = api_request(
            base_url=base_url,
            method="POST",
            path=f"/orders/{order_id}/complete",
            token=customer_token,
        )
        # Проверим статус заказа через /orders/
        actual_status_after = get_order_status(base_url, int(order_id))
        if actual_status_after != "closed":
            raise ApiError(f"Ожидали статус заказа 'closed' после complete, получили: {actual_status_after}")
        print("[OK] Шаг 6: Заказ закрыт (closed)")

        # Step 7: notifications for worker
        print("[STEP 7] Проверка уведомлений исполнителя")
        notifs = api_request(base_url=base_url, method="GET", path="/notifications/", token=worker_token)
        if not isinstance(notifs, list) or not notifs:
            raise ApiError(f"Ожидали непустой список уведомлений, получили: {notifs}")

        success_messages = [
            n.get("message", "") for n in notifs
            if isinstance(n, dict) and order_title in n.get("message", "") and ("успешно завершен" in n.get("message", ""))  # noqa: E501
        ]
        if not success_messages:
            raise ApiError(
                f"Не нашли уведомление об успешном завершении по заказу '{order_title}'. Уведомления:\n{_pretty_json(notifs)}"
            )

        worker_new_balance = complete_resp.get("worker_new_balance")
        if worker_new_balance is not None:
            if float(worker_new_balance) != 10000:
                print(f"[WARN] worker_new_balance != 10000 (опционально). Получили: {worker_new_balance}")

        print("[OK] Шаг 7: Уведомление найдено. Happy Path прошел успешно.")

        return 0
    except Exception as e:
        print("[FAIL] Сценарий остановлен из-за ошибки:")
        print(str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

