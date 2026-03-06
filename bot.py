
# ============================================================
# NIVORA AUTO FLOW BOT V2 (FIXED ERRORS ONLY)
# ============================================================

import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8793368680:AAHt-SAaKjCx7ZcPyGPovDYHiXtYnflaNCk"
ADMIN_ID = 6277321336

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect("bot.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
username TEXT,
name TEXT,
text TEXT,
type TEXT,
price INTEGER,
status TEXT,
date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
free_used INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats(
date TEXT PRIMARY KEY,
starts INTEGER
)
""")

db.commit()

# ============================================================
# STATES
# ============================================================

class AskState(StatesGroup):
    waiting_question = State()
    waiting_free = State()

# ============================================================
# DATA
# ============================================================

POPULAR = [
"📥 Как скачать Game Guardian",
"⚙️ Как установить Game Guardian (Android 5-14)",
"📦 Как скачать виртуальное пространство",
"🛠 Как настроить Game Guardian",
"📘 Как пользоваться Game Guardian",
"📱 Что делать если Android 15-16",
"📜 Как скачать скрипт",
"📂 Как установить скрипт",
"🎮 Как пользоваться скриптом"
]

SERVICES = [
"👑 Макс ранг",
"🎭 Анимации",
"🏠 Дома",
"🏆 Без урона",
"⛽ Бесконечное топливо",
"🚀 W16 двигатель",
"💵 Деньги",
"🪙 Коины"
]

# ============================================================
# MENUS
# ============================================================

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Бесплатный пробный вопрос", callback_data="free_question")],
        [InlineKeyboardButton(text="🤩 Популярные вопросы", callback_data="popular")],
        [InlineKeyboardButton(text="✍️ Написать свой вопрос", callback_data="ask")],
        [InlineKeyboardButton(text="🚘 Услуги в игре", callback_data="services")]
    ])

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад в меню", callback_data="back")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Новые заказы", callback_data="admin_new")],
        [InlineKeyboardButton(text="✅ Готовые", callback_data="admin_done")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="stats_menu")]
    ])

# ============================================================
# START
# ============================================================

@dp.message(Command("start"))
async def start(message: Message):

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT * FROM stats WHERE date=?", (today,))
    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE stats SET starts = starts + 1 WHERE date=?",
            (today,)
        )
    else:
        cursor.execute(
            "INSERT INTO stats VALUES(?,1)",
            (today,)
        )

    db.commit()

    await message.answer(
"""👋 Добро пожаловать!

Я помогу решить проблемы
с Game Guardian и Virtual Space.

Напишите ваш вопрос 👇
"""
    )

# ============================================================
# BACK
# ============================================================

@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.edit_text("🏠 Главное меню", reply_markup=main_menu())

# ============================================================
# POPULAR
# ============================================================

@dp.callback_query(F.data == "popular")
async def popular(call: CallbackQuery):

    buttons = []
    for i, q in enumerate(POPULAR):
        buttons.append([InlineKeyboardButton(text=q, callback_data=f"pq_{i}")])

    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])

    await call.message.edit_text(
        "🤩 Популярные вопросы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("pq_"))
async def buy_pop(call: CallbackQuery):

    index = int(call.data.split("_")[1])
    question = POPULAR[index]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответ на вопрос — 1⭐", callback_data=f"pay_pop_{index}")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="popular")]
    ])

    await call.message.edit_text(
        f"""❓ Вопрос

{question}

Нажмите кнопку ниже чтобы получить ответ
""",
        reply_markup=kb
    )
    @dp.callback_query(F.data.startswith("pay_pop_"))
async def pay_pop(call: CallbackQuery):

    index = int(call.data.split("_")[2])
    question = POPULAR[index]

    cursor.execute("""
INSERT INTO orders(user_id,username,name,text,type,price,status,date)
VALUES(?,?,?,?,?,?,?,?)
""", (
        call.from_user.id,
        call.from_user.username,
        call.from_user.first_name,
        question,
        "popular",
        1,
        "waiting_payment",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    order_id = cursor.lastrowid
    db.commit()

    await bot.send_invoice(
        call.from_user.id,
        title="Ответ на вопрос",
        description=question,
        payload=f"order_{order_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Ответ", amount=1)],
        reply_markup=back_menu()
    )
# ============================================================
# SERVICES
# ============================================================

@dp.callback_query(F.data == "services")
async def services(call: CallbackQuery):

    buttons = []
    for i, s in enumerate(SERVICES):
        buttons.append([InlineKeyboardButton(text=s, callback_data=f"service_{i}")])

    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])

    await call.message.edit_text(
        "🚘 Игровые услуги\nЦена любой услуги 10⭐",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("service_"))
async def buy_service(call: CallbackQuery):

    index = int(call.data.split("_")[1])
    service = SERVICES[index]

    cursor.execute("""
INSERT INTO orders(user_id,username,name,text,type,price,status,date)
VALUES(?,?,?,?,?,?,?,?)
""",(
call.from_user.id,
call.from_user.username,
call.from_user.first_name,
service,
"service",
10,
"waiting_payment",
datetime.now().strftime("%Y-%m-%d %H:%M")
))

    order_id = cursor.lastrowid
    db.commit()

    await bot.send_invoice(
    call.from_user.id,
    title="Игровая услуга",
    description=service,
    payload=f"order_{order_id}",
    provider_token="",
    currency="XTR",
    prices=[LabeledPrice(label="Услуга", amount=10)],
    reply_markup=back_menu()
)
# ============================================================
# ASK QUESTION
# ============================================================

@dp.callback_query(F.data == "ask")
async def ask(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text(
"""✍️ Напишите ваш вопрос

Максимум 150 символов
""",
reply_markup=back_menu()
)

    await state.set_state(AskState.waiting_question)


@dp.message(AskState.waiting_question)
async def receive_question(message: Message, state: FSMContext):

    if len(message.text) > 150:
        await message.answer("❗ Максимум 150 символов")
        return

    user_id = message.from_user.id

    cursor.execute("SELECT free_used FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row and row[0] == 1:

        cursor.execute("""
        INSERT INTO orders(user_id,username,name,text,type,price,status,date)
        VALUES(?,?,?,?,?,?,?,?)
        """,(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.text,
        "question",
        1,
        "waiting_payment",
        datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

        order_id = cursor.lastrowid
        db.commit()

        await bot.send_invoice(
            message.from_user.id,
            title="Ответ на вопрос",
            description=message.text,
            payload=f"order_{order_id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Ответ", amount=1)],
            reply_markup=back_menu()
        )

    else:

        cursor.execute("UPDATE users SET free_used=1 WHERE user_id=?", (user_id,))
        db.commit()

        await message.answer(
            "✅ Бесплатный вопрос отправлен!",
            reply_markup=main_menu()
        )

        await bot.send_message(
            ADMIN_ID,
            f"""📩 Новый бесплатный вопрос

👤 {message.from_user.first_name}
📄 {message.text}

/admin"""
        )

    await state.clear()
# =========================================
# FREE QUESTION
# =========================================

@dp.callback_query(F.data == "free_question")
async def free_question(call: CallbackQuery, state: FSMContext):

    user_id = call.from_user.id

    # проверяем есть ли пользователь
    cursor.execute(
        "SELECT free_used FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()

    # если пользователь уже использовал бесплатный вопрос
    if row and row[0] == 1:
        await call.answer(
            "❌ Вы уже использовали бесплатный вопрос",
            show_alert=True
        )
        return

    # если пользователя нет в базе
    if not row:
        cursor.execute(
            "INSERT INTO users (user_id, free_used) VALUES (?, 0)",
            (user_id,)
        )
        db.commit()

    # сообщение пользователю
    await call.message.edit_text(
        "✏️ Напишите ваш бесплатный вопрос:",
        reply_markup=back_menu()
    )

    # устанавливаем состояние
    await state.set_state(AskState.waiting_free)
# ============================================================
# PAYMENT
# ============================================================

@dp.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def payment(message: Message):

    payload = message.successful_payment.invoice_payload
    order_id = int(payload.split("_")[1])

    cursor.execute("UPDATE orders SET status='new' WHERE id=?", (order_id,))
    db.commit()

    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    o = cursor.fetchone()

    await message.answer(
f"""🧾 Чек

👤 {o[3]}
📦 {o[4]}
⭐ {o[6]}

✅ Оплата прошла успешно""",
reply_markup=back_menu()
)

    if o[5] == "free":
        text = "🆓 Новый бесплатный вопрос"
    else:
        text = "📦 Новый заказ"

    await bot.send_message(
        ADMIN_ID,
f"""{text}

👤 {o[3]}
📄 {o[4]}

/admin"""
)

# ============================================================
# ADMIN PANEL (FIXED)
# ============================================================

@dp.message(Command("admin"))
async def admin(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("⚙️ Админ панель", reply_markup=admin_menu())

@dp.callback_query(F.data == "admin_new")
async def admin_new(call: CallbackQuery):

    cursor.execute("SELECT id,name,text,date FROM orders WHERE status='new'")
    orders = cursor.fetchall()

    buttons = []

    for o in orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"{o[1]} | {o[3]}",
                callback_data=f"order_{o[0]}"
            )
        ])

    if not buttons:
       buttons.append([InlineKeyboardButton(text="❗ Заказов нет", callback_data="none")])

    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")])

    await call.message.edit_text(
        "📥 Новые заказы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data == "admin_done")
async def admin_done(call: CallbackQuery):

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='done'")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT date FROM orders WHERE status='done' ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    last = row[0] if row else "Нет"

    text = f"""📊 Выполненные заказы

👇
За все время
{total} заказов

Последний в {last}
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
    ])

    await call.message.edit_text(text, reply_markup=kb)
@dp.callback_query(F.data == "stats_menu")
async def stats_menu(call: CallbackQuery):

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='done'")
    done = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE status='done' AND date LIKE ?",
        (today + "%",)
    )
    today_done = cursor.fetchone()[0]

    text = f"""📊 Аналитика

Выполнено заказов всего: {done}
Выполнено заказов сегодня: {today_done}
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
    ])

    await call.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery):
    await call.message.edit_text("⚙️ Админ панель", reply_markup=admin_menu())

@dp.callback_query(F.data == "none")
async def none(call: CallbackQuery):
    await call.answer("")


# ============================================================
# ORDER VIEW (ADDED FIX)
# ============================================================

@dp.callback_query(F.data.startswith("order_"))
async def view_order(call: CallbackQuery):

    order_id = int(call.data.split("_")[1])

    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    o = cursor.fetchone()

    if not o:
        await call.answer("Заказ не найден")
        return

    text = f"""📦 Заказ #{o[0]}

👤 {o[3]}
📄 {o[4]}
📅 {o[8]}
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить заказ", callback_data=f"done_{order_id}")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_new")]
    ])

    await call.message.edit_text(text, reply_markup=kb)


# ============================================================
# MARK DONE (ADDED FIX)
# ============================================================

@dp.callback_query(F.data.startswith("done_"))
async def mark_done(call: CallbackQuery):

    order_id = int(call.data.split("_")[1])

    cursor.execute("UPDATE orders SET status='done' WHERE id=?", (order_id,))
    db.commit()

    await call.message.edit_text("✅ Заказ завершен", reply_markup=admin_menu())

# ============================================================

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())











