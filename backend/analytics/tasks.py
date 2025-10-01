from celery import shared_task
from .models import HistoricalData, Prediction
from .trading_env import TradingEnv  # ДОБАВЛЕНО: Импорт новой среды
from stable_baselines3 import PPO  # ДОБАВЛЕНО: RL-модель
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # ДОБАВЛЕНО: Для новостей
from textblob import TextBlob  # ДОБАВЛЕНО: Для sentiment-анализа новостей
import os

# ДОБАВЛЕНО: Глобальная RL-модель (инициализируйте при старте)
model_path = "ppo_trading_model.zip"
if os.path.exists(model_path):
    model = PPO.load(model_path)
else:
    model = PPO("MlpPolicy", TradingEnv([], []), verbose=1)  # Пустая среда для инициализации

@shared_task
def fetch_historical_data():
    """Получить исторические данные."""
    # Интеграция старого кода: используйте ccxt или API
    from trading.models import Bot
    bot = Bot.objects.first()
    if bot:
        data = bot.exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
        for candle in data:
            HistoricalData.objects.create(
                symbol='BTC/USDT',
                timestamp=candle[0],
                price=candle[4],  # Close price
                volume=candle[5],
                user=bot.user
            )
    return "Historical data fetched"

@shared_task
def train_ml_model():
    """Обучить ML-модель с RL и новостями."""
    data = HistoricalData.objects.all()
    # ДОБАВЛЕНО: Интеграция новостей
    from ..news import get_news_sentiment  # Импорт из news.py
    news_features = np.array(get_news_sentiment()).reshape(-1, 1)

    # Создайте среду и обучите RL
    hist_data = list(data.values_list('price', 'volume'))
    env = TradingEnv(hist_data, news_features)
    model.set_env(env)
    model.learn(total_timesteps=10000)  # RL-обучение
    model.save(model_path)
    return "Model trained with RL and news"

@shared_task
def predict_price():
    """Предсказать цену с RL."""
    # Пример состояния: последние данные + новости
    last_hist = HistoricalData.objects.last()
    news_sentiment = get_news_sentiment()[0] if get_news_sentiment() else 0
    obs = np.array([last_hist.price, last_hist.volume, news_sentiment])
    action, _ = model.predict(obs)
    prediction = Prediction(action=action, predicted_price=last_hist.price, user=last_hist.user)
    prediction.save()
    return action

# ДОБАВЛЕНО: Функция для онлайн-обучения после сделки
@shared_task
def train_model_on_trade(trade_result, historical_data, news_data):
    """Обучить модель после сделки."""
    reward = trade_result['profit'] if trade_result['profit'] > 0 else -1
    news_features = np.array([TextBlob(text).sentiment.polarity for text in news_data]).reshape(-1, 1)
    
    env = TradingEnv(historical_data, news_features)
    model.set_env(env)
    model.learn(total_timesteps=100, reset_num_timesteps=False)  # Короткое обучение
    model.save(model_path)
    return "Model updated after trade"
