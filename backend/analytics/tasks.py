"""
Модуль для выполнения асинхронных задач с использованием Celery.
Включает задачи для получения исторических данных, обучения моделей,
предсказания цен, анализа данных с новостями и обучения на основе сделок.
"""

import logging
import os

import ccxt
import numpy as np
from celery import shared_task
from django.db.models import Avg
from django.utils import timezone
from stable_baselines3 import PPO
from textblob import TextBlob
from datetime import timedelta

from .models import AnalyticsData, Prediction
from analytics.trading_env import TradingEnv
from news.models import News

logger = logging.getLogger(__name__)

_model = None


def get_model():
    """
    Ленивая инициализация RL-модели PPO.
    Загружает модель из файла, если существует, иначе создает новую.
    
    :return: Объект модели PPO.
    """
    global _model
    if _model is None:
        model_path = "ppo_trading_model.zip"
        if os.path.exists(model_path):
            _model = PPO.load(model_path)
        else:
            _model = PPO("MlpPolicy", TradingEnv([], []), verbose=1)
    return _model


@shared_task
def fetch_historical_data():
    """
    Получить исторические данные с использованием активных стратегий.
    
    :return: Сообщение об успехе или ошибке.
    """
    try:
        from trading.models import Strategy
        active_strategies = Strategy.objects.filter(is_active=True)
        for strategy in active_strategies:
            if strategy.exchange:
                data = strategy.exchange.fetch_ohlcv(
                    strategy.symbol,
                    timeframe='1h',
                    limit=100
                )
                for candle in data:
                    AnalyticsData.objects.create(
                        symbol=strategy.symbol,
                        timestamp=candle[0] / 1000,
                        price=candle[4],
                        volume=candle[5],
                        user=strategy.user
                    )
        logger.info("Historical data fetched successfully")
        return "Historical data fetched"
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return f"Error: {e}"


@shared_task
def train_ml_model():
    """
    Обучить ML-модель с использованием RL и данных новостей.
    
    :return: Сообщение об успехе или ошибке.
    """
    try:
        try:
            from news.tasks import get_news_sentiment
            news_features = np.array(get_news_sentiment()).reshape(-1, 1)
        except ImportError:
            news_features = np.zeros((len(data), 1))

        data = list(
            AnalyticsData.objects.values_list('price', 'volume')
        )
        if not data:
            return "No historical data available"

        if len(news_features) != len(data):
            news_features = np.zeros((len(data), 1))

        env = TradingEnv(data, news_features)
        model = get_model()
        model.set_env(env)
        model.learn(total_timesteps=10000)
        model.save("ppo_trading_model.zip")
        logger.info("Model trained with RL and news")
        return "Model trained with RL and news"
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return f"Error: {e}"


@shared_task
def predict_price():
    """
    Предсказать цену с использованием RL-модели.
    
    :return: Действие предсказания или сообщение об ошибке.
    """
    try:
        last_hist = AnalyticsData.objects.last()
        if not last_hist:
            return "No historical data"

        try:
            from news.tasks import get_news_sentiment
            news_sentiment = (
                get_news_sentiment()[0] if get_news_sentiment() else 0
            )
        except ImportError:
            news_sentiment = 0

        obs = np.array([last_hist.price, last_hist.volume, news_sentiment])

        model = get_model()
        action, _ = model.predict(obs)
        prediction = Prediction(
            action=action,
            predicted_price=last_hist.price,
            user=last_hist.user
        )
        prediction.save()
        logger.info(f"Prediction made: action {action}")
        return action
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        return f"Error: {e}"


@shared_task
def train_model_on_trade(trade_result, historical_data, news_data):
    """
    Обучить модель после сделки (онлайн-обучение).
    
    :param trade_result: Результат сделки.
    :param historical_data: Исторические данные.
    :param news_data: Данные новостей.
    :return: Сообщение об успехе или ошибке.
    """
    try:
        reward = (
            trade_result.get('profit', 0)
            if trade_result.get('profit', 0) > 0 else -1
        )
        news_features = (
            np.array([
                TextBlob(text).sentiment.polarity for text in news_data
            ]).reshape(-1, 1)
            if news_data else np.zeros((len(historical_data), 1))
        )

        env = TradingEnv(historical_data, news_features)
        model = get_model()
        model.set_env(env)
        model.learn(total_timesteps=100, reset_num_timesteps=False)
        model.save("ppo_trading_model.zip")
        logger.info("Model updated after trade")
        return "Model updated after trade"
    except Exception as e:
        logger.error(f"Error training on trade: {e}")
        return f"Error: {e}"


@shared_task
def analyze_data_with_news(symbol, user_id=None):
    """
    Анализ данных с использованием sentiment из новостей для RL-предсказаний.
    Обновляет AnalyticsData и связывает с News.
    
    :param symbol: Символ актива.
    :param user_id: ID пользователя (опционально).
    :return: Сообщение об успехе или ошибке.
    """
    try:
        past_24h = timezone.now() - timedelta(hours=24)
        news_qs = News.objects.filter(
            symbol=symbol,
            timestamp__gte=past_24h
        )
        if user_id:
            news_qs = news_qs.filter(user_id=user_id)

        avg_sentiment = (
            news_qs.aggregate(Avg('sentiment'))['sentiment__avg'] or 0.0
        )

        analytics, created = AnalyticsData.objects.get_or_create(
            symbol=symbol,
            user_id=user_id,
            defaults={
                'data': {},
                'news_sentiment': avg_sentiment,
            }
        )
        if not created:
            analytics.news_sentiment = avg_sentiment
            analytics.save()

        analytics.related_news.set(news_qs)

        logger.info(
            f"Анализ для {symbol}: средний sentiment {avg_sentiment}, "
            f"связанных новостей: {news_qs.count()}"
        )
        return f"Analyzed {symbol} with news sentiment: {avg_sentiment}"
    except Exception as e:
        logger.error(f"Error in analyze_data_with_news: {e}")
        return f"Error: {e}"


@shared_task
def bulk_load_historical_data(symbol, timeframe='1h', limit=1000):
    """
    Массово загрузить исторические данные для символа.
    
    :param symbol: Символ актива.
    :param timeframe: Временной интервал.
    :param limit: Количество записей.
    """
    exchange = ccxt.binance()
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    objects = [
        AnalyticsData(
            symbol=symbol,
            timestamp=d[0],
            open=d[1],
            high=d[2],
            low=d[3],
            close=d[4],
            volume=d[5]
        ) for d in data
    ]
    AnalyticsData.objects.bulk_create(objects, ignore_conflicts=True)
