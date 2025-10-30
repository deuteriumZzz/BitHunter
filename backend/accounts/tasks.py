from celery import shared_task
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile
import requests
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_user_balance(user_id, amount):
    """
    Асинхронная задача для обновления баланса пользователя.
    Используй, например, после успешной сделки на бирже.

    :param user_id: ID пользователя
    :param amount: Сумма для добавления (может быть отрицательной)
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
        profile.balance += amount
        profile.save()
        logger.info(f"Updated balance for user {user.username}: +{amount}")
        # Опционально: отправить уведомление в Telegram
        send_telegram_notification.delay(user_id, f"Ваш баланс обновлен на {amount}. Текущий: {profile.balance}")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
    except Exception as e:
        logger.error(f"Error updating balance for user {user_id}: {str(e)}")

@shared_task
def send_telegram_notification(user_id, message):
    """
    Асинхронная задача для отправки уведомления в Telegram.
    Требует настроенного бота и токена в settings.py (например, TELEGRAM_BOT_TOKEN).

    :param user_id: ID пользователя
    :param message: Текст сообщения
    """
    try:
        user = User.objects.get(id=user_id)
        profile = user.userprofile
        if profile.telegram_chat_id:
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
            if not bot_token:
                logger.warning("TELEGRAM_BOT_TOKEN not set in settings")
                return
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': profile.telegram_chat_id,
                'text': message
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info(
                    f"Sent Telegram notification to user {user.username}"
                )
            else:
                logger.error(
                    f"Failed to send Telegram message: {response.text}"
                )
        else:
            logger.info(f"No Telegram Chat ID for user {user.username}")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")


@shared_task
def invalidate_profile_cache(user_id):
    """
    Асинхронная задача для инвалидации кэша профиля.
    Полезно после массовых обновлений.

    :param user_id: ID пользователя
    """
    cache_key = f'profile_{user_id}'
    cache.delete(cache_key)
    logger.info(f"Invalidated cache for profile {user_id}")
