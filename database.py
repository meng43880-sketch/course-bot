import sqlite3
from datetime import datetime, timedelta

DB_NAME = "course_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            tariff TEXT DEFAULT NULL,
            paid BOOLEAN DEFAULT FALSE,
            price INTEGER DEFAULT 0,
            purchase_date TEXT DEFAULT NULL,
            in_channel BOOLEAN DEFAULT FALSE,
            last_activity TEXT DEFAULT NULL,
            reminded BOOLEAN DEFAULT FALSE
        )
    """)
    
    # Таблица настроек
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Настройки по умолчанию
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("course_price", "1990"))
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("premium_price", "2990"))
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("course_name", "Курс подготовки к экзамену ПДД"))
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("channel_link", "https://t.me/your_course_channel"))
    cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ("support_link", "https://t.me/your_support_bot"))
    
    conn.commit()
    conn.close()

# ===== ПОЛЬЗОВАТЕЛИ =====
def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, tariff, paid, purchase_date, in_channel, last_activity FROM users")
    users = cur.fetchall()
    conn.close()
    return users

def get_paid_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, tariff, purchase_date, last_activity FROM users WHERE paid = 1")
    users = cur.fetchall()
    conn.close()
    return users

def get_inactive_users(days):
    """Получить пользователей, которые не заходили в канал больше X дней"""
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username, full_name, last_activity FROM users WHERE paid = 1 AND (last_activity IS NULL OR last_activity < ?) AND reminded = 0",
        (cutoff_date,)
    )
    users = cur.fetchall()
    conn.close()
    return users

def add_user(user_id, username=None, full_name=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name, last_activity) VALUES (?, ?, ?, ?)",
        (user_id, username, full_name, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def mark_paid(user_id, tariff, price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET paid = TRUE, tariff = ?, price = ?, purchase_date = ?, last_activity = ? WHERE user_id = ?",
        (tariff, price, datetime.now().isoformat(), datetime.now().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

def is_paid(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT paid FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result and result[0] == 1

def get_user_tariff(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT tariff FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_price(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT price FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_purchase_date(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT purchase_date FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def update_last_activity(user_id):
    """Обновляем время последней активности (когда пользователь заходил в канал)"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_activity = ?, reminded = 0 WHERE user_id = ?", 
                (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def set_reminded(user_id):
    """Отмечаем, что пользователю уже отправили напоминание"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET reminded = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def reset_reminders():
    """Сбрасываем флаги напоминаний (например, раз в месяц)"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET reminded = 0")
    conn.commit()
    conn.close()

def set_in_channel(user_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET in_channel = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE paid = 1")
    paid_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE in_channel = 1")
    in_channel_users = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(price) FROM users WHERE paid = 1")
    total_income = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(*) FROM users WHERE paid = 1 AND last_activity IS NULL")
    never_visited = cur.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_users": total_users,
        "paid_users": paid_users,
        "in_channel_users": in_channel_users,
        "total_income": total_income,
        "never_visited": never_visited
    }

# ===== НАСТРОЙКИ =====
def get_setting(key):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()