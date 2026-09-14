import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from config import BOT_TOKEN
from database import init_db
from handlers import router, start_reminder_scheduler

# Прокси для обхода блокировки (если нужно)
PROXY_API = "https://telegram-api-proxy.vercel.app"

async def main():
    # Создаём базу данных
    init_db()
    
    # Настраиваем бота
    try:
        api_server = TelegramAPIServer.from_base(PROXY_API)
        session = AiohttpSession(api=api_server)
        bot = Bot(token=BOT_TOKEN, session=session)
    except:
        bot = Bot(token=BOT_TOKEN)
    
    dp = Dispatcher()
    dp.include_router(router)
    
    # Запускаем фоновую задачу для напоминаний
    asyncio.create_task(start_reminder_scheduler(bot))
    
    # Запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен!")
    print(f"📊 Напоминания будут отправляться каждые 24 часа")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())