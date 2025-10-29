import requests
from textblob import TextBlob
from celery import shared_task
from django.conf import settings
from .models import News
from django.utils import timezone

@shared_task
def get_news_sentiment(symbol, user_id=None):
    """
    Асинхронная задача для получения новостей по символу из NewsAPI,
    анализа sentiment с помощью TextBlob и сохранения в БД.
    Вызывается периодически или вручную (например, из analytics/tasks.py).
    """
    api_key = getattr(settings, 'NEWS_API_KEY', None)
    if not api_key:
        raise ValueError("NEWS_API_KEY не установлен в settings.py")

    # Запрос к NewsAPI (бесплатный план: 100 запросов/день)
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}&language=en&sortBy=publishedAt&pageSize=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        # Логирование ошибки (добавьте logging в production)
        print(f"Ошибка при запросе к NewsAPI для {symbol}: {e}")
        return

    articles = data.get('articles', [])
    if not articles:
        print(f"Нет новостей для {symbol}")
        return

    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        if not title or not url:
            continue  # Пропустить неполные новости

        # Анализ sentiment (на основе title + description)
        text = f"{title} {description}".strip()
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity  # От -1 до 1

        # Сохранение в БД (если не существует)
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
            print(f"Сохранена новость: {news}")
        else:
            print(f"Новость уже существует: {news}")

    print(f"Обработано {len(articles)} новостей для {symbol}")
