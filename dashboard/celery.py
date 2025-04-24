import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

app = Celery('dashboard')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'signal-run-parser-every-10-minutes': {
        'task': 'app.tasks.signal_run_parser',
        'schedule': crontab(minute='*/10'),
    },
    'send-telegram-report-every-day-17-12': {
        'task': 'app.tasks.send_telegram_report',
        'schedule': crontab(minute=5, hour=19),
    },
}
