import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
from config import TOKEN, ADMIN_ID, DB_FILE, PROMOCODES, CITIES
from list import PRODUCTS
from db import read_db, write_db, get_user, create_user, update_user

bot = telebot.TeleBot(TOKEN)

def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🛍️ Ассортимент", callback_data="catalog"))
    kb.add(InlineKeyboardButton("💰 Баланс", callback_data="balance"))
    kb.add(InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
    return kb

def catalog_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    for pid, product in PRODUCTS.items():
        kb.add(InlineKeyboardButton(f"👕 {product['name']} — {product['price']} ₽", callback_data=f"product_{pid}"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
    return kb

def product_detail_menu(product_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✅ Купить", callback_data=f"buy_{product_id}"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="catalog"))
    return kb

def balance_menu(user_id):
    user = get_user(user_id)
    if user is None:
        balance = 0
    else:
        balance = user[3]
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("💳 Пополнить баланс", callback_data="deposit"))
    kb.add(InlineKeyboardButton("🎟️ Промокоды", callback_data="promocodes"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
    return kb, balance

def deposit_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🏦 СБП (авто)", callback_data="deposit_sbp"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="balance"))
    return kb

def settings_menu(user_id):
    user = get_user(user_id)
    if user is None:
        city = "Сургут"
        name = ""
        lastname = ""
    else:
        name, lastname, city, _ = user
    text = (f"⚙️ Настройки\n\n"
            f"Имя: {name if name else 'не указано'}\n"
            f"Фамилия: {lastname if lastname else 'не указано'}\n"
            f"Город: {city}")
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("✏️ Изменить имя", callback_data="change_name"))
    kb.add(InlineKeyboardButton("✏️ Изменить фамилию", callback_data="change_lastname"))
    kb.add(InlineKeyboardButton("📍 Сменить город", callback_data="change_city"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
    return text, kb

def cities_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    for city in CITIES:
        kb.add(InlineKeyboardButton(f"🏙️ {city}", callback_data=f"city_{city}"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="settings"))
    return kb

def promocode_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🎟️ Ввести промокод", callback_data="enter_promo"))
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="balance"))
    return kb

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    if get_user(user_id) is None:
        create_user(user_id, "", "", "Сургут", 0)
    photo_path = "photos/shop_cover.png"
    caption = f"👋 Добро пожаловать в наш шоп, {message.from_user.first_name}!"
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, caption, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    message = call.message
    def edit_text(text, markup):
        if message.content_type == "photo":
            bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, caption=text, reply_markup=markup)
        else:
            bot.edit_message_text(text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
    if data == "catalog" and message.content_type == "photo":
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "🛍️ Наш ассортимент:", reply_markup=catalog_menu())
        return

    if data == "back_main" and message.content_type == "photo":
        bot.delete_message(message.chat.id, message.message_id)
        photo_path = "photos/shop_cover.png"
        caption = f"👋 Добро пожаловать, {call.from_user.first_name}!"
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption, reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, caption, reply_markup=main_menu())
        return
    if data == "back_main":
        edit_text(f"👋 Добро пожаловать, {call.from_user.first_name}!", main_menu())
    elif data == "catalog":
        edit_text("🛍️ Ассортимент:", catalog_menu())
    elif data == "balance":
        kb, balance = balance_menu(user_id)
        edit_text(f"💰 Баланс: {balance} ₽", kb)
    elif data == "settings":
        text, kb = settings_menu(user_id)
        edit_text(text, kb)
    elif data.startswith("product_"):
        pid = data.split("_")[1]
        p = PRODUCTS[pid]
        if os.path.exists(p["photo"]):
            with open(p["photo"], 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f"🎽 {p['name']}\n💰 {p['price']} ₽\n📝 {p['description']}", reply_markup=product_detail_menu(pid))
                bot.delete_message(message.chat.id, message.message_id)
        else:
            edit_text(f"🎽 {p['name']}\n💰 {p['price']} ₽\n📝 {p['description']}", product_detail_menu(pid))
    elif data.startswith("buy_"):
        pid = data.split("_")[1]
        p = PRODUCTS[pid]
        user = get_user(user_id)
        if user is None:
            bot.answer_callback_query(call.id, "❌ Ошибка: пользователь не найден.")
            return
        balance = user[3]
        if balance >= p["price"]:
            new_balance = balance - p["price"]
            update_user(user_id, balance=new_balance)
            bot.answer_callback_query(call.id, f"✅ Куплено: {p['name']}")
            bot.send_message(message.chat.id, f"✅ Вы купили {p['name']} за {p['price']} ₽.\nОстаток: {new_balance} ₽")
            bot.send_message(ADMIN_ID, f"🛒 ПОКУПКА\n@{call.from_user.username or call.from_user.first_name}\nТовар: {p['name']}\nЦена: {p['price']} ₽")
        else:
            bot.answer_callback_query(call.id, f"❌ Не хватает {p['price'] - balance} ₽")
    elif data == "deposit":
        edit_text("💳 Способ пополнения:", deposit_menu())
    elif data == "deposit_sbp":
        msg = bot.send_message(message.chat.id, "💰 Введите сумму (руб):")
        bot.register_next_step_handler(msg, process_sbp_amount, user_id)
    elif data.startswith("check_sbp_"):
        code = data.split("_")[-1]
        if not hasattr(bot, 'sbp_requests'):
            bot.sbp_requests = {}
        if code in bot.sbp_requests and not bot.sbp_requests[code].get("used", False):
            amount = bot.sbp_requests[code]["amount"]
            user_id_req = bot.sbp_requests[code]["user_id"]
            if user_id_req == user_id:
                user = get_user(user_id)
                if user:
                    new_balance = user[3] + amount
                    update_user(user_id, balance=new_balance)
                    bot.sbp_requests[code]["used"] = True
                    bot.answer_callback_query(call.id, f"✅ Зачислено {amount} ₽!")
                    kb, new_bal = balance_menu(user_id)
                    edit_text(f"💰 Баланс: {new_bal} ₽", kb)
                else:
                    bot.answer_callback_query(call.id, "❌ Пользователь не найден.")
            else:
                bot.answer_callback_query(call.id, "❌ Неверный код заявки.")
        else:
            bot.answer_callback_query(call.id, "❌ Заявка не найдена или уже использована.")
    elif data == "promocodes":
        edit_text("🎟️ Здесь вы можете получить бонусы за промокоды!", promocode_menu())
    elif data == "enter_promo":
        msg = bot.send_message(message.chat.id, "Введите промокод:")
        bot.register_next_step_handler(msg, process_promocode)
    elif data == "change_city":
        edit_text("📍 Выберите город:", cities_menu())
    elif data.startswith("city_"):
        city = data.split("_", 1)[1]
        if city in CITIES:
            update_user(user_id, city=city)
            bot.answer_callback_query(call.id, f"Город изменён на {city}")
            text, kb = settings_menu(user_id)
            edit_text(text, kb)
        else:
            bot.answer_callback_query(call.id, "❌ Неверный город")
    elif data == "change_name":
        msg = bot.send_message(message.chat.id, "Введите ваше имя:")
        bot.register_next_step_handler(msg, process_name_change, user_id)
    elif data == "change_lastname":
        msg = bot.send_message(message.chat.id, "Введите вашу фамилию:")
        bot.register_next_step_handler(msg, process_lastname_change, user_id)

def process_name_change(m, user_id):
    name = m.text.strip()
    if name:
        update_user(user_id, name=name)
        bot.send_message(m.chat.id, f"✅ Имя изменено на {name}")
    else:
        bot.send_message(m.chat.id, "❌ Имя не может быть пустым.")
    text, kb = settings_menu(user_id)
    bot.send_message(m.chat.id, text, reply_markup=kb)

def process_lastname_change(m, user_id):
    lastname = m.text.strip()
    if lastname:
        update_user(user_id, lastname=lastname)
        bot.send_message(m.chat.id, f"✅ Фамилия изменена на {lastname}")
    else:
        bot.send_message(m.chat.id, "❌ Фамилия не может быть пустой.")
    text, kb = settings_menu(user_id)
    bot.send_message(m.chat.id, text, reply_markup=kb)

def process_sbp_amount(m, user_id):
    try:
        amount = int(m.text.strip())
        if amount < 10:
            bot.send_message(m.chat.id, "❌ Минимум 10 ₽")
            return
        code = str(random.randint(100000, 999999))
        if not hasattr(bot, 'sbp_requests'):
            bot.sbp_requests = {}
        bot.sbp_requests[code] = {"user_id": user_id, "amount": amount, "used": False}
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Проверить оплату", callback_data=f"check_sbp_{code}"))
        bot.send_message(m.chat.id, f"🏦 СБП на {amount} ₽\n\nКод заявки: {code}\n\nПосле оплаты нажмите кнопку ниже.\n(Демо-режим: деньги зачисляются мгновенно по кнопке)", reply_markup=kb)
    except:
        bot.send_message(m.chat.id, "❌ Введите число")

def process_promocode(m):
    user_id = m.from_user.id
    code = m.text.strip().upper()
    if code in PROMOCODES:
        bonus = PROMOCODES[code]
        user = get_user(user_id)
        if user:
            new_balance = user[3] + bonus
            update_user(user_id, balance=new_balance)
            bot.send_message(m.chat.id, f"✅ Промокод активирован! +{bonus} ₽ на баланс.")
        else:
            bot.send_message(m.chat.id, "❌ Ошибка пользователя.")
    else:
        bot.send_message(m.chat.id, "❌ Неверный промокод.")
    start_message(m)

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling() 