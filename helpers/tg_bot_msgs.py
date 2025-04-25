import requests
import os
import telebot
from datetime import timezone, timedelta
from dateutil import parser

def get_report_text() -> str:
    API_BASE_URL = os.getenv("API_BASE_URL", "")
    url = f"{API_BASE_URL}/api/get-unread-report/"
    data = requests.get(url).json()
     # Обробка дати
    updated_at_raw = data.get('updated_at', '')
    updated_at_str = '---'
    if updated_at_raw:
        try:
            dt_utc = parser.isoparse(updated_at_raw)
            kyiv_time = dt_utc.astimezone(timezone(timedelta(hours=3)))
            updated_at_str = kyiv_time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            updated_at_str = updated_at_raw

    text = "📊 **Звіт про непрочитані повідомлення**\n"
    text += f"Оновлено: {updated_at_str}\n\n"
    text += f"🔔 Пропущені дзвінки: {data.get('missed_calls', 0)}\n"
    text += f"❗ Втрачені дзвінки: {data.get('lost_calls', 0)}\n\n"
    text += "💬 Непрочитані чати по каналах:\n"
    crm = data.get("crm", [])
    for channel in crm:
        for name, unread in channel.items():
            text += f"• {name}: {unread}\n"
    return text


def send_msg():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    text = get_report_text()
    bot.send_message(CHAT_ID, text)