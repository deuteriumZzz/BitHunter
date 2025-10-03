from celery import shared_task
from .models import AnalyticsData, Prediction
from analytics.trading_env import TradingEnv  # Импорт среды
from stable_baselines3 import PPO
import numpy as np
from textblob import TextBlob  # Для sentiment-анализа новостей
import os
import logging

logger = logging.getLogger(__name__)

# Ленивая инициализация RL-модели
_model = None
def get_model():
    global _model
    if _model is None:
        model_path = "ppo_trading_model.zip"
        if os.path.exists(model_path):
            _model = PPO.load(model_path)
        else:
            # Инициализация с пустой средой (замените на вашу логику)
            _model = PPO("MlpPolicy", TradingEnv([], []), verbose=1)
    return _model

@shared_task
def fetch_historical_data():
    """Получить исторические данные с ccxt через Strategy."""
    try:
        from trading.models import Strategy
        active_strategies = Strategy.objects.filter(is_active=True)
        for strategy in active_strategies:
            if strategy.exchange:  # Используем property exchange из models.py
                data = strategy.exchange.fetch_ohlcv(strategy.symbol, timeframe='1h', limit=100)
                for candle in data:
                    AnalyticsData.objects.create(
                        symbol=strategy.symbol,
                        timestamp=candle[0] / 1000,  # Преобразование из ms в s
                        price=candle[4],  # Close price
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
    """Обучить ML-модель с RL и новостями."""
    try:
        from ..news import get_news_sentiment  # Импорт из news.py
        data = list(HistoricalData.objects.values_list('price', 'volume'))
        if not data:
            return "No historical data available"
        
        # Интеграция новостей
        news_features = np.array(get_news_sentiment()).reshape(-1, 1)
        if len(news_features) != len(data):
            news_features = np.zeros((len(data), 1))  # Fallback если новости не совпадают
        
        # RL-обучение
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
    """Предсказать цену с RL."""
    try:
        last_hist = AnalyticsData.objects.last()
        if not last_hist:
            return "No historical data"
        
        from ..news import get_news_sentiment
        news_sentiment = get_news_sentiment()[0] if get_news_sentiment() else 0
        obs = np.array([last_hist.price, last_hist.volume, news_sentiment])
        
        model = get_model()
        action, _ = model.predict(obs)
        prediction = Prediction(action=action, predicted_price=last_hist.price, user=last_hist.user)
        prediction.save()
        logger.info(f"Prediction made: action {action}")
        return action
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        return f"Error: {e}"

@shared_task
def train_model_on_trade(trade_result, historical_data, news_data):
    """Обучить модель после сделки (онлайн-обучение)."""
    try:
        reward = trade_result.get('profit', 0) if trade_result.get('profit', 0) > 0 else -1
        news_features = np.array([TextBlob(text).sentiment.polarity for text in news_data]).reshape(-1, 1) if news_data else np.zeros((len(historical_data), 1))
        
        env = TradingEnv(historical_data, news_features)
        model = get_model()
        model.set_env(env)
        model.learn(total_timesteps=100, reset_num_timesteps=False)  # Короткое обучение
        model.save("ppo_trading_model.zip")
        logger.info("Model updated after trade")
        return "Model updated after trade"
    except Exception as e:
        logger.error(f"Error training on trade: {e}")
        return f"Error: {e}"
