from celery import shared_task
from .models import Trade, Bot
from analytics.tasks import train_model_on_trade  # ДОБАВЛЕНО
import ccxt
from django.conf import settings

@shared_task
def place_trade(action, bot_id):
    """Разместить сделку и обучить модель."""
    bot = Bot.objects.get(id=bot_id)
    if settings.DEMO_MODE:
        # Симуляция
        price = 50000  # Фиктивная цена
        trade = Trade.objects.create(bot=bot, type='buy' if action == 1 else 'sell', amount=0.01, price=price)
    else:
        if action == 1:
            order = bot.exchange.create_market_buy_order('BTC/USDT', 0.01)
            trade = Trade.objects.create(bot=bot, type='buy', amount=0.01, price=order['price'])
        elif action == 2:
            order = bot.exchange.create_market_sell_order('BTC/USDT', 0.01)
            trade = Trade.objects.create(bot=bot, type='sell', amount=0.01, price=order['price'])
        else:
            return "Hold"

    # ДОБАВЛЕНО: Обучение после сделки
    trade_result = {'profit': trade.price * 0.01 if trade.type == 'sell' else -trade.price * 0.01}
    historical_data = [[trade.price, 1000]]
    news_data = ["Market news"]
    train_model_on_trade.delay(trade_result, historical_data, news_data)
    return f"Trade placed: {trade.type}"

@shared_task
def run_bot(bot_id):
    """Запустить бота с RL."""
    from analytics.tasks import predict_price
    action = predict_price.delay().get()
    place_trade.delay(action, bot_id)
    return "Bot run with RL prediction"
