import requests
from celery import shared_task
from helpers.tg_bot_msgs import send_msg

@shared_task
def signal_run_parser():
    url = "http://172.24.48.1:8000/api/run-parser/"
    try:
        resp = requests.post(url, json={"code": "6start6"})
        resp.raise_for_status()
    except Exception as e:
        print(f"API call failed: {e}")


@shared_task
def send_telegram_report():
    try:
        send_msg()
    except Exception as e:
        print(f"Telegram bot call failed: {e}")