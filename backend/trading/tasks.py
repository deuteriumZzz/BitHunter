"""
Модуль задач для Celery в приложении трейдинга.

Определяет асинхронные задачи для размещения трейдов (с симуляцией или реальными ордерами),
а также для запуска стратегий с предсказаниями RL-модели. Включает интеграцию с обучением модели.
"""

import ccxt

from celery import shared_task
from django.conf import settings

from .models import Strategy, Trade
from analytics.tasks import predict_price, train_model_on_trade


@shared_task
def place_trade(action, strategy_id):
    """
    Размещает трейд на основе действия и ID стратегии.

    В режиме демо симулирует трейд с фиктивной ценой. В реальном режиме создаёт ордер
    на бирже через ccxt. После размещения трейда запускает асинхронное обучение RL-модели
    с результатами, историческими данными и новостями.

    Параметры:
    - action (int): 1 для покупки (long), 2 для продажи (short), иначе hold.
    - strategy_id (int): ID стратегии.

    Возвращает:
    - str: Сообщение о размещённом трейде или "Hold".
    """
    strategy = Strategy.objects.get(id=strategy_id)
    if settings.DEMO_MODE:
        # Симуляция трейда
        price = 50000  # Фиктивная цена
        trade = Trade.objects.create(
            strategy=strategy,
            action='long' if action == 1 else 'short',
            amount=0.01,
            price=price
        )
    else:
        if action == 1:
            order = strategy.exchange.create_market_buy_order('BTC/USDT', 0.01)
            trade = Trade.objects.create(
                strategy=strategy,
                action='long',
                amount=0.01,
                price=order['price']
            )
        elif action == 2:
            order = strategy.exchange.create_market_sell_order('BTC/USDT', 0.01)
            trade = Trade.objects.create(
                strategy=strategy,
                action='short',
                amount=0.01,
                price=order['price']
            )
        else:
            return "Hold"

    # Обучение модели после размещения трейда
    trade_result = {'profit': trade.price * 0.01 if trade.action == 'short' else -trade.price * 0.01}
    historical_data = [[trade.price, 1000]]
    news_data = ["Market news"]
    train_model_on_trade.delay(trade_result, historical_data, news_data)
    return f"Trade placed: {trade.action}"


@shared_task
def run_bot(strategy_id):
    """
    Запускает стратегию с предсказанием RL-модели.

    Получает предсказание действия от RL-модели и асинхронно размещает трейд.

    Параметры:
    - strategy_id (int): ID стратегии.

    Возвращает:
    - str: Сообщение о запуске бота.
    """
    action = predict_price.delay().get()
    place_trade.delay(action, strategy_id)
    return "Bot run with RL prediction"

@shared_task
def calculate_metrics(strategy_id):
    """
    Рассчитывает метрики для указанной стратегии на основе её торгов.

    Получает все сделки (`Trade`) для стратегии, вычисляет ключевые метрики:
    - total_trades: Общее количество сделок.
    - win_rate: Процент выигрышных сделок (предполагаем, что profit > 0 — выигрыш).
    - total_profit: Общая прибыль/убыток.
    - avg_profit: Средняя прибыль на сделку.
    
    В демо-режиме использует симулированные прибыли (на основе цены). 
    В реальном режиме — предполагает, что в модели Trade есть поле 'profit' 
    (если нет, добавьте его в модель или доработайте расчёт).
    
    Если стратегия не найдена, возвращает ошибку.

    Параметры:
    - strategy_id (int): ID стратегии.

    Возвращает:
    - dict: Словарь с метриками или {'error': str} в случае ошибки.
    """
    try:
        strategy = Strategy.objects.get(id=strategy_id)
        trades = Trade.objects.filter(strategy=strategy)
        
        if not trades.exists():
            return {'error': 'No trades found for this strategy.'}
        
        total_trades = trades.count()
        profits = []
        
        for trade in trades:
            if settings.DEMO_MODE:
                # Симуляция прибыли: для long +1% от цены, для short -1% (упрощённо; доработайте по логике)
                if trade.action == 'long':
                    profit = trade.price * trade.amount * 0.01  # +1% прибыль
                elif trade.action == 'short':
                    profit = -trade.price * trade.amount * 0.01  # -1% убыток (или инвертируйте)
                else:
                    profit = 0
                # Если в модели нет поля profit, сохраните его здесь: trade.profit = profit; trade.save()
            else:
                # В реальном режиме: используйте реальный profit из ордера или модели
                profit = getattr(trade, 'profit', 0)  # Предполагаем поле 'profit' в модели Trade
            
            profits.append(profit)
        
        wins = sum(1 for p in profits if p > 0)
        total_profit = sum(profits)
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'total_profit': round(total_profit, 2),
            'avg_profit': round(avg_profit, 2),
            'strategy_name': strategy.name  # Дополнительно, для удобства
        }
    
    except Strategy.DoesNotExist:
        return {'error': f'Strategy with ID {strategy_id} not found.'}
    except Exception as e:
        return {'error': f'Error calculating metrics: {str(e)}'}
