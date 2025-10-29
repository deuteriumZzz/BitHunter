from celery import shared_task
from django.core.cache import cache
from django.conf import settings
import ccxt
import json
from alerts.models import AlertRule, Notification  # Импортируем модели из alerts.models
from django.utils import timezone

@shared_task
def check_alerts():
    alert_rules = AlertRule.objects.filter(is_active=True).select_related('user')
    for rule in alert_rules:
        price = get_current_price(rule.symbol)
        if price is None:
            continue
        triggered = False
        if rule.condition == 'above' and price > rule.value:
            triggered = True
        elif rule.condition == 'below' and price < rule.value:
            triggered = True
        elif rule.condition == 'change_percent':
            previous_price = cache.get(f'previous_price_{rule.symbol}')
            if previous_price:
                change = ((price - previous_price) / previous_price) * 100
                if abs(change) >= abs(rule.value):
                    triggered = True
        if triggered:
            message = f"Alert: {rule.symbol} {rule.condition} {rule.value}. Current price: {price}"
            notification = Notification.objects.create(
                user=rule.user,
                alert_rule=rule,
                message=message,
            )
            # Отправка уведомления (здесь можно добавить email или Telegram)
            print(f"Notification created: {notification}")
            cache.set(f'previous_price_{rule.symbol}', price, timeout=3600)

@shared_task
def send_notifications():
    notifications = Notification.objects.filter(is_sent=False)
    for notification in notifications:
        # Логика отправки (email, WebSocket и т.д.)
        print(f"Sending notification: {notification.message}")
        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save()

def get_current_price(symbol):
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None
