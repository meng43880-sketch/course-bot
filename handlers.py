from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from config import ADMIN_IDS, REMINDER_DAYS
from database import *
from keyboards import *
from states import CourseStates

import io
import csv
import asyncio

router = Router()

# ============================================
# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
# ============================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_course_description():
    course_name = get_setting("course_name") or "Курс подготовки к экзамену ПДД"
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"
    
    return (
        f"📚 **О {course_name}**\n\n"
        "✅ **Что входит:**\n"
        "• 50+ видеоуроков\n"
        "• 1000+ тестовых заданий\n"
        "• Разбор реальных билетов\n"
        "• Советы от инструкторов\n\n"
        "📊 **Формат:**\n"
        "• Закрытый Telegram-канал\n"
        "• Доступ 24/7\n"
        "• Обновления материалов\n\n"
        f"💰 **Стоимость:**\n"
        f"• Стандарт: {standard_price} ₽\n"
        f"• Премиум: {premium_price} ₽\n\n"
        "🔐 **Доступ:**\n"
        "• Бессрочный после оплаты"
    )

def get_tariff_description(tariff):
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"
    if tariff == "premium":
        return (
            f"💎 **Тариф «Премиум» — {premium_price} ₽**\n\n"
            "✅ Всё из тарифа «Стандарт»\n"
            "✅ Личный разбор ошибок\n"
            "✅ Приоритетная поддержка\n"
            "✅ Экзамен-тренажёр с ответами\n\n"
            "Доступ навсегда после оплаты."
        )
    return (
        f"🔥 **Тариф «Стандарт» — {standard_price} ₽**\n\n"
        "✅ 50+ видеоуроков\n"
        "✅ 1000+ тестовых заданий\n"
        "✅ Разбор реальных билетов\n"
        "✅ Доступ навсегда\n\n"
        "Оплата и доступ — в мини‑аппе."
    )

def get_tariff_name(tariff):
    return "Премиум" if tariff == "premium" else "Стандарт"

def get_faq_answers():
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"

    return {
        "faq_price": f"💰 **Стоимость:**\n• Стандарт: {standard_price} ₽\n• Премиум: {premium_price} ₽",
        "faq_whats_included": "📚 **Что входит:**\n• 50+ видеоуроков\n• 1000+ тестов\n• Разбор билетов\n• Советы инструкторов",
        "faq_duration": "⏱ **Доступ:**\nБессрочный после оплаты",
        "faq_how_to_get": "🔐 **Как получить доступ:**\n1. Выбери тариф\n2. Оплати\n3. Получи ссылку на канал",
        "faq_payment": "💳 **Оплата:**\n• СБП\n• Банковская карта\n• Криптовалюта",
        "faq_refund": "↩️ **Возврат:**\nВ течение 14 дней, если курс не подошел"
    }

# ============================================
# ===== ПОЛЬЗОВАТЕЛЬСКАЯ ЧАСТЬ =====
# ============================================

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)
    if not user:
        add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name
        )
    
    paid = is_paid(message.from_user.id)
    await state.set_state(CourseStates.main_menu)
    await message.answer(
        f"🚗 **{get_setting('course_name') or 'Курс ПДД'}**\n\n"
        "Привет! 👋\n"
        "Всё необходимое для подготовки — в одном месте.\n\n"
        "Курс доступен после оплаты — нажми кнопку ниже, чтобы выбрать тариф в мини‑аппе.",
        reply_markup=main_menu_keyboard(paid),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    paid = is_paid(callback.from_user.id)
    await state.set_state(CourseStates.main_menu)
    await callback.message.edit_text(
        f"🚗 **{get_setting('course_name') or 'Курс ПДД'}**\n\n"
        "Всё необходимое для подготовки — в одном месте.",
        reply_markup=main_menu_keyboard(paid),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "about_course")
async def about_course(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CourseStates.about_course)
    await callback.message.edit_text(
        get_course_description(),
        reply_markup=about_course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "free_material")
async def free_material(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CourseStates.free_material)
    await callback.message.edit_text(
        "🎁 **Бесплатный материал**\n\n"
        "Попробуй формат обучения перед покупкой.",
        reply_markup=free_material_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "get_free_material")
async def get_free_material(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 **Бесплатный разбор**\n\n"
        "Вот один из уроков курса:\n"
        "📹 [Видеоурок: Перекрёстки]\n\n"
        "✅ Тест: 5 вопросов\n\n"
        "Понравился формат? Приобретай полный курс!",
        reply_markup=after_free_material_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "free_example")
async def free_example(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 **Бесплатный разбор**\n\n"
        "Вот один из уроков курса:\n"
        "📹 [Видеоурок: Перекрёстки]\n\n"
        "✅ Тест: 5 вопросов\n\n"
        "Понравился формат? Приобретай полный курс!",
        reply_markup=after_free_material_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "get_access")
async def get_access(callback: types.CallbackQuery, state: FSMContext):
    if is_paid(callback.from_user.id):
        await callback.answer("У вас уже есть доступ к курсу! ✅", show_alert=True)
        return
    
    await state.set_state(CourseStates.tariffs)
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"
    
    await callback.message.edit_text(
        "🔥 **Выбери вариант доступа:**\n\n"
        f"🔥 Стандарт — {standard_price} ₽\n"
        f"💎 Премиум — {premium_price} ₽",
        reply_markup=tariffs_keyboard(standard_price, premium_price),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "whats_included")
async def whats_included(callback: types.CallbackQuery, state: FSMContext):
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"
    
    await callback.message.edit_text(
        get_course_description(),
        reply_markup=tariffs_keyboard(standard_price, premium_price),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tariff_"))
async def select_tariff(callback: types.CallbackQuery, state: FSMContext):
    tariff = callback.data.replace("tariff_", "")
    standard_price = int(get_setting("course_price") or 1990)
    premium_price = int(get_setting("premium_price") or 2990)
    price = standard_price if tariff == "standard" else premium_price
    
    await state.update_data(tariff=tariff, price=price)
    await state.set_state(CourseStates.tariff_selected)
    
    await callback.message.edit_text(
        get_tariff_description(tariff),
        reply_markup=tariff_selected_keyboard(tariff, price),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "tariffs")
async def tariffs_list(callback: types.CallbackQuery, state: FSMContext):
    if is_paid(callback.from_user.id):
        await callback.answer("У вас уже есть доступ к курсу! ✅", show_alert=True)
        return

    await state.set_state(CourseStates.tariffs)
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"

    await callback.message.edit_text(
        "🔥 **Выбери вариант доступа:**\n\n"
        f"🔥 Стандарт — {standard_price} ₽\n"
        f"💎 Премиум — {premium_price} ₽",
        reply_markup=tariffs_keyboard(standard_price, premium_price),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ ОПЛАТА ЧЕРЕЗ МИНИ-АПП ============

@router.callback_query(F.data.startswith("pay_"))
async def pay_via_mini_app(callback: types.CallbackQuery, state: FSMContext):
    """Старый callback на всякий случай: перенаправляем в мини-апп."""
    if is_paid(callback.from_user.id):
        await callback.answer("У вас уже есть доступ к курсу! ✅", show_alert=True)
        return

    tariff = callback.data.replace("pay_", "")
    price = int(get_setting("course_price") or 1990) if tariff == "standard" else int(get_setting("premium_price") or 2990)
    await state.set_state(CourseStates.payment)
    await callback.message.edit_text(
        f"💳 **Оплата через мини‑апп**\n\n"
        f"Тариф: {get_tariff_name(tariff)}\n"
        f"Сумма: {price} ₽\n\n"
        "Нажми кнопку ниже — откроется мини‑апп с оплатой.",
        reply_markup=buy_course_keyboard(tariff),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ FAQ ============

@router.callback_query(F.data == "faq")
async def faq(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CourseStates.faq)
    await callback.message.edit_text(
        "❓ **Частые вопросы**\n\nВыбери интересующий вопрос:",
        reply_markup=faq_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def faq_item(callback: types.CallbackQuery, state: FSMContext):
    answer = get_faq_answers().get(callback.data)
    if not answer:
        await callback.answer()
        return
    await callback.message.edit_text(
        answer,
        reply_markup=faq_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ ПОДДЕРЖКА ============

@router.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(CourseStates.support)
    support_link = get_setting("support_link") or "https://t.me/your_support_bot"
    await callback.message.edit_text(
        "💬 **Поддержка**\n\n"
        "Если возникли вопросы — напиши нам, поможем!",
        reply_markup=support_keyboard(support_link),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ ОТКРЫТЬ КУРС ============

@router.callback_query(F.data == "open_course")
async def open_course(callback: types.CallbackQuery, state: FSMContext):
    if not is_paid(callback.from_user.id):
        await callback.answer("Доступ открывается после оплаты 😉", show_alert=True)
        return

    await state.set_state(CourseStates.access_granted)
    await callback.message.edit_text(
        "📚 **Твой курс**\n\n"
        "Кнопка ниже откроет обучающий мини‑апп со всеми материалами.",
        reply_markup=open_course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ МОЙ ДОСТУП ============

@router.callback_query(F.data == "my_access")
async def my_access(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if not is_paid(user_id):
        await state.set_state(CourseStates.tariffs)
        await callback.message.edit_text(
            "🔒 **У тебя пока нет доступа к курсу.**\n\n"
            "Курс открывается сразу после оплаты в мини‑аппе.\n\n"
            "Выбери тариф и оплати — доступ появится мгновенно.",
            reply_markup=buy_course_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    await state.set_state(CourseStates.my_access)
    await callback.message.edit_text(
        "👤 **Мой доступ**\n\n"
        "✅ Доступ к курсу активен!\n"
        "Кнопка ниже откроет мини‑апп с курсом.",
        reply_markup=open_course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "restore_access")
async def restore_access(callback: types.CallbackQuery, state: FSMContext):
    if not is_paid(callback.from_user.id):
        await callback.answer("Сначала оплати курс 😉", show_alert=True)
        return
    await callback.message.edit_text(
        "✅ **Доступ активен** — твой курс ниже 👇",
        reply_markup=open_course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "get_access_link")
async def get_access_link(callback: types.CallbackQuery, state: FSMContext):
    if not is_paid(callback.from_user.id):
        await callback.answer("Сначала оплати курс 😉", show_alert=True)
        return
    await state.set_state(CourseStates.access_granted)
    await callback.message.edit_text(
        "🔐 **Вот твой курс**\n\nНажми кнопку, чтобы открыть обучающий мини‑апп.",
        reply_markup=open_course_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ МОЯ ПОКУПКА ============

@router.callback_query(F.data == "my_purchase")
async def my_purchase(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    if not is_paid(user_id):
        await state.set_state(CourseStates.tariffs)
        await callback.message.edit_text(
            "🧾 **Покупок пока нет.**\n\n"
            "Оплати курс в мини‑аппе, и здесь появится вся информация о покупке.",
            reply_markup=buy_course_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    await state.set_state(CourseStates.my_purchase)
    tariff = get_user_tariff(user_id)
    price = get_user_price(user_id)
    purchase_date = get_purchase_date(user_id)
    tariff_name = get_tariff_name(tariff or "standard")

    await callback.message.edit_text(
        "🧾 **Моя покупка**\n\n"
        f"💎 Тариф: {tariff_name}\n"
        f"💰 Сумма: {price} ₽\n"
        f"📅 Дата: {purchase_date or 'неизвестна'}\n"
        f"🎁 Статус: оплачено ✅",
        reply_markup=my_purchase_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "get_check")
async def get_check(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not is_paid(user_id):
        await callback.answer("Сначала оплати курс 😉", show_alert=True)
        return

    tariff = get_user_tariff(user_id)
    price = get_user_price(user_id)
    purchase_date = get_purchase_date(user_id)

    await callback.message.edit_text(
        "🧾 **Чек об оплате**\n\n"
        "Учебный курс «ПДД 2026»\n"
        f"Тариф: {get_tariff_name(tariff or 'standard')}\n"
        f"Сумма: {price} ₽\n"
        f"Дата оплаты: {purchase_date or 'неизвестна'}\n"
        f"Способ оплаты: мини‑апп\n\n"
        "_Это демо-чек. При подключении реальной оплаты здесь будет фискальный чек._",
        reply_markup=my_purchase_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ... (остальная пользовательская часть, включая оплату - как в предыдущей версии)

# ============================================
# ===== НАПОМИНАНИЯ =====
# ============================================

async def send_reminders(bot):
    """Отправляет напоминания пользователям, которые не заходили больше REMINDER_DAYS дней"""
    users = get_inactive_users(REMINDER_DAYS)
    
    if not users:
        return
    
    channel_link = get_setting("channel_link") or "https://t.me/your_course_channel"
    course_name = get_setting("course_name") or "Курс ПДД"
    
    text = (
        f"🔔 **Напоминание о курсе {course_name}**\n\n"
        f"Ты давно не заходил в наш закрытый канал!\n"
        f"Там появились новые материалы и обновления.\n\n"
        f"[👉 Перейти в канал]({channel_link})\n\n"
        f"Не откладывай обучение! 🚀"
    )
    
    for user in users:
        try:
            await bot.send_message(user[0], text, parse_mode="Markdown")
            set_reminded(user[0])
            await asyncio.sleep(0.5)  # Защита от флуда
        except Exception as e:
            print(f"Ошибка отправки напоминания {user[0]}: {e}")

async def start_reminder_scheduler(bot):
    """Запускает фоновую задачу для отправки напоминаний каждые 24 часа"""
    while True:
        try:
            await send_reminders(bot)
        except Exception as e:
            print(f"Ошибка в планировщике напоминаний: {e}")
        await asyncio.sleep(86400)  # Ждём 24 часа

# ============================================
# ===== АДМИНКА =====
# ============================================

@router.message(Command("admin"))
async def admin_panel(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ У вас нет доступа к этой команде.")
        return
    
    await state.set_state(CourseStates.admin)
    await message.answer(
        "👑 **Панель администратора**\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👑 **Панель администратора**\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await state.set_state(CourseStates.main_menu)
    paid = is_paid(callback.from_user.id)
    await callback.message.edit_text(
        f"🚗 **{get_setting('course_name') or 'Курс ПДД'}**\n\n"
        "Всё необходимое для подготовки — в одном месте.",
        reply_markup=main_menu_keyboard(paid),
        parse_mode="Markdown"
    )
    await callback.answer()

# ===== СТАТИСТИКА =====
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    stats = get_stats()
    conversion = round(stats["paid_users"] / stats["total_users"] * 100, 1) if stats["total_users"] > 0 else 0
    
    await callback.message.edit_text(
        "📊 **Статистика**\n\n"
        f"👤 Всего пользователей: {stats['total_users']}\n"
        f"✅ Купили курс: {stats['paid_users']}\n"
        f"📊 Конверсия: {conversion}%\n"
        f"🔐 В канале: {stats['in_channel_users']}\n"
        f"⚠️ Ни разу не заходили: {stats['never_visited']}\n"
        f"💰 Доход: {stats['total_income']} ₽",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ===== ПОЛЬЗОВАТЕЛИ =====
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 **Управление пользователями**\n\n"
        "Выберите действие:",
        reply_markup=admin_users_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    users = get_all_users()
    if not users:
        await callback.answer("Пользователей пока нет", show_alert=True)
        return
    
    text = "📋 **Список всех пользователей**\n\n"
    for user in users[:20]:
        status = "✅" if user[4] else "❌"
        in_ch = "🔐" if user[6] else "🚫"
        text += f"{status} {in_ch} {user[1] or user[0]} — {user[2] or 'Без имени'}\n"
    
    if len(users) > 20:
        text += f"\n... и ещё {len(users) - 20} пользователей"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_users_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_users_paid")
async def admin_users_paid(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    users = get_paid_users()
    if not users:
        await callback.answer("Купивших пока нет", show_alert=True)
        return
    
    text = "✅ **Список купивших курс**\n\n"
    for user in users[:20]:
        last_activity = user[5] or "Никогда"
        text += f"• {user[1] or user[0]} — {user[3] or 'Стандарт'} — {user[4] or 'дата неизвестна'}\n"
    
    if len(users) > 20:
        text += f"\n... и ещё {len(users) - 20} человек"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_users_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_users_find")
async def admin_users_find(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔍 **Поиск пользователя**\n\n"
        "Отправь ID пользователя (число) или его username (с @).\n"
        "Например: 123456789 или @username\n\n"
        "❌ Отмена: /cancel",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(CourseStates.admin_find_user)
    await callback.answer()

@router.message(StateFilter(CourseStates.admin_find_user))
async def admin_find_user_result(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    query = message.text.strip()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if query.startswith("@"):
        cur.execute("SELECT * FROM users WHERE username = ?", (query[1:],))
    else:
        try:
            user_id = int(query)
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        except ValueError:
            await message.answer("❌ Неверный формат. Введи ID (число) или username (с @).")
            return
    
    user = cur.fetchone()
    conn.close()
    
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return
    
    last_activity = user[8] or "Никогда"
    reminded = "✅ Да" if user[9] else "❌ Нет"
    
    await message.answer(
        "👤 **Найден пользователь**\n\n"
        f"ID: `{user[0]}`\n"
        f"Username: @{user[1] or 'Нет'}\n"
        f"Имя: {user[2] or 'Нет'}\n"
        f"Тариф: {user[3] or 'Не куплен'}\n"
        f"Оплачено: {'✅ Да' if user[4] else '❌ Нет'}\n"
        f"Цена: {user[5] or 0} ₽\n"
        f"Дата покупки: {user[6] or 'Нет'}\n"
        f"В канале: {'✅ Да' if user[7] else '❌ Нет'}\n"
        f"Последняя активность: {last_activity}\n"
        f"Напоминание отправлено: {reminded}",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )

# ===== ВЫДАТЬ ДОСТУП =====
@router.callback_query(F.data == "admin_give_access")
async def admin_give_access(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💰 **Выдача доступа вручную**\n\n"
        "Отправь ID пользователя (число), которому нужно выдать доступ.\n"
        "Например: 123456789\n\n"
        "❌ Отмена: /cancel",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(CourseStates.admin_give_access)
    await callback.answer()

@router.message(StateFilter(CourseStates.admin_give_access))
async def admin_give_access_process(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введи число (ID пользователя).")
        return
    
    if not get_user(user_id):
        await message.answer("❌ Пользователь с таким ID не найден.")
        return
    
    mark_paid(user_id, "standard", 0)
    await message.answer(f"✅ Доступ выдан пользователю {user_id}")
    await state.set_state(CourseStates.admin)

# ===== РАССЫЛКА =====
@router.callback_query(F.data == "admin_mailing")
async def admin_mailing(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📨 **Рассылка**\n\n"
        "Выбери кому отправить:",
        reply_markup=admin_mailing_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_mailing_"))
async def admin_mailing_get_text(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    target = callback.data.replace("admin_mailing_", "")
    await state.update_data(mailing_target=target)
    
    await callback.message.edit_text(
        "📝 **Отправь текст рассылки**\n\n"
        "Я разошлю его выбранной группе пользователей.\n"
        "Поддерживается Markdown.\n\n"
        "Также можно отправить:\n"
        "• Фото с подписью\n"
        "• Видео с подписью\n"
        "• Документ с подписью\n\n"
        "❌ Отмена: /cancel",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(CourseStates.admin_mailing)
    await callback.answer()

@router.message(StateFilter(CourseStates.admin_mailing))
async def admin_mailing_send(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    target = data.get("mailing_target")
    
    # Получаем пользователей
    if target == "all":
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()
        conn.close()
    elif target == "paid":
        users = get_paid_users()
        users = [(user[0],) for user in users]
    else:
        await message.answer("❌ Неизвестная группа.")
        return
    
    if not users:
        await message.answer("❌ Нет пользователей для рассылки.")
        return
    
    sent = 0
    failed = 0
    
    # Отправляем сообщение всем
    for user in users:
        try:
            if message.photo:
                await message.bot.send_photo(
                    user[0],
                    message.photo[-1].file_id,
                    caption=message.caption,
                    parse_mode="Markdown" if message.caption else None
                )
            elif message.video:
                await message.bot.send_video(
                    user[0],
                    message.video.file_id,
                    caption=message.caption,
                    parse_mode="Markdown" if message.caption else None
                )
            elif message.document:
                await message.bot.send_document(
                    user[0],
                    message.document.file_id,
                    caption=message.caption,
                    parse_mode="Markdown" if message.caption else None
                )
            else:
                await message.bot.send_message(
                    user[0],
                    message.text,
                    parse_mode="Markdown"
                )
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.5)  # Защита от флуда
    
    await message.answer(
        f"✅ Рассылка завершена!\n"
        f"Отправлено: {sent}\n"
        f"Не доставлено: {failed}\n"
        f"Всего: {len(users)}"
    )
    await state.set_state(CourseStates.admin)

# ===== НАПОМИНАНИЯ (АДМИНКА) =====
@router.callback_query(F.data == "admin_reminders")
async def admin_reminders(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    inactive_count = len(get_inactive_users(REMINDER_DAYS))
    
    await callback.message.edit_text(
        "🔔 **Управление напоминаниями**\n\n"
        f"📊 Пользователей, не заходивших {REMINDER_DAYS} дней: **{inactive_count}**\n\n"
        "Что хочешь сделать?",
        reply_markup=admin_reminders_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_remind_now")
async def admin_remind_now(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.answer("🔄 Отправляю напоминания...")
    
    users = get_inactive_users(REMINDER_DAYS)
    
    if not users:
        await callback.message.edit_text(
            "✅ Нет пользователей, которым нужно отправить напоминание.",
            reply_markup=admin_reminders_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    channel_link = get_setting("channel_link") or "https://t.me/your_course_channel"
    course_name = get_setting("course_name") or "Курс ПДД"
    
    text = (
        f"🔔 **Напоминание о курсе {course_name}**\n\n"
        f"Ты давно не заходил в наш закрытый канал!\n"
        f"Там появились новые материалы и обновления.\n\n"
        f"[👉 Перейти в канал]({channel_link})\n\n"
        f"Не откладывай обучение! 🚀"
    )
    
    sent = 0
    for user in users:
        try:
            await callback.bot.send_message(user[0], text, parse_mode="Markdown")
            set_reminded(user[0])
            sent += 1
            await asyncio.sleep(0.5)
        except:
            pass
    
    await callback.message.edit_text(
        f"✅ Отправлено {sent} напоминаний из {len(users)}.",
        reply_markup=admin_reminders_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_remind_interval")
async def admin_remind_interval(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⏱ **Настройка интервала напоминаний**\n\n"
        f"Текущий интервал: {REMINDER_DAYS} дней\n\n"
        "Отправь новое значение (число дней).\n"
        "Например: 7, 10, 14\n\n"
        "❌ Отмена: /cancel",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(CourseStates.admin_remind_interval)
    await callback.answer()

@router.message(StateFilter(CourseStates.admin_remind_interval))
async def admin_remind_interval_set(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    try:
        days = int(message.text.strip())
        if days < 1:
            await message.answer("❌ Введи число больше 0.")
            return
    except ValueError:
        await message.answer("❌ Введи число (количество дней).")
        return
    
    # Сохраняем в настройки
    set_setting("reminder_days", str(days))
    
    await message.answer(f"✅ Интервал напоминаний установлен: {days} дней.")
    await state.set_state(CourseStates.admin)
    
    await message.answer(
        "👑 **Панель администратора**\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin_remind_reset")
async def admin_remind_reset(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    reset_reminders()
    await callback.answer("🔄 Флаги напоминаний сброшены!")
    await callback.message.edit_text(
        "✅ Все флаги напоминаний сброшены.\n"
        "Теперь напоминания будут отправлены снова.",
        reply_markup=admin_reminders_keyboard(),
        parse_mode="Markdown"
    )

# ===== НАСТРОЙКИ =====
@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    standard_price = get_setting("course_price") or "1990"
    premium_price = get_setting("premium_price") or "2990"
    course_name = get_setting("course_name") or "Курс ПДД"
    channel_link = get_setting("channel_link") or "Не задана"
    support_link = get_setting("support_link") or "Не задана"
    
    await callback.message.edit_text(
        "⚙️ **Настройки**\n\n"
        f"💰 Стандарт: {standard_price} ₽\n"
        f"💰 Премиум: {premium_price} ₽\n"
        f"📝 Название: {course_name}\n"
        f"🔗 Канал: {channel_link[:30]}...\n"
        f"📞 Поддержка: {support_link[:30]}...\n\n"
        "Выбери что изменить:",
        reply_markup=admin_settings_keyboard(standard_price, premium_price, course_name, channel_link, support_link),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_set_"))
async def admin_set_setting(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    key = callback.data.replace("admin_set_", "")
    setting_names = {
        "standard": "цену для тарифа Стандарт (число)",
        "premium": "цену для тарифа Премиум (число)",
        "name": "название курса (текст)",
        "channel": "ссылку на канал (начинается с https://t.me/)",
        "support": "ссылку на поддержку (начинается с https://t.me/)"
    }
    
    await state.update_data(setting_key=key)
    await callback.message.edit_text(
        f"✏️ **Изменить {setting_names[key]}**\n\n"
        f"Отправь новое значение.\n\n"
        "❌ Отмена: /cancel",
        reply_markup=back_to_admin_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(CourseStates.admin_edit_setting)
    await callback.answer()

@router.message(StateFilter(CourseStates.admin_edit_setting))
async def admin_edit_setting_process(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    key = data.get("setting_key")
    value = message.text.strip()
    
    if not key:
        await message.answer("❌ Ошибка. Попробуй снова /admin")
        return
    
    # Валидация
    if key in ["standard", "premium"]:
        try:
            int(value)
        except ValueError:
            await message.answer("❌ Введи число (цену в рублях).")
            return
        db_key = "course_price" if key == "standard" else "premium_price"
    elif key == "name":
        db_key = "course_name"
    elif key == "channel":
        db_key = "channel_link"
        if not value.startswith("https://t.me/"):
            await message.answer("❌ Ссылка должна начинаться с https://t.me/")
            return
    elif key == "support":
        db_key = "support_link"
        if not value.startswith("https://t.me/"):
            await message.answer("❌ Ссылка должна начинаться с https://t.me/")
            return
    else:
        await message.answer("❌ Неизвестный параметр.")
        return
    
    set_setting(db_key, value)
    await message.answer(f"✅ Настройка обновлена!")
    await state.set_state(CourseStates.admin)
    
    await message.answer(
        "👑 **Панель администратора**\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="Markdown"
    )

# ===== ЭКСПОРТ CSV =====
@router.callback_query(F.data == "admin_export")
async def admin_export(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Нет доступа", show_alert=True)
        return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    conn.close()
    
    if not rows:
        await callback.answer("❌ Нет данных для экспорта", show_alert=True)
        return
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['user_id', 'username', 'full_name', 'tariff', 'paid', 'price', 'purchase_date', 'in_channel', 'last_activity', 'reminded'])
    writer.writerows(rows)
    
    await callback.answer("📄 Файл отправлен в личные сообщения!", show_alert=True)
    
    await callback.message.answer_document(
        FSInputFile(io.BytesIO(output.getvalue().encode('utf-8')), filename='users_export.csv'),
        caption="📊 Экспорт базы пользователей"
    )

# ============================================
# ===== ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД =====
# ============================================

@router.message()
async def unknown_message(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Действие отменено.")
        return
    
    await message.answer(
        "❌ Я не понимаю эту команду.\n"
        "Используй кнопки для навигации."
    )