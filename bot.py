# ============================================================
# NIVORA AUTO FLOW BOT V3 (FIXED)
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

db.commit()

# ============================================================
# STATES
# ============================================================

class AskState(StatesGroup):
    waiting_question = State()
    waiting_free = State()

class AdminReply(StatesGroup):
    waiting_reply = State()

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

    text = """здраствуй:
• Game Guardian
• Virtual Space

🚗 Приобрести услуги для игры:
Car Parking Multiplayer

Выберите нужный раздел ниже 👇
"""

    await message.answer(text, reply_markup=main_menu())

# ============================================================
# BACK
# ============================================================

@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):

    await call.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

# ============================================================
# POPULAR QUESTIONS
# ============================================================

@dp.callback_query(F.data == "popular")
async def popular(call: CallbackQuery):

    buttons = []

    for i, q in enumerate(POPULAR):
        buttons.append([
            InlineKeyboardButton(text=q, callback_data=f"pq_{i}")
        ])

    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])

    await call.message.edit_text(
        "🤩 Популярные вопросы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@dp.callback_query(F.data.startswith("pq_"))
async def popular_question(call: CallbackQuery):

    index = int(call.data.split("_")[1])
    question = POPULAR[index]

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(
            text="💳 Ответ на вопрос — 1⭐",
            callback_data=f"pay_pop_{index}"
        )],

        [InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="popular"
        )]

    ])

    await call.message.edit_text(
        f"❓ Вопрос:\n\n{question}\n\nНажмите кнопку ниже чтобы получить ответ.",
        reply_markup=kb
    )

# ============================================================
# POPULAR PAYMENT
# ============================================================

@dp.callback_query(F.data.startswith("pay_pop_"))
async def pay_popular(call: CallbackQuery):

    index = int(call.data.split("_")[2])
    question = POPULAR[index]

    cursor.execute("""
INSERT INTO orders(user_id,username,name,text,type,price,status,date)
VALUES(?,?,?,?,?,?,?,?)
""",(
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
# ASK QUESTION
# ============================================================

@dp.callback_query(F.data == "ask")
async def ask_question(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text(
        "✏ Напишите ваш вопрос:",
        reply_markup=back_menu()
    )

    await state.set_state(AskState.waiting_question)


@dp.message(AskState.waiting_question)
async def save_question(message: Message, state: FSMContext):

    await state.update_data(question=message.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(
            text="💳 Ответить на вопрос — 1⭐",
            callback_data="pay_custom"
        )],

        [InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="back"
        )]

    ])

    await message.answer(
        f"❓ Ваш вопрос:\n\n{message.text}\n\nНажмите оплатить чтобы отправить вопрос.",
        reply_markup=kb
    )


@dp.callback_query(F.data == "pay_custom")
async def pay_custom(call: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    question = data["question"]

    cursor.execute("""
INSERT INTO orders(user_id,username,name,text,type,price,status,date)
VALUES(?,?,?,?,?,?,?,?)
""",(
call.from_user.id,
call.from_user.username,
call.from_user.first_name,
question,
"custom",
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
# FREE QUESTION
# ============================================================

@dp.callback_query(F.data == "free_question")
async def free_question(call: CallbackQuery, state: FSMContext):

    cursor.execute(
        "SELECT free_used FROM users WHERE user_id=?",
        (call.from_user.id,)
    )

    row = cursor.fetchone()

    if row and row[0] == 1:

        await call.answer(
            "❌ Вы уже использовали бесплатный вопрос",
            show_alert=True
        )

        return

    if not row:

        cursor.execute(
            "INSERT INTO users (user_id,free_used) VALUES (?,0)",
            (call.from_user.id,)
        )

        db.commit()

    await call.message.edit_text(
        "✏️ Напишите ваш бесплатный вопрос:",
        reply_markup=back_menu()
    )

    await state.set_state(AskState.waiting_free)


@dp.message(AskState.waiting_free)
async def receive_free(message: Message, state: FSMContext):

    cursor.execute("""
INSERT INTO orders(user_id,username,name,text,type,price,status,date)
VALUES(?,?,?,?,?,?,?,?)
""",(
message.from_user.id,
message.from_user.username,
message.from_user.first_name,
message.text,
"free",
0,
"new",
datetime.now().strftime("%Y-%m-%d %H:%M")
))

    cursor.execute(
        "UPDATE users SET free_used=1 WHERE user_id=?",
        (message.from_user.id,)
    )

    db.commit()

    await message.delete()

    await bot.send_message(
        message.from_user.id,
        "✅ Бесплатный вопрос отправлен",
        reply_markup=main_menu()
    )

    await bot.send_message(
        ADMIN_ID,
        f"🆓 Новый бесплатный вопрос\n\n👤 {message.from_user.first_name}\n📄 {message.text}\n\n/admin"
    )

    await state.clear()

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

    cursor.execute(
        "UPDATE orders SET status='new' WHERE id=?",
        (order_id,)
    )

    db.commit()

    cursor.execute(
        "SELECT * FROM orders WHERE id=?",
        (order_id,)
    )

    o = cursor.fetchone()

    await message.answer(
f"""🧾 Чек

👤 {o[3]}
📦 {o[4]}
⭐ {o[6]}

✅ Оплата прошла успешно""",
reply_markup=back_menu()
)

    await bot.send_message(
        ADMIN_ID,
f"""📦 Новый заказ

👤 {o[3]}
📄 {o[4]}

/admin"""
)

# ============================================================
# ADMIN
# ============================================================

@dp.message(Command("admin"))
async def admin(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "⚙️ Админ панель",
        reply_markup=admin_menu()
    )

@dp.callback_query(F.data == "admin_new")
async def admin_new(call: CallbackQuery):

    cursor.execute(
        "SELECT id,name,text,date FROM orders WHERE status='new'"
    )

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

        buttons.append([
            InlineKeyboardButton(
                text="❗ Заказов нет",
                callback_data="none"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="admin_back"
        )
    ])

    await call.message.edit_text(
        "📥 Новые заказы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# ============================================================

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())





























