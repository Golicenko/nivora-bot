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

# ============================================================
# ADMIN ORDERS COUNTER
# ============================================================

ADMIN_ORDERS_MESSAGE_ID = None
ADMIN_ORDERS_COUNT = 0

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

# ФУНКЦИЯ ЗАПИСИ АКТИВНОСТИ
def log_visit(user_id):

    cursor.execute(
        "INSERT INTO visits(user_id,date) VALUES(?,?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"))
    )

    db.commit()

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
"price": 50
}

]

# =====================================================
# GAMEGUARDIAN TRAINING
# =====================================================

GG_TRAINING = [

{
"name": "📱 Обучение GameGuardian (Android 5-14)",
"photo": "photo1.jpg",
"text": """📱 Обучение GameGuardian

Подходит для Android 5–14.

Я расскажу и покажу пошагово, как правильно
пользоваться GameGuardian и виртуальным пространством.

Вы узнаете:

• как скачать GameGuardian  
• как установить виртуальное пространство  
• как выдать все необходимые разрешения  
• как пользоваться скриптами  
• базовые основы работы с GameGuardian  

Подходит для новичков и опытных пользователей.
Всегда есть чему научиться.

⭐ Цена: 150 Stars
""",
"price": 150,
"url": "https://golicenko.github.io/nivora-bot/android5-14-guide.html"
},

{
"name": "📱 Обучение GameGuardian (Android 15-16)",
"photo": "photo2.jpg",
"text": """📱 Обучение GameGuardian

Подходит для Android 15–16.

В этих версиях Android есть ограничения,
поэтому используется другой способ запуска.

Я покажу и расскажу:

• как установить GameGuardian  
• как настроить виртуальное пространство  
• как выдать все необходимые разрешения  
• как обходить античит  
• как пользоваться скриптами  
• базовые основы работы с GameGuardian  

Подходит для новичков и опытных пользователей.
Всегда есть чему научиться.

⭐ Цена: 250 Stars
""",
"price": 250,
"url": "https://golicenko.github.io/nivora-bot/guide-android-15-16.html"
}

]

@dp.callback_query(F.data.startswith("gg_next:"))
async def gg_next(call: CallbackQuery):

    index = int(call.data.split(":")[1]) + 1

    if index >= len(GG_TRAINING):
        index = len(GG_TRAINING) - 1

    g = GG_TRAINING[index]

    buttons = []

    if index == 1:
        buttons.append([
            InlineKeyboardButton(text="⬅ Назад", callback_data="gg_prev:1")
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        *buttons,
        [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_gg:{index}")],
        [
            InlineKeyboardButton(
                text="📖 Полное описание",
                web_app=WebAppInfo(url=g["url"])
            )
        ],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]
    ])

    media = InputMediaPhoto(
        media=FSInputFile(g["photo"]),
        caption=g["text"]
    )

    await call.message.edit_media(
        media=media,
        reply_markup=kb
    )
# ============================================================
# MENUS
# ============================================================

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text="🎁 Наборы услуг (выгоднее)", callback_data="sets")],

        [InlineKeyboardButton(text="🚘 Услуги в игре", callback_data="services")],

        [InlineKeyboardButton(text="🎓 Обучение GameGuardian", callback_data="gg_training")],

        [InlineKeyboardButton(text="💬 Написать в поддержку", callback_data="support")]

    ])
        
def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Новые заказы", callback_data="admin_new")],
        [InlineKeyboardButton(text="✅ Готовые", callback_data="admin_done")],
        [InlineKeyboardButton(text="📊 Аналитика", callback_data="analytics")]

    ])
    
# =====================================================
# GAMEGUARDIAN TRAINING START
# =====================================================

@dp.callback_query(F.data == "gg_training")
async def gg_training(call: CallbackQuery):

    index = 0
    g = GG_TRAINING[index]

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back_menu"),
            InlineKeyboardButton(text="➡ Далее", callback_data="gg_next:0")
        ],

        [InlineKeyboardButton(text="💳 Купить", callback_data="buy_gg:0")],

        [
            InlineKeyboardButton(
                text="📖 Полное описание",
                web_app=WebAppInfo(url=g["url"])
            )
        ],

        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]

    ])

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(g["photo"]),
            caption=g["text"]
        ),
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("gg_next:"))
async def gg_next(call: CallbackQuery):

    index = int(call.data.split(":")[1]) + 1

    if index >= len(GG_TRAINING):
        index = len(GG_TRAINING) - 1

    g = GG_TRAINING[index]

    buttons = []

    if index == 1:
        buttons.append([
            InlineKeyboardButton(text="⬅ Назад", callback_data="gg_prev:1")
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        *buttons,
        [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_gg:{index}")],
        [
            InlineKeyboardButton(
                text="📖 Полное описание",
                web_app=WebAppInfo(url=g["url"])
            )
        ],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]
    ])

    media = InputMediaPhoto(
        media=FSInputFile(g["photo"]),
        caption=g["text"]
    )

    await call.message.edit_media(
        media=media,
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("gg_prev:"))
async def gg_prev(call: CallbackQuery):

    index = int(call.data.split(":")[1]) - 1

    if index < 0:
        index = 0

    g = GG_TRAINING[index]

    kb = InlineKeyboardMarkup(inline_keyboard=[

        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back_menu"),
            InlineKeyboardButton(text="➡ Далее", callback_data="gg_next:0")
        ],

        [InlineKeyboardButton(text="💳 Купить", callback_data=f"buy_gg:{index}")],

        [
            InlineKeyboardButton(
                text="📖 Полное описание",
                web_app=WebAppInfo(url=g["url"])
            )
        ],

        [InlineKeyboardButton(text="🏠 Меню", callback_data="back_menu")]

    ])

    media = InputMediaPhoto(
        media=FSInputFile(g["photo"]),
        caption=g["text"]
    )

    await call.message.edit_media(
        media=media,
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("buy_gg:"))
async def buy_gg(call: CallbackQuery):

    index = int(call.data.split(":")[1])

    g = GG_TRAINING[index]

    name = g["name"]
    price = g["price"]

    order_id = create_order(
        call.from_user.id,
        call.from_user.username,
        call.from_user.first_name,
        name,
        "training",
        price
    )

    prices = [LabeledPrice(label=name, amount=price)]

    await bot.send_invoice(
        call.from_user.id,
        title=name,
        description="Покупка обучения GameGuardian",
        payload=f"order_{order_id}",
        provider_token="",
        currency="XTR",
        prices=prices
    )
# =====================================================
# SETS START
# =====================================================

@dp.callback_query(F.data == "sets")
async def sets_start(call: CallbackQuery):

    log_visit(call.from_user.id)

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

    user_id = message.from_user.id
    name = message.from_user.first_name

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY
    )
    """)

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    # записываем посещение
    cursor.execute(
        "INSERT INTO visits(user_id,date) VALUES(?,?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"))
    )

    conn.commit()
    conn.close()

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
"""AF Bot — Главное меню

🚘 Прокачай свой аккаунт в игре Car Parking.

Выбери услугу, наборы
или задай свой вопрос ниже 👇""",
        reply_markup=main_menu()
    )

    await call.answer()

# ============================================================
# ANALYTICS TODAY
# ============================================================

@dp.callback_query(F.data == "analytics")
async def analytics(call: CallbackQuery):

    # пользователи
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    # активные сегодня
    cursor.execute("""
    SELECT COUNT(DISTINCT user_id)
    FROM visits
    WHERE date(date)=date('now')
    """)
    active_today = cursor.fetchone()[0]

    # заказы сегодня (оплаченные)
    cursor.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE status='new'
    AND date(date)=date('now')
    """)
    orders_today = cursor.fetchone()[0]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
        ]
    )

    await call.message.edit_text(
f"""📊 Аналитика

👥 Пользователей: {users}

🔥 Активных сегодня: {active_today}

📦 Заказов сегодня: {orders_today}
""",
        reply_markup=kb
    )
    
# ============================================================
# SERVICES
# ============================================================

@dp.callback_query(F.data=="services")
async def services(call:CallbackQuery):

    log_visit(call.from_user.id)

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

@dp.callback_query(F.data=="support")
async def support(call: CallbackQuery, state: FSMContext):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )

    await call.message.edit_text(
"""💬 Поддержка

Напишите ваше сообщение прямо в чат.

Опишите проблему максимально подробно,
чтобы мы могли быстрее помочь.""",
        reply_markup=kb
    )

    await state.set_state(AskState.waiting_question)
@dp.message(AskState.waiting_question)
async def receive_question(message: Message, state: FSMContext):

    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Ответить", callback_data=f"reply_support_{user_id}")]
        ]
    )

    admin_msg = await bot.send_message(
        ADMIN_ID,
        f"""📩 Сообщение в поддержку

👤 Пользователь: @{username}
🆔 ID: {user_id}

💬 Сообщение:
{text}
""",
        reply_markup=kb
    )

    # сообщение пользователю
    sent = await message.answer(
"""✅ Сообщение отправлено в поддержку.

Ожидайте ответа администратора."""
    )

    await state.clear()

    # очищаем чат через 2 секунды
    await asyncio.sleep(2)

    try:
        await message.delete()
    except:
        pass

    try:
        await sent.delete()
    except:
        pass

# ============================================================
# PAYMENT
# ============================================================

@dp.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def payment(message: Message):

    global ADMIN_ORDERS_COUNT

    payload = message.successful_payment.invoice_payload

    try:
        order_id = int(payload.split("_")[1])
    except:
        await message.answer("❗ Ошибка обработки платежа.")
        return

    cursor.execute(
        "SELECT * FROM orders WHERE id=?",
        (order_id,)
    )
    order = cursor.fetchone()

    if not order:
        await message.answer("❗ Заказ не найден.")
        return

    # меняем статус заказа
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

    # чек пользователю
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
Ожидайте выполнения услуги.
"""
    )

    # увеличиваем счетчик заказов
    ADMIN_ORDERS_COUNT += 1

    # обновляем сообщение админа
    await update_admin_orders()


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

    await call.message.delete()

    await call.answer("Заказ добавлен в новые")

@dp.callback_query(F.data == "accept_all_orders")
async def accept_all_orders(call: CallbackQuery):

    global ADMIN_ORDERS_COUNT
    global ADMIN_ORDERS_MESSAGE_ID

    cursor.execute(
        "UPDATE orders SET status='new' WHERE status='new'"
    )
    db.commit()

    try:
        await bot.delete_message(
            ADMIN_ID,
            ADMIN_ORDERS_MESSAGE_ID
        )
    except:
        pass

    ADMIN_ORDERS_MESSAGE_ID = None
    ADMIN_ORDERS_COUNT = 0

    await call.answer("Все заказы приняты")

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
        await call.message.edit_text(
            text,
            reply_markup=main_menu()
        )
    except:
        # если вдруг сообщение не редактируется
        await call.message.delete()
        await call.message.answer(
            text,
            reply_markup=main_menu()
        )

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

# ============================================================
# DOWNLOAD DATABASE
# ============================================================

@dp.message(Command("db"))
async def send_db(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    file = FSInputFile("bot.db")
    await message.answer_document(file)
    
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
# ADMIN ORDER NOTIFICATION
# ============================================================

async def update_admin_orders():

    global ADMIN_ORDERS_MESSAGE_ID
    global ADMIN_ORDERS_COUNT

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять", callback_data="accept_all_orders")]
        ]
    )

    text = f"📥 Новые заказы: {ADMIN_ORDERS_COUNT}"

    if ADMIN_ORDERS_MESSAGE_ID is None:

        msg = await bot.send_message(
            ADMIN_ID,
            text,
            reply_markup=kb
        )

        ADMIN_ORDERS_MESSAGE_ID = msg.message_id

    else:

        await bot.edit_message_text(
            text,
            ADMIN_ID,
            ADMIN_ORDERS_MESSAGE_ID,
            reply_markup=kb
        )

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

@dp.callback_query(F.data.startswith("reply_") & ~F.data.startswith("reply_support_"))
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
    reply_msg = await bot.send_message(
    user_id,
    f"""📩 Ответ 

{message.text}

⬇ Нажмите кнопку ниже чтобы очистить чат и вернуться в меню""",
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

    # готовые заказы сегодня
    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE status='done' AND date(date)=date('now')"
    )
    today_done = cursor.fetchone()[0]

    # готовые заказы за всё время
    cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE status='done'"
    )
    all_done = cursor.fetchone()[0]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
    ])

    await call.message.edit_text(
f"""✅ Готовые заказы

📅 Сегодня: {today_done}
📊 За всё время: {all_done}
""",
        reply_markup=kb
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

class SupportReply(StatesGroup):
    waiting_text = State()


@dp.callback_query(F.data.startswith("reply_support_"))
async def support_reply(call: CallbackQuery, state: FSMContext):

    user_id = int(call.data.split("_")[2])

    msg = await bot.send_message(
        ADMIN_ID,
        "✍️ Напишите ответ пользователю"
    )

    await state.update_data(
        user_id=user_id,
        reply_msg=msg.message_id,
        support_msg=call.message.message_id
    )

    await state.set_state(SupportReply.waiting_text)

@dp.message(SupportReply.waiting_text)
async def support_send(message: Message, state: FSMContext):

    data = await state.get_data()

    user_id = data.get("user_id")
    reply_msg = data.get("reply_msg")
    support_msg = data.get("support_msg")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Закрыть", callback_data="close_support")]
        ]
    )

    # отправляем ответ пользователю
    sent = await bot.send_message(
        user_id,
        f"""📩 Ответ поддержки

{message.text}""",
        reply_markup=kb
    )

    await state.clear()

    # удаляем ответ админа
    try:
        await message.delete()
    except:
        pass

    # удаляем сообщение "Напишите ответ"
    try:
        await bot.delete_message(ADMIN_ID, reply_msg)
    except:
        pass

    # удаляем сообщение поддержки
    try:
        await bot.delete_message(ADMIN_ID, support_msg)
    except:
        pass
        
@dp.callback_query(F.data == "close_support")
async def close_support(call: CallbackQuery):

    try:
        await call.message.delete()
    except:
        pass

    await call.answer()
    
@dp.callback_query(F.data=="none")
async def none(call: CallbackQuery):
    await call.answer("Заказов нет")
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())

























































































