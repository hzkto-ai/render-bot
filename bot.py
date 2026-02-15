import requests
import time
import json
import os

TOKEN = "8320881686:AAEQMJ3qdadlEP3KqEoIsGXFiRzJmFCL080"
ADMIN_ID = 7233660707
ADMIN_USERNAME = "hzkto_ai"
CARD_NUMBER = "2204320682939709"
PHONE_NUMBER = "+79523030942"

# Ссылка на мини‑приложение (GitHub Pages)
WEBAPP_URL = "https://hzkto-ai.github.io/uc-shop-app"

PRODUCTS = {
    "60 UC": 80,
    "325 UC": 400,
    "660 UC": 800,
    "985 UC": 1210,
    "1310 UC": 1588,
    "1800 UC": 1956,
    "3850 UC": 4100,
    "5650 UC": 5950,
    "8100 UC": 7900,
    "11950 UC": 12000,
    "16200 UC": 16600,
    "24300 UC": 23500
}

orders = {}
last_update_id = 0

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def edit_message(chat_id, msg_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

print("✅ Бот запущен на Render.com")
print(f"🌐 Магазин: {WEBAPP_URL}")
print(f"👤 Админ: @{ADMIN_USERNAME}")

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        response = requests.get(url, params={
            "offset": last_update_id + 1,
            "timeout": 30
        }, timeout=35)
        
        if response.status_code == 200:
            data = response.json()
            for update in data.get("result", []):
                last_update_id = update["update_id"]
                
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    
                    if text == "/start":
                        welcome = "🎮 <b>Добро пожаловать в магазин UC для PUBG Mobile!</b>\n\n"
                        welcome += f"Привет, {msg['from'].get('first_name', '')}! 👋\n\n"
                        welcome += "💰 <b>Цены за 1 пак:</b>\n"
                        for p, pr in PRODUCTS.items():
                            welcome += f"• {p} — {pr} руб\n"
                        
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "🌐 ОТКРЫТЬ МАГАЗИН", "web_app": {"url": WEBAPP_URL}}],
                                [{"text": "📋 Реквизиты", "callback_data": "payment"}],
                                [{"text": "ℹ️ Помощь", "callback_data": "help"}]
                            ]
                        }
                        send_message(chat_id, welcome, keyboard)
                    
                    elif "web_app_data" in msg:
                        try:
                            data_from_app = json.loads(msg["web_app_data"]["data"])
                            print("📦 Заказ из магазина:", data_from_app)
                            
                            if data_from_app["action"] == "buy":
                                product = data_from_app["product"]
                                quantity = data_from_app["quantity"]
                                total = data_from_app["total"]

                                orders[chat_id] = {
                                    "product": product,
                                    "quantity": quantity,
                                    "total": total,
                                    "awaiting_id": True
                                }

                                text = (
                                    f"✅ <b>ЗАКАЗ ПОЛУЧЕН!</b>\n\n"
                                    f"📦 Товар: {product}\n"
                                    f"🔢 Количество: {quantity} шт\n"
                                    f"💰 Сумма к оплате: {total} руб\n\n"
                                    f"💳 <b>РЕКВИЗИТЫ ОЗОН БАНК:</b>\n"
                                    f"<code>{CARD_NUMBER}</code>\n"
                                    f"📞 {PHONE_NUMBER}\n\n"
                                    f"⚠️ <b>ДАЛЬНЕЙШИЕ ДЕЙСТВИЯ:</b>\n"
                                    f"1️⃣ Переведите <b>{total} руб</b> на карту выше\n"
                                    f"2️⃣ <b>Напишите в этот чат ваш ИГРОВОЙ ID</b>\n"
                                    f"3️⃣ После этого отправьте ФОТО ЧЕКА\n\n"
                                    f"⏱ Ожидайте подтверждения от администратора."
                                )
                                send_message(chat_id, text)
                        except Exception as e:
                            print("Ошибка обработки данных из магазина:", e)
                    
                    elif chat_id in orders and orders[chat_id].get("awaiting_id") and text and not text.startswith("/"):
                        orders[chat_id]["game_id"] = text.strip()
                        orders[chat_id]["awaiting_id"] = False
                        orders[chat_id]["awaiting_photo"] = True
                        
                        send_message(chat_id, 
                            "✅ <b>ИГРОВОЙ ID СОХРАНЁН!</b>\n\n"
                            f"<code>{text.strip()}</code>\n\n"
                            "📸 <b>ТЕПЕРЬ ОТПРАВЬТЕ ФОТО ЧЕКА</b>\n"
                            "Пришлите фото перевода одним сообщением."
                        )
                    
                    elif "photo" in msg and chat_id in orders:
                        file_id = msg["photo"][-1]["file_id"]
                        
                        if "game_id" not in orders[chat_id]:
                            send_message(chat_id, 
                                "❌ <b>ОШИБКА ПОРЯДКА ДЕЙСТВИЙ</b>\n\n"
                                "🔴 <b>СНАЧАЛА НАПИШИТЕ ИГРОВОЙ ID!</b>\n\n"
                                "1️⃣ Напишите свой ID в чат\n"
                                "2️⃣ ТОЛЬКО ПОТОМ отправляйте чек"
                            )
                            continue
                        
                        admin_text = (
                            f"🔔 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
                            f"👤 Покупатель: @{msg['from'].get('username', 'Нет')}\n"
                            f"🆔 ID: <code>{orders[chat_id]['game_id']}</code>\n"
                            f"📦 Товар: {orders[chat_id]['product']}\n"
                            f"🔢 Количество: {orders[chat_id]['quantity']} шт\n"
                            f"💰 Сумма: {orders[chat_id]['total']} руб\n"
                        )
                        
                        admin_keyboard = {
                            "inline_keyboard": [
                                [{"text": "✅ Подтвердить", "callback_data": f"confirm_{chat_id}"}],
                                [{"text": "❌ Отклонить", "callback_data": f"reject_{chat_id}"}]
                            ]
                        }
                        
                        url_photo = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                        requests.post(url_photo, json={
                            "chat_id": ADMIN_ID,
                            "photo": file_id,
                            "caption": admin_text,
                            "parse_mode": "HTML",
                            "reply_markup": admin_keyboard
                        }, timeout=10)
                        
                        send_message(chat_id, 
                            "✅ <b>Чек получен!</b>\n\n"
                            "Заказ передан администратору.\n"
                            "Ожидайте подтверждения в течение 5–15 минут."
                        )
                        
                        orders[chat_id]["awaiting_photo"] = False
                
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    data = cb["data"]
                    chat_id = cb["message"]["chat"]["id"]
                    msg_id = cb["message"]["message_id"]
                    user_id = cb["from"]["id"]
                    
                    if data == "payment":
                        text = (
                            f"💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ</b>\n\n"
                            f"🏦 Банк: Озон Банк\n"
                            f"💳 Карта: <code>{CARD_NUMBER}</code>\n"
                            f"📞 Телефон: <code>{PHONE_NUMBER}</code>"
                        )
                        edit_message(chat_id, msg_id, text, 
                            {"inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]}
                        )
                    
                    elif data == "help":
                        text = (
                            f"ℹ️ <b>ПОМОЩЬ</b>\n\n"
                            f"1️⃣ Открой магазин\n"
                            f"2️⃣ Выбери товар и количество\n"
                            f"3️⃣ Оплати на карту\n"
                            f"4️⃣ Напиши игровой ID\n"
                            f"5️⃣ Отправь фото чека\n\n"
                            f"⏱ Выдача: 5-15 мин после подтверждения\n"
                            f"👤 Поддержка: @{ADMIN_USERNAME}"
                        )
                        edit_message(chat_id, msg_id, text,
                            {"inline_keyboard": [[{"text": "🔙 Назад", "callback_data": "back"}]]}
                        )
                    
                    elif data.startswith("confirm_") and user_id == ADMIN_ID:
                        user = int(data[8:])
                        if user in orders:
                            game_id = orders[user].get('game_id', 'Не указан')
                            product = orders[user].get('product', '')
                            quantity = orders[user].get('quantity', 1)
                            total = orders[user].get('total', 0)
                            
                            send_message(user,
                                "✅ <b>ЗАКАЗ ПОДТВЕРЖДЁН!</b>\n\n"
                                f"📦 Товар: {product}\n"
                                f"🔢 Количество: {quantity} шт\n"
                                f"💰 Сумма: {total} руб\n"
                                f"🆔 ID: <code>{game_id}</code>\n\n"
                                f"UC будет выдан в ближайшее время!"
                            )
                            
                            del orders[user]
                            
                            try:
                                requests.post(
                                    f"https://api.telegram.org/bot{TOKEN}/editMessageCaption",
                                    json={
                                        "chat_id": ADMIN_ID,
                                        "message_id": cb["message"]["message_id"],
                                        "caption": cb["message"]["caption"] + "\n\n✅ ПОДТВЕРЖДЁНО"
                                    },
                                    timeout=10
                                )
                            except:
                                pass
                    
                    elif data.startswith("reject_") and user_id == ADMIN_ID:
                        user = int(data[7:])
                        
                        send_message(user,
                            "❌ <b>ЗАКАЗ ОТКЛОНЁН</b>\n\n"
                            f"Проверьте правильность оплаты или свяжитесь с @{ADMIN_USERNAME}"
                        )
                        
                        if user in orders:
                            del orders[user]
                        
                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN}/editMessageCaption",
                                json={
                                    "chat_id": ADMIN_ID,
                                    "message_id": cb["message"]["message_id"],
                                    "caption": cb["message"]["caption"] + "\n\n❌ ОТКЛОНЁНО"
                                },
                                timeout=10
                            )
                        except:
                            pass
                    
                    elif data == "back":
                        welcome = "🏠 <b>Главное меню</b>"
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "🌐 ОТКРЫТЬ МАГАЗИН", "web_app": {"url": WEBAPP_URL}}],
                                [{"text": "📋 Реквизиты", "callback_data": "payment"}],
                                [{"text": "ℹ️ Помощь", "callback_data": "help"}]
                            ]
                        }
                        edit_message(chat_id, msg_id, welcome, keyboard)
                    
                    requests.post(
                        f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                        json={"callback_query_id": cb["id"]},
                        timeout=10
                    )
        
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)