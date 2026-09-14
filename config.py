import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
_admin_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_str.split(",") if x.strip()]

# Данные курса
COURSE_NAME = "Курс подготовки к экзамену ПДД"
COURSE_PRICE = 1990
PREMIUM_PRICE = 2990

# Ссылки
CHANNEL_LINK = "https://t.me/your_course_channel"
SUPPORT_LINK = "https://t.me/your_support_bot"

# Настройки напоминаний
REMINDER_DAYS = 7  # Через сколько дней напоминать