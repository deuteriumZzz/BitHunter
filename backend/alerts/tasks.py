import telegram
import os
from celery import shared_task
from django.conf import settings
from .models import UserProfile

@shared_task
def send_message(user, message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return
    profile = UserProfile.objects.get(user=user)
    chat_id = profile.telegram_chat_id
    if not chat_id:
        return
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)
