from celery import shared_task
from .models import Trade, Strategy  # Исправлено: Bot → Strategy
from analytics.tasks import train_model_on_trade  # ДОБАВЛЕНО
import ccxt
from django.conf import settings

@shared_task
def place_trade(action, strategy_id):  # Исправлено: bot_id → strategy_id
    """Разместить сделку и обучить модель."""
    strategy = Strategy.objects.get(id=strategy_id)  # Исправлено: Bot → Strategy, bot_id → strategy_id
    if settings.DEMO_MODE:
        # Симуляция
        price = 50000  # Фиктивная цена
        trade = Trade.objects.create(strategy=strategy, action='long' if action == 1 else 'short', amount=0.01, price=price)  # Исправлено: bot → strategy, type → action
    else:
        if action == 1:
            order = strategy.exchange.create_market_buy_order('BTC/USDT', 0.01)  # Исправлено: bot → strategy
            trade = Trade.objects.create(strategy=strategy, action='long', amount=0.01, price=order['price'])  # Исправлено: bot → strategy, type → action
        elif action == 2:
            order = strategy.exchange.create_market_sell_order('BTC/USDT', 0.01)  # Исправлено: bot → strategy
            trade = Trade.objects.create(strategy=strategy, action='short', amount=0.01, price=order['price'])  # Исправлено: bot → strategy, type → action
        else:
            return "Hold"

    # ДОБАВЛЕНО: Обучение после сделки
    trade_result = {'profit': trade.price * 0.01 if trade.action == 'short' else -trade.price * 0.01}  # Исправлено: type → action
    historical_data = [[trade.price, 1000]]
    news_data = ["Market news"]
    train_model_on_trade.delay(trade_result, historical_data, news_data)
    return f"Trade placed: {trade.action}"  # Исправлено: type → action

@shared_task
def run_bot(strategy_id):  # Исправлено: bot_id → strategy_id
    """Запустить бота с RL."""
    from analytics.tasks import predict_price
    action = predict_price.delay().get()
    place_trade.delay(action, strategy_id)  # Исправлено: bot_id → strategy_id
    return "Bot run with RL prediction"
