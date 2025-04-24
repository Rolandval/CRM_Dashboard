from django.core.management.base import BaseCommand
from helpers.crm_parser import update_crm_channels_in_db

class Command(BaseCommand):
    help = "Оновлює дані CRM каналів у базі"

    def handle(self, *args, **kwargs):
        update_crm_channels_in_db()