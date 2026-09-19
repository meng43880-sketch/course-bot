from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import MINI_APP_URL

# ===== МИНИ-АПП =====
def open_course_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Открыть курс", web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/account"))],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_main")]
    ])

def buy_course_keyboard(tariff=None):
    url = f"{MINI_APP_URL}#/paywall"
    if tariff:
        url += f"?tariff={tariff}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить в мини‑аппе", web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/account"))],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_main")]
    ])

def account_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Открыть личный кабинет", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/account"))],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_main")]
    ])

# ===== ГЛАВНОЕ МЕНЮ =====
def main_menu_keyboard(is_paid=False):
    if is_paid:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Открыть курс", web_app=WebAppInfo(url=MINI_APP_URL))],
            [InlineKeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/account"))],
            [InlineKeyboardButton(text="🧾 Моя покупка", callback_data="my_purchase")],
            [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="❓ Вопросы", callback_data="faq")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Купить доступ к курсу", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/paywall"))],
            [InlineKeyboardButton(text="👤 Личный кабинет", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/account"))],
            [InlineKeyboardButton(text="📚 О курсе", callback_data="about_course")],
            [InlineKeyboardButton(text="🎁 Бесплатно", callback_data="free_material")],
            [InlineKeyboardButton(text="❓ Вопросы", callback_data="faq")]
        ])

# ===== О КУРСЕ =====
def about_course_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Купить доступ", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/paywall"))],
        [InlineKeyboardButton(text="🎁 Посмотреть пример", callback_data="free_example")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ===== БЕСПЛАТНЫЙ МАТЕРИАЛ =====
def free_material_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Получить бесплатный разбор", callback_data="get_free_material")],
        [InlineKeyboardButton(text="📚 О курсе", callback_data="about_course")],
        [InlineKeyboardButton(text="🚀 Купить доступ", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/paywall"))],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def after_free_material_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Перейти к полному курсу", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/paywall"))],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="free_material")]
    ])

# ===== ТАРИФЫ =====
def tariffs_keyboard(standard_price, premium_price):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔥 Стандарт — {standard_price} ₽", callback_data="tariff_standard")],
        [InlineKeyboardButton(text=f"💎 Премиум — {premium_price} ₽", callback_data="tariff_premium")],
        [InlineKeyboardButton(text="📚 Что входит?", callback_data="whats_included")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def tariff_selected_keyboard(tariff, price):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить {price} ₽", web_app=WebAppInfo(url=f"{MINI_APP_URL}#/paywall?tariff={tariff}"))],
        [InlineKeyboardButton(text="⬅️ Выбрать другой тариф", callback_data="tariffs")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ===== ОПЛАТА =====
def payment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="go_payment")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")]
    ])

def payment_check_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_tariff")]
    ])

def payment_success_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Получить доступ", callback_data="get_access_link")]
    ])

# ===== ДОСТУП =====
def access_link_keyboard(channel_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти в закрытый канал", url=channel_link)]
    ])

def after_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Открыть курс", callback_data="open_course")],
        [InlineKeyboardButton(text="👤 Мой доступ", callback_data="my_access")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")]
    ])

# ===== МОЙ ДОСТУП =====
def my_access_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Войти в курс", callback_data="get_access_link")],
        [InlineKeyboardButton(text="🧾 Моя покупка", callback_data="my_purchase")],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def restore_access_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Восстановить доступ", callback_data="restore_access")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="my_access")]
    ])

# ===== МОЯ ПОКУПКА =====
def my_purchase_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Получить чек", callback_data="get_check")],
        [InlineKeyboardButton(text="👤 Мой доступ", callback_data="my_access")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ===== FAQ =====
def faq_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Сколько стоит?", callback_data="faq_price")],
        [InlineKeyboardButton(text="📚 Что входит?", callback_data="faq_whats_included")],
        [InlineKeyboardButton(text="⏱ Как долго действует доступ?", callback_data="faq_duration")],
        [InlineKeyboardButton(text="🔐 Как получить доступ?", callback_data="faq_how_to_get")],
        [InlineKeyboardButton(text="💳 Как оплатить?", callback_data="faq_payment")],
        [InlineKeyboardButton(text="↩️ Можно ли вернуть деньги?", callback_data="faq_refund")],
        [InlineKeyboardButton(text="💬 Задать свой вопрос", callback_data="support")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ===== ПОДДЕРЖКА =====
def support_keyboard(support_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать в поддержку", url=support_link)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ===== УНИВЕРСАЛЬНАЯ КНОПКА НАЗАД =====
def back_to_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

# ============================================
# ===== КЛАВИАТУРЫ АДМИНКИ =====
# ============================================

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="💰 Выдать доступ", callback_data="admin_give_access")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_mailing")],
        [InlineKeyboardButton(text="🔔 Напоминания", callback_data="admin_reminders")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")],
        [InlineKeyboardButton(text="📄 Экспорт CSV", callback_data="admin_export")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin_close")]
    ])

def admin_users_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список всех", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="✅ Список купивших", callback_data="admin_users_paid")],
        [InlineKeyboardButton(text="🔍 Найти пользователя", callback_data="admin_users_find")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])

def admin_settings_keyboard(standard_price, premium_price, course_name, channel_link, support_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💰 Цена Стандарт: {standard_price} ₽", callback_data="admin_set_standard")],
        [InlineKeyboardButton(text=f"💰 Цена Премиум: {premium_price} ₽", callback_data="admin_set_premium")],
        [InlineKeyboardButton(text=f"📝 Название курса", callback_data="admin_set_name")],
        [InlineKeyboardButton(text=f"🔗 Ссылка на канал", callback_data="admin_set_channel")],
        [InlineKeyboardButton(text=f"📞 Ссылка на поддержку", callback_data="admin_set_support")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])

def admin_mailing_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Всем пользователям", callback_data="admin_mailing_all")],
        [InlineKeyboardButton(text="✅ Только купившим", callback_data="admin_mailing_paid")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])

def admin_reminders_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Отправить напоминания сейчас", callback_data="admin_remind_now")],
        [InlineKeyboardButton(text="⏱ Настроить интервал", callback_data="admin_remind_interval")],
        [InlineKeyboardButton(text="🔄 Сбросить флаги напоминаний", callback_data="admin_remind_reset")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])

def back_to_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")]
    ])