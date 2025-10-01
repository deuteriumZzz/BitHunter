import logging
from django.core.cache import cache
import requests
import os
from textblob import TextBlob
import time  # Для задержки
from trading.models import News

logger = logging.getLogger(__name__)

def get_news_sentiment(symbol='BTC', limit=10):
    cache_key = f"news_sentiment_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_key = os.environ.get('NEWS_API_KEY')
    if not api_key:
        logger.warning("NEWS_API_KEY not set, returning neutral sentiments")
        return [0.0] * limit
    
    try:
        time.sleep(1)  # Задержка для rate limiting
        response = requests.get(
            f'https://newsapi.org/v2/everything?q={symbol} cryptocurrency&apiKey={api_key}&pageSize={limit}&sortBy=publishedAt'
        )
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if not articles:
                logger.info(f"No articles found for {symbol}")
                return [0.0] * limit
            sentiments = []
            for article in articles:
                text = article.get('title', '') + ' ' + (article.get('description') or '')
                if text.strip():
                    sentiment = TextBlob(text).sentiment.polarity
                    sentiments.append(sentiment)
                else:
                    sentiments.append(0.0)
            cache.set(cache_key, sentiments, 1800)  # Кэш на 30 мин
            return sentiments
        elif response.status_code == 429:
            logger.error("NewsAPI rate limit exceeded")
            return [0.0] * limit
        else:
            logger.error(f"NewsAPI error: {response.status_code}")
            return [0.0] * limit
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return [0.0] * limit
