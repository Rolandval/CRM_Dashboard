import telebot
import os
import django
import sys
from datetime import datetime

# Налаштування Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Імпортуємо модель після налаштування Django
from app.models import TelegramMSGS

TELEGRAM_TOKEN = os.getenv("TELEGRAM_REQ_TOKEN")
TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID"))
FINISHED_GROUP_ID = int(os.getenv("FINISHED_GROUP_ID"))

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: message.chat.id == TARGET_GROUP_ID)
def handle_group_messages(message):
    """Обробник повідомлень з цільової групи"""
    try:
        # Зберігаємо повідомлення в базу даних
        TelegramMSGS.objects.create(text=message.text)
        print(f"Збережено повідомлення: {message.text[:50]}...")
    except Exception as e:
        print(f"Помилка при збереженні повідомлення: {e}")


@bot.message_handler(func=lambda message: message.chat.id == FINISHED_GROUP_ID)
def check_group_messages(message):
    """Обробник повідомлень з цільової групи"""
    try:
        # Отримуємо текст повідомлення
        search_text = message.text
        # Знаходимо всі збережені повідомлення
        saved_messages = TelegramMSGS.objects.all()
        
        deleted_count = 0
        # Перевіряємо кожне збережене повідомлення
        for saved_msg in saved_messages:
            if search_text in saved_msg.text:
                # Зберігаємо текст перед видаленням для логування
                msg_preview = saved_msg.text[:50] + "..." if len(saved_msg.text) > 50 else saved_msg.text
                # Видаляємо повідомлення
                saved_msg.delete()
                deleted_count += 1
                print(f"Видалено повідомлення: {msg_preview}")
        
        if deleted_count > 0:
            print(f"Видалено {deleted_count} повідомлень, що містять вказаний текст.")
        else:
            print("Не знайдено повідомлень з вказаним текстом.")
            
    except Exception as e:
        print(f"Помилка при обробці повідомлення: {e}")
        bot.reply_to(message, f"Виникла помилка: {str(e)}")


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю! 👋\nЯ бот для звітів про непрочитані повідомлення.\n"
    )


bot.polling(none_stop=True)
