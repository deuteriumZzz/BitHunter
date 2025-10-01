from celery import shared_task
from .model_trainer import ModelTrainer
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

@shared_task
def predict_price(exchange, symbol, look_back=60):
    trainer = ModelTrainer(settings.BASE_DIR)
    input_data, scaler = trainer.prepare_prediction_data(exchange, symbol, look_back)
    if input_data is None:
        return None
    model = load_model(trainer.model_path)
    prediction = trainer.predict_price(input_data, scaler, model)
    return prediction

@shared_task
def analyze_news(symbol):
    api_key = settings.NEWS_API_KEY
    if not api_key:
        return 0.0
    response = requests.get(f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}&pageSize=10')
    data = response.json()
    if not data.get('articles'):
        return 0.0
    positive_words = ['rise', 'bull', 'growth', 'profit', 'up']
    negative_words = ['fall', 'bear', 'decline', 'down', 'loss']
    sentiment = 0.0
    for article in data['articles']:
        text = article['title'].lower() + ' ' + article.get('description', '').lower()
        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        sentiment += (pos - neg)
    return max(-1.0, min(1.0, sentiment / len(data['articles'])))

@shared_task
def train_model_task():
    trainer = ModelTrainer(settings.BASE_DIR)
    data = trainer.load_data_from_csv()
    if data is not None:
        trainer.train_model(data)
        logger.info("Модель обучена")
