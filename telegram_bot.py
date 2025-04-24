import telebot
import os
from helpers.tg_bot_msgs import get_report_text

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_unread_report(chat_id):
    text = get_report_text()
    bot.send_message(chat_id, text)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю! 👋\nЯ бот для звітів про непрочитані повідомлення.\n"
        "Надішліть /report, щоб отримати актуальний звіт."
    )


@bot.message_handler(commands=['report'])
def handle_report(message):
    send_unread_report(message.chat.id)
import telebot
import os
from helpers.tg_bot_msgs import get_report_text

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_unread_report(chat_id):
    try:
        text = get_report_text()
        bot.send_message(chat_id, text)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Сталася помилка при формуванні звіту:\n{e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        bot.send_message(
            message.chat.id,
            "Вітаю! 👋\nЯ бот для звітів про непрочитані повідомлення.\n"
            "Надішліть /report, щоб отримати актуальний звіт."
        )
    except Exception as e:
        print(e)

@bot.message_handler(commands=['report'])
def handle_report(message):
    send_unread_report(message.chat.id)

bot.polling(none_stop=True)
