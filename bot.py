import requests
from flask import Flask, request

# === Настройки ===
TELEGRAM_TOKEN = "8412172576:AAGQwxT7b7bap-sClTpy3jIfZrXYLkD6eZc"
NOTION_TOKEN = "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"
DATABASE_ID = "2508ece1030a80d69b59e3b8ec3d5b22"

app = Flask(__name__)

# Хранилище состояния пользователей
user_states = {}

# Функция добавления данных в Notion
def add_to_notion(order):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Имя": {"title": [{"text": {"content": order.get("name","")}}]},
            "Телефон": {"rich_text": [{"text": {"content": order.get("phone","")}}]},
            "Детали поездки": {"rich_text": [{"text": {"content": order.get("trip","")}}]}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

# Отправка сообщений в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# Webhook от Telegram
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" not in data or "text" not in data["message"]:
        return "OK"
    
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"].strip()

    # Обработка команды /start
    if text == "/start":
        user_states[chat_id] = {"step": 1, "order": {}}
        send_message(chat_id, "Привет! Я бот Helsinki_Transferbot. Давай оформим твой заказ.\nКак вас зовут?")
        return "OK"

    # Если пользователь новый, создаём пустой заказ
    if chat_id not in user_states:
        user_states[chat_id] = {"step": 1, "order": {}}
        send_message(chat_id, "Привет! Как вас зовут?")
        return "OK"

    # Пошаговый диалог
    state = user_states[chat_id]

    if state["step"] == 1:
        state["order"]["name"] = text
        send_message(chat_id, "Укажите номер телефона:")
        state["step"] += 1
    elif state["step"] == 2:
        state["order"]["phone"] = text
        send_message(chat_id, "Опишите детали поездки (откуда → куда, дата, время):")
        state["step"] += 1
    elif state["step"] == 3:
        state["order"]["trip"] = text
        success = add_to_notion(state["order"])
        if success:
            send_message(chat_id, "✅ Ваш заказ добавлен в Notion!")
        else:
            send_message(chat_id, "❌ Ошибка при добавлении заказа.")
        del user_states[chat_id]

    return "OK"

# Главная страница для проверки работы сервиса
@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
