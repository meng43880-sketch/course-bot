"""
HTTP API для Telegram Mini App (оплата-заглушка + проверка доступа).

Запускается в том же aiohttp-процессе, что и health-check сервер.
"""
import hashlib
import hmac
import json
import os
import urllib.parse

from aiohttp import web
from aiohttp.web import middleware

from config import BOT_TOKEN
from database import (
    add_user,
    get_purchase_date,
    get_setting,
    get_user,
    get_user_price,
    get_user_tariff,
    is_paid,
    mark_paid,
    update_profile,
)

# В dev-режиме (локально) разрешаем определять пользователя по user_id без initData.
# В продакшене обязательно установите API_ALLOW_INSECURE=false.
ALLOW_INSECURE = os.getenv("ALLOW_INSECURE", "true").lower() in ("1", "true", "yes")


def _verify_init_data(init_data: str):
    """Проверяем подпись Telegram WebApp initData и возвращаем user, либо None."""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None

    received_hash = parsed.get("hash")
    if not received_hash:
        return None
    parsed.pop("hash", None)

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calc, received_hash):
        return None

    try:
        user = json.loads(parsed.get("user", "{}"))
    except (ValueError, TypeError):
        return None

    if not isinstance(user, dict) or "id" not in user:
        return None

    user["id"] = int(user["id"])
    return user


def _resolve_user(body: dict):
    """Определяем Telegram-пользователя по initData (или user_id в dev-режиме)."""
    init_data = body.get("initData") or body.get("init_data") or ""
    if init_data:
        user = _verify_init_data(init_data)
        if not user:
            return None, "Неверная подпись initData"
        return user, None

    user_id = body.get("user_id") or body.get("userId")
    if user_id is None:
        return None, "Не передан initData или user_id"
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None, "user_id должен быть числом"

    if not ALLOW_INSECURE:
        return None, "Требуется initData (режим безопасности включён)"
    return {"id": user_id}, None


def _user_info(user_id: int):
    add_user(user_id)

    tariff = get_user_tariff(user_id)
    return {
        "user_id": user_id,
        "is_paid": bool(is_paid(user_id)),
        "tariff": tariff,
        "price": get_user_price(user_id),
        "purchase_date": get_purchase_date(user_id),
        "course_name": get_setting("course_name") or "Курс подготовки к экзамену ПДД",
        "standard_price": int(get_setting("course_price") or 1990),
        "premium_price": int(get_setting("premium_price") or 2990),
        "support_link": get_setting("support_link") or "https://t.me/your_support_bot",
    }


async def handle_me(request: web.Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    user, error = _resolve_user(body)
    if error:
        return web.json_response({"error": error}, status=401)

    return web.json_response(_user_info(user["id"]))


async def handle_pay(request: web.Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    user, error = _resolve_user(body)
    if error:
        return web.json_response({"error": error}, status=401)

    user_id = user["id"]

    if is_paid(user_id):
        return web.json_response(_user_info(user_id))

    tariff = (body.get("tariff") or "standard").lower()
    if tariff not in ("standard", "premium"):
        tariff = "standard"

    price = int(get_setting("course_price") or 1990) if tariff == "standard" else int(get_setting("premium_price") or 2990)
    mark_paid(user_id, tariff, price)

    return web.json_response({"ok": True, **_user_info(user_id)})


async def handle_refresh(request: web.Request):
    """Обновляем имя/username пользователя (небольшая служебная ручка)."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    user, error = _resolve_user(body)
    if error:
        return web.json_response({"error": error}, status=401)

    update_profile(user["id"], user.get("username"), user.get("first_name"))
    return web.json_response({"ok": True})


async def handle_health(request: web.Request):
    return web.json_response({"status": "ok"})


@middleware
async def _cors_middleware(request, handler):
    if request.method == "OPTIONS":
        return web.Response(status=204, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        })
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def create_web_app() -> web.Application:
    """Собирает aiohttp-приложение: health-check + API для мини-аппа."""
    app = web.Application(middlewares=[_cors_middleware])
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    app.router.add_post("/api/me", handle_me)
    app.router.add_post("/api/pay", handle_pay)
    app.router.add_post("/api/refresh", handle_refresh)
    return app