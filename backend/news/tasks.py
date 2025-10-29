import requests
from textblob import TextBlob
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from .models import News
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task(bind=True, max_retries=3)
def get_news_sentiment(self, symbol, user_id=None):
    """
    Задача с кешированием и rate-limiting.
    """
    api_key = getattr(settings, 'NEWS_API_KEY', None)
    if not api_key:
        raise ValueError("NEWS_API_KEY не установлен")

    cache_key = f'news_{symbol}'
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"Используем кеш для {symbol}")
        return cached_data

    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}&language=en&sortBy=publishedAt&pageSize=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Ошибка: {e}")
        self.retry(countdown=60)  # Повтор через 1 минуту
        return

    articles = data.get('articles', [])
    if not articles:
        print(f"Нет новостей для {symbol}")
        return

    channel_layer = get_channel_layer()
    group_name = f'news_{symbol.lower()}'

    sentiment_list = []
    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        if not title or not url:
            continue

        text = f"{title} {description}".strip()
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        sentiment_list.append(sentiment)

        news, created = News.objects.get_or_create(
            symbol=symbol.upper(),
            url=url,
            defaults={
                'user_id': user_id,
                'title': title,
                'description': description,
                'sentiment': sentiment,
                'timestamp': timezone.now(),
            }
        )
        if created:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'news_update',
                    'message': {
                        'symbol': news.symbol,
                        'title': news.title,
                        'sentiment': news.sentiment,
                        'timestamp': str(news.timestamp),
                    }
                }
            )
            print(f"Сохранена новость: {news}")

    # Кешировать средний sentiment на 1 час
    avg_sentiment = sum(sentiment_list) / len(sentiment_list) if sentiment_list else 0.0
    cache.set(cache_key, avg_sentiment, 3600)
    print(f"Обработано {len(articles)} новостей для {symbol}, средний sentiment: {avg_sentiment}")
