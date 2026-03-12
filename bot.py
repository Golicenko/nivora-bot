# ============================================================
# TELEGRAM BOT 
# ============================================================

import asyncio
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, LabeledPrice, PreCheckoutQuery,
    FSInputFile, InputMediaPhoto, WebAppInfo
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
CREATE TABLE IF NOT EXISTS visits(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
date TEXT
)
""")

db.commit()

def create_order(user_id, username, name, text, type, price):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "INSERT INTO orders(user_id, username, name, text, type, price, status, date) VALUES(?,?,?,?,?,?,?,?)",
        (user_id, username, name, text, type, price, "waiting_payment", now)
    )

    db.commit()

    return cursor.lastrowid
# ============================================================
# STATES
# ============================================================

class AskState(StatesGroup):
    waiting_question = State()

class ReplyState(StatesGroup):
    waiting_reply = State()

class BroadcastState(StatesGroup):
    waiting_text = State()
    
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
"🪙 Коины — 30.000",
"💰 Вирты — 50.000.000",
"💪 Силы — 300 / 414 / 800 / 1625",
"🏎 Донатный W16",
"🚗 Чит машина",
"⚙️ Настройка трансмиссии",
"✨ Хром машина",
"🧰 Боди кит (ваш выбор)",
"⚖️ Изменение массы машины",
"🏠 Открыть 3 дом",
"📋 Копирование вашей машины",
"⛽ Бесконечное топливо",
"👑 Ранг King на аккаунт",
"🛸 Машина НЛО на ваше авто",
"🌈 Разноцветный ник в игре"
]

# =====================================================
# SETS DATA
# =====================================================

SETS = [

{
"name": "🥉 Стартовый набор",
"photo": "standard.jpg",
"text": """🥉 Набор №1 — Стартовый

Что входит:

💰 Вирты — 50.000.000
🪙 Коины — 10.000
⚙️ Чит силы 300 / 414 / 800 / 1695

⭐ Цена: 20 Stars
""",
"price": 20
},

{
"name": "🥈 Продвинутый набор",
"photo": "pro.jpg",
"text": """🥈 Набор №2 — Продвинутый

Что входит:

💰 Вирты — 50.000.000
🪙 Коины — 30.000
💪 Силы — 300 / 414 / 800 / 1625
🚗 Чит машина
🏠 Дом 3

⭐ Цена: 35 Stars
""",
"price": 35
},

{
"name": "🥇 Полный набор",
"photo": "vip.jpg",
"text": """🥇 Набор №3 — Полный

Что входит:

💰 Вирты — 50.000.000
🪙 Коины — 30.000
💪 Силы — 300 / 414 / 800 / 1625
🏎 Донатный W16
🚗 Чит машина
⚙️ Настройка трансмиссии
✨ Хром машина
🧰 Боди кит
⚖️ Изменение массы машины
🏠 Открыть 3 дом
⛽ Бесконечное топливо

⭐ Цена: 50 Stars
""",
"price": 1
}

]
# ============================================================
# MENUS
# ============================================================

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="🎁 Наборы услуг (выгоднее)", callback_data="sets")],

        [InlineKeyboardButton(text="🚘 Услуги в игре", callback_data="services")],

        [InlineKeyboardButton(text="✍️ Задать свой вопрос", callback_data="ask")],

        [InlineKeyboardButton(text="🤩 Популярные вопросы", callback_data="popular")]

    ])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Новые заказы", callback_data="admin_new")],
        [InlineKeyboardButton(text="✅ Готовые", callback_data="admin_done")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="analytics")]
    ])


def analytics_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="analytics_today")],
        [InlineKeyboardButton(text="📊 Все время", callback_data="analytics_all")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
    ])

# =====================================================
# SETS START
# =====================================================

@dp.callback_query(F.data == "sets")
async def sets_start(call: CallbackQuery):

    index = 0
    s = SETS[index]

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back_menu"),
            InlineKeyboardButton(text="➡ Далее", callback_data="set_next:0")
        ],

        [InlineKeyboardButton(text="💳 Купить", callback_data="buy_set:0")],

        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]

    ])

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(s["photo"]),
            caption=s["text"]
        ),
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("set_next:"))
async def set_next(call: CallbackQuery):

    index = int(call.data.split(":")[1]) + 1

    if index >= len(SETS):
        index = len(SETS) - 1

    s = SETS[index]

    buttons = []

    if index == 1:
        buttons.append([
            InlineKeyboardButton(text="⬅ Назад", callback_data="set_prev:1"),
            InlineKeyboardButton(text="➡ Далее", callback_data="set_next:1")
        ])

    elif index == 2:
        buttons.append([
            InlineKeyboardButton(text="⬅ Назад", callback_data="set_prev:2")
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        *buttons,
        [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_set:{index}")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]
    ])

    media = InputMediaPhoto(
        media=FSInputFile(s["photo"]),
        caption=s["text"]
    )

    await call.message.edit_media(
        media=media,
        reply_markup=kb
    )


# =====================================================
# PREVIOUS SET
# =====================================================

@dp.callback_query(F.data.startswith("set_prev:"))
async def set_prev(call: CallbackQuery):

    index = int(call.data.split(":")[1]) - 1

    if index < 0:
        index = 0

    s = SETS[index]

    if index == 0:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back_menu"),
                InlineKeyboardButton(text="➡ Далее", callback_data="set_next:0")
            ],
            [InlineKeyboardButton(text="💳 Купить", callback_data="buy_set:0")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]
        ])

    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data=f"set_prev:{index}"),
                InlineKeyboardButton(text="➡ Далее", callback_data=f"set_next:{index}")
            ],
            [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_set:{index}")],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]
        ])

    media = InputMediaPhoto(
        media=FSInputFile(s["photo"]),
        caption=s["text"]
    )

    await call.message.edit_media(
        media=media,
        reply_markup=kb
    )
# =====================================================
# BUY SET
# =====================================================

@dp.callback_query(F.data.startswith("buy_set:"))
async def buy_set(call: CallbackQuery):

    index = int(call.data.split(":")[1])

    s = SETS[index]

    name = s["name"]
    price = s["price"]

    order_id = create_order(
        call.from_user.id,
        call.from_user.username,
        call.from_user.first_name,
        name,
        "set",
        price
    )

    prices = [LabeledPrice(label=name, amount=price)]

    await bot.send_invoice(
        call.from_user.id,
        title=name,
        description="Покупка набора",
        payload=f"order_{order_id}",
        provider_token="",
        currency="XTR",
        prices=prices
    )

# ============================================================
# START
# ============================================================

@dp.message(Command("start"))
async def start(message: Message):

    name = message.from_user.first_name

    # записываем посещение
    cursor.execute(
        "INSERT INTO visits(user_id,date) VALUES(?,?)",
        (message.from_user.id, datetime.now().strftime("%Y-%m-%d"))
    )
    db.commit()

    text = f"""Здравствуй, {name}! 👋

Если ты совершаешь покупку первый раз в нашем боте,
рекомендуем ознакомиться с информацией ниже.

Мы подготовили несколько страниц с важной информацией:

🔎 Почему нам можно доверять  
🔒 Гарантии безопасности  
🛒 Как проходит покупка  
🌐 Наши официальные каналы  

После ознакомления ты можешь перейти в основное меню бота.
"""

    await message.answer(
        text,
        reply_markup=trust_menu()
    )

def trust_menu():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🔎 Почему нам можно доверять",
                    web_app=WebAppInfo(
                        url="https://golicenko.github.io/nivora-bot/trust.html"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔒 Гарантии безопасности",
                    web_app=WebAppInfo(
                        url="https://golicenko.github.io/nivora-bot/security.html"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛒 Как проходит покупка",
                    web_app=WebAppInfo(
                        url="https://golicenko.github.io/nivora-bot/purchase.html"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    text="🌐 Наши официальные каналы",
                    web_app=WebAppInfo(
                        url="https://golicenko.github.io/nivora-bot/channels.html"
                    )
                )
            ],

            [
                InlineKeyboardButton(
                    text="🚀 Перейти в меню бота",
                    callback_data="back_menu"
                )
            ]

        ]
    )

    return keyboard
    
# ============================================================
# BACK
# ============================================================

@dp.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    await call.message.edit_text(
       """AF-Bot 🏠Главное меню

Прокачай свой аккаунт в игре Car Parking.

Выбери услугу, наборы
или задай свой вопрос ниже 👇""",
        reply_markup=main_menu()
    )

# ============================================================
# ANALYTICS TODAY
# ============================================================
@dp.callback_query(F.data == "analytics")
async def analytics(call: CallbackQuery):

    await call.message.edit_text(
        "📊 Аналитика",
        reply_markup=analytics_menu()
    )

@dp.callback_query(F.data == "analytics_today")
async def analytics_today(call: CallbackQuery):
 
    # заказы сегодня
    cursor.execute(
    "SELECT COUNT(*) FROM orders WHERE status='new' AND date >= date('now')"
)
    orders = cursor.fetchone()[0]

    # посещения сегодня
    cursor.execute(
        "SELECT COUNT(*) FROM visits WHERE date(date)=date('now')"
    )
    visits = cursor.fetchone()[0]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="analytics")]
        ]
    )

    await call.message.edit_text(
        f"""📊 Сегодня

📦 Заказы: {orders}
👥 Посещения: {visits}
""",
        reply_markup=kb
    )

# ====================================================
# ANALYTICS ALL TIME
# ====================================================

@dp.callback_query(F.data == "analytics_all")
async def analytics_all(call: CallbackQuery):

    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE status='new'"
    )
    orders = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM visits"
    )
    visits = cursor.fetchone()[0]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="analytics")]
    ])

    await call.message.edit_text(
        f"""📊 Все время

📦 Заказы: {orders}
👥 Посещения: {visits}
""",
        reply_markup=kb
    )
# ============================================================
# POPULAR QUESTIONS
# ============================================================

@dp.callback_query(F.data=="popular")
async def popular(call:CallbackQuery):

    buttons=[]
    for i,q in enumerate(POPULAR):
        buttons.append([InlineKeyboardButton(text=q,callback_data=f"pq_{i}")])

    buttons.append([InlineKeyboardButton(text="⬅ Назад",callback_data="back")])

    await call.message.edit_text(
        "🤩 Популярные вопросы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("pq_"))
async def buy_pop(call:CallbackQuery):

    index=int(call.data.split("_")[1])
    question=POPULAR[index]

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

    order_id=cursor.lastrowid
    db.commit()

    await bot.send_invoice(
        call.from_user.id,
        title="Ответ на вопрос",
        description=question,
        payload=f"order_{order_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Ответ",amount=1)]
    )

# ============================================================
# SERVICES
# ============================================================

@dp.callback_query(F.data=="services")
async def services(call:CallbackQuery):

    buttons=[]
    for i,s in enumerate(SERVICES):
        buttons.append([InlineKeyboardButton(text=s,callback_data=f"service_{i}")])

    buttons.append([InlineKeyboardButton(text="⬅ Назад",callback_data="back")])

    await call.message.edit_text(
        "🚘 Игровые услуги\nЦена любой услуги 10⭐",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("service_"))
async def buy_service(call:CallbackQuery):

    index=int(call.data.split("_")[1])
    service=SERVICES[index]

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

    order_id=cursor.lastrowid
    db.commit()

    await bot.send_invoice(
chat_id=call.from_user.id,
title="Игровая услуга",
description=service,
payload=f"order_{order_id}",
provider_token="",
currency="XTR",
prices=[LabeledPrice(label=service, amount=10)]
)

# ============================================================
# ASK QUESTION
# ============================================================

@dp.callback_query(F.data=="ask")
async def ask(call:CallbackQuery,state:FSMContext):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )

    await call.message.edit_text(
"""Здравствуйте я Максим.

Пожалуйста напишите свой вопрос максимально понятно
чтобы мы могли ответить максимально подробно.

Максимум 150 символов""",
        reply_markup=kb
    )

    await state.set_state(AskState.waiting_question)

@dp.message(AskState.waiting_question)
async def receive_question(message: Message, state: FSMContext):

    if message.text.startswith("/"):
        await state.clear()
        await message.answer(
            """AF Bot — Главное меню

🚘 Прокачай свой аккаунт в игре Car Parking.

Выбери услугу, наборы
или задай свой вопрос ниже 👇""",
            reply_markup=main_menu()
        )
        return

    if len(message.text) > 150:
        await message.answer("❗ Максимум 150 символов")
        return

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

    await state.clear()

    await bot.send_invoice(
        message.from_user.id,
        title="Ответ на вопрос",
        description=message.text,
        payload=f"order_{order_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Ответ", amount=1)]
    )

# ============================================================
# PAYMENT
# ============================================================

@dp.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def payment(message: Message):

    payload = message.successful_payment.invoice_payload

    try:
        order_id = int(payload.split("_")[-1])
    except:
        await message.answer("❗ Ошибка обработки платежа.")
        return

    cursor.execute(
        "SELECT * FROM orders WHERE id=?",
        (order_id,)
    )
    order = cursor.fetchone()

    if not order:
        await message.answer("❗ Заказ не найден. Напишите администратору.")
        return

    cursor.execute(
        "UPDATE orders SET status='new' WHERE id=?",
        (order_id,)
    )
    db.commit()

    username = message.from_user.username
    buyer = f"@{username}" if username else message.from_user.full_name

    service = order[4]
    price = order[6]
    date = order[8]

    # ЧЕК
    await message.answer(
f"""🧾 ЧЕК ОБ ОПЛАТЕ

📦 Услуга:
{service}

⭐ Стоимость:
{price} Telegram Stars

🕒 Дата:
{date}

👤 Покупатель:
{buyer}

━━━━━━━━━━━━━━━

✅ Оплата прошла успешно!

📩 Администратор уже получил ваш заказ.
Ожидайте выполнения услуги."""
)

    # КНОПКА ПРИНЯТЬ
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data=f"take_{order_id}")]
        ]
    )

    # ЗАКАЗ АДМИНУ
    await bot.send_message(
        ADMIN_ID,
f"""📥 Новый заказ

👤 {buyer}
📦 {service}
⭐ {price} Stars
⏰ {date}""",
reply_markup=kb
    )

# ============================================================
# TAKE ORDER
# ============================================================

@dp.callback_query(F.data.startswith("take_"))
async def take_order(call: CallbackQuery):

    order_id = int(call.data.split("_")[1])

    cursor.execute(
        "UPDATE orders SET status='new' WHERE id=?",
        (order_id,)
    )
    db.commit()

    # удаляем сообщение из чата
    await call.message.delete()

    await call.answer("Заказ принят")

# ============================================================
# BACK TO MENU
# ============================================================

@dp.callback_query(F.data == "back_menu")
async def back_menu(call: CallbackQuery):

    text = """AF Bot — Главное меню

🚘 Прокачай свой аккаунт в игре Car Parking.

Выбери услугу, наборы
или задай свой вопрос ниже 👇"""

    try:
        await call.message.edit_text(text, reply_markup=main_menu())
    except:
        await call.message.answer(text, reply_markup=main_menu())

    await call.answer()
    
# ============================================================
# ADMIN PANEL
# ============================================================

@dp.message(Command("admin"))
async def admin(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        await message.delete()
    except:
        pass

    await message.answer(
        "⚙️ Админ панель",
        reply_markup=admin_menu()
    )

# ============================
# BROADCAST
# ============================

class BroadcastState(StatesGroup):
    waiting_text = State()


@dp.message(Command("broadcast"))
async def broadcast_start(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📢 Напишите сообщение для рассылки"
    )

    await state.set_state(BroadcastState.waiting_text)


@dp.message(BroadcastState.waiting_text)
async def broadcast_send(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text

    cursor.execute(
        "SELECT DISTINCT user_id FROM visits"
    )

    users = cursor.fetchall()

    sent = 0
    failed = 0

    for user in users:

        try:
            await bot.send_message(
                user[0],
                f"📢 Обновление бота\n\n{text}"
            )
            sent += 1

        except:
            failed += 1

        await asyncio.sleep(0.05)

    await message.answer(
        f"✅ Рассылка завершена\n\n"
        f"Отправлено: {sent}\n"
        f"Ошибка: {failed}"
    )

    await state.clear()
# ============================================================
# NEW ORDERS
# ============================================================

@dp.callback_query(F.data=="admin_new")
async def admin_new(call:CallbackQuery):

    cursor.execute("SELECT * FROM orders WHERE status='new'")
    orders=cursor.fetchall()

    buttons=[]

    for o in orders:
        buttons.append([
            InlineKeyboardButton(
                text=f"{o[3]} | {o[8]}",
                callback_data=f"order_{o[0]}"
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(text="❗ Заказов нет",callback_data="none")
        ])

    buttons.append([
InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")
])
    await call.message.edit_text(
"📥 Новые заказы",
reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
)

# ============================================================
# VIEW ORDER
# ============================================================

# ============================================================
# VIEW ORDER
# ============================================================

@dp.callback_query(F.data.startswith("order_"))
async def view_order(call: CallbackQuery):

    order_id = int(call.data.split("_")[1])

    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    o = cursor.fetchone()

    if not o:
        await call.answer("Заказ не найден")
        return

    text = f"""
📦 Заказ #{o[0]}

👤 Имя: {o[3]}
🔗 Username: @{o[2]}

📄 Текст:
{o[4]}

🕒 Время: {o[8]}
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✉️ Ответить",
                callback_data=f"reply_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Перейти к пользователю",
                url=f"tg://user?id={o[1]}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅ Назад",
                callback_data="admin_new"
            )
        ]
    ])

    await call.message.edit_text(text, reply_markup=kb)

# =====================================================
# REPLY
# =====================================================

@dp.callback_query(F.data.startswith("reply_"))
async def reply_start(call: CallbackQuery, state: FSMContext):

    order_id = call.data.split("_")[1]

    await state.update_data(
        order_id=order_id,
        order_msg_id=call.message.message_id
    )

    msg = await bot.send_message(
        ADMIN_ID,
        "✍️ Напишите ответ"
    )

    await state.update_data(reply_msg=msg.message_id)

    await state.set_state(ReplyState.waiting_reply)


@dp.message(ReplyState.waiting_reply)
async def reply_send(message: Message, state: FSMContext):

    data = await state.get_data()

    order_id = data.get("order_id")
    reply_msg = data.get("reply_msg")
    order_msg_id = data.get("order_msg_id")

    cursor.execute(
        "SELECT user_id FROM orders WHERE id=?",
        (order_id,)
    )

    row = cursor.fetchone()

    if not row:
        await state.clear()
        return

    user_id = row[0]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )

    # отправляем ответ клиенту
    msg = await bot.send_message(
        user_id,
        f"📩 Ответ\n\n{message.text}",
        reply_markup=kb
    )

    # меняем статус заказа
    cursor.execute(
        "UPDATE orders SET status='done' WHERE id=?",
        (order_id,)
    )

    db.commit()

    await state.clear()

    # удаляем сообщение админа
    try:
        await message.delete()
    except:
        pass

    # удаляем "Напишите ответ"
    try:
        await bot.delete_message(ADMIN_ID, reply_msg)
    except:
        pass

    # удаляем сообщение заказа
    try:
        await bot.delete_message(ADMIN_ID, order_msg_id)
    except:
        pass

    # админ меню
    await bot.send_message(
        ADMIN_ID,
        "⚙️ Админ панель",
        reply_markup=admin_menu()
    )
    
# ============================================================
# DONE ORDERS
# ============================================================

@dp.callback_query(F.data=="admin_done")
async def admin_done(call:CallbackQuery):

    cursor.execute(
        "SELECT * FROM orders WHERE status='done' ORDER BY id DESC"
    )

    orders = cursor.fetchall()

    buttons = []

    for o in orders:

        buttons.append([
            InlineKeyboardButton(
                text=f"{o[3]} | {o[8]}",
                callback_data="none"
            )
        ])

    if not buttons:

        buttons.append([
            InlineKeyboardButton(
                text="❗ Готовых заказов нет",
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
        "✅ Готовые заказы",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
 
# ============================================================
# STATS
# ============================================================

def get_stats(days=None):

    if days:
        date=(datetime.now()-timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT COUNT(*), SUM(price) FROM orders WHERE date>=?",(date,))
    else:
        cursor.execute("SELECT COUNT(*), SUM(price) FROM orders")

    data=cursor.fetchone()
    return data[0], data[1] or 0

@dp.callback_query(F.data=="stats_menu")
async def stats_menu(call:CallbackQuery):

    kb=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 день",callback_data="stats_1")],
        [InlineKeyboardButton(text="7 дней",callback_data="stats_7")],
        [InlineKeyboardButton(text="30 дней",callback_data="stats_30")],
        [InlineKeyboardButton(text="Все время",callback_data="stats_all")],
        [InlineKeyboardButton(text="⬅ Назад",callback_data="admin_back")]
    ])

    await call.message.edit_text("📊 Статистика",reply_markup=kb)

@dp.callback_query(F.data=="admin_back")
async def admin_back(call:CallbackQuery):
    await call.message.edit_text("⚙️ Админ панель",reply_markup=admin_menu())

@dp.callback_query(F.data.startswith("stats_"))
async def stats(call: CallbackQuery):

    p = call.data.split("_")[1]

    if p == "all":
        c, s = get_stats()
        title = "Все время"
    else:
        days = int(p)
        c, s = get_stats(days)
        title = f"{days} дней"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="stats_menu")]
    ])

    await call.message.edit_text(
f"""📊 Статистика ({title})

Заказы: {c}
""",
reply_markup=kb
)
@dp.callback_query(F.data=="none")
async def none(call: CallbackQuery):
    await call.answer("Заказов нет")
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())










































































