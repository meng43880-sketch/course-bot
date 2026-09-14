import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from handlers import router, start_reminder_scheduler

PORT = int(os.getenv("PORT", 10000))

# HTTP сервер для health-check (чтобы UptimeRobot не давал Render-у усыпить бота)
async def handle_health(request):
    return web.Response(text="ok")

async def run_http_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print(f"🌐 HTTP health-check server запущен на порту {PORT}")

async def main():
    # Создаём базу данных
    init_db()
    
    # Прокси для обхода блокировки (только если задан через env PROXY_API)
    proxy_api = os.getenv("PROXY_API")
    if proxy_api:
        try:
            api_server = TelegramAPIServer.from_base(proxy_api)
            session = AiohttpSession(api=api_server)
            bot = Bot(token=BOT_TOKEN, session=session)
        except Exception:
            bot = Bot(token=BOT_TOKEN)
    else:
        bot = Bot(token=BOT_TOKEN)
    
    dp = Dispatcher()
    dp.include_router(router)
    
    # Запускаем HTTP сервер и фоновую задачу для напоминаний
    await run_http_server()
    asyncio.create_task(start_reminder_scheduler(bot))
    
    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен!")
    print(f"📊 Напоминания будут отправляться каждые 24 часа")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())