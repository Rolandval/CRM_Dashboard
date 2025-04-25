import requests
from celery import shared_task
from helpers.tg_bot_msgs import send_msg
import os


@shared_task
def signal_run_parser():
    API_BASE_URL = os.getenv("API_BASE_URL", "")
    url = f"{API_BASE_URL}/api/run-parser/"
    try:
        resp = requests.post(url, json={"code": "6start6"})
        resp.raise_for_status()
    except Exception as e:
        print(f"API call failed: {e}")
        print(f"API call failed: {e}")


@shared_task
def send_telegram_report():
    try:
        send_msg()
    except Exception as e:
        print(f"Telegram bot call failed: {e}")