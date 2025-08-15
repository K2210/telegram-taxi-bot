import requests
from flask import Flask, request

# === Настройки ===
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
NOTION_TOKEN = "ВАШ_NOTION_INTEGRATION_TOKEN"
DATABASE_ID = "ВАШ_DATABASE_ID"

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
        r
