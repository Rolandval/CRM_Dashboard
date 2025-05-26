from django.db import models

class CRMModel(models.Model):
    channel_name = models.CharField(max_length=255)
    unread_chats = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.channel_name

class TelegramMSGS(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    