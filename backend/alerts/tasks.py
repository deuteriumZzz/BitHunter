import telegram
import os
import logging
from celery import shared_task
from django.conf import settings
from accounts.models import UserProfile
from .models import AlertRule, Notification
import ccxt

logger = logging.getLogger(__name__)

@shared_task
def send_message(user, message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set")
        return
    try:
        profile = UserProfile.objects.get(user=user)
        chat_id = profile.telegram_chat_id
        if not chat_id:
            logger.info(f"No chat_id for user {user.username}")
            return
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Message sent to {user.username}: {message}")
    except UserProfile.DoesNotExist:
        logger.error(f"UserProfile not found for user {user}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")

@shared_task
def check_alerts():
    exchange = ccxt.binance()
    try:
        for rule in AlertRule.objects.select_related('user').all():  # Оптимизация запроса
            ticker = exchange.fetch_ticker(rule.symbol)
            if ticker['last'] >= rule.threshold:
                notification = Notification.objects.create(
                    rule=rule, 
                    message=f'Alert for {rule.symbol}: price {ticker["last"]} reached threshold {rule.threshold}'
                )
                # Отправка уведомления в Telegram
                send_message.delay(rule.user, notification.message)
                logger.info(f"Alert triggered for {rule.symbol}")
    except Exception as e:
        logger.error(f"Error in check_alerts: {e}")
