import requests
import os
from textblob import TextBlob
from django.core.cache import cache

def get_news_sentiment(symbol='BTC', limit=10):
    """Получить sentiment-анализ новостей для символа."""
    cache_key = f"news_sentiment_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_key = os.environ.get('NEWS_API_KEY')  # Установите в .env
    if not api_key:
        return [0] * limit  # Fallback если нет ключа
    
    try:
        response = requests.get(f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}&pageSize={limit}')
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            sentiments = [TextBlob(article['title'] + ' ' + (article.get('description') or '')).sentiment.polarity for article in articles]
            cache.set(cache_key, sentiments, 3600)  # Кэш на 1 час
            return sentiments
        else:
            return [0] * limit
    except Exception as e:
        print(f"Error fetching news: {e}")
        return [0] * limit
