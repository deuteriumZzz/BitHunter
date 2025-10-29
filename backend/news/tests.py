from django.test import TestCase
from django.contrib.auth.models import User
from .models import News
from .tasks import get_news_sentiment

class NewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_news_creation(self):
        news = News.objects.create(
            user=self.user,
            symbol='BTC',
            title='Test News',
            description='Description',
            url='https://example.com',
            sentiment=0.5
        )
        self.assertEqual(news.symbol, 'BTC')
        self.assertEqual(news.sentiment, 0.5)

    def test_task_get_news_sentiment(self):
        # Тест задачи (требует mock для requests, но для примера)
        # get_news_sentiment.delay('BTC', self.user.id)  # В реальности добавьте mock
        pass
