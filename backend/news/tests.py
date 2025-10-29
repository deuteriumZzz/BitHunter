from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from .models import News
from .tasks import get_news_sentiment


class NewsTestCase(TestCase):
    """
    Набор тестов для модели News и связанных задач.
    """

    def setUp(self):
        """
        Настройка тестового окружения: создание тестового пользователя.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='pass'
        )

    def test_news_creation(self):
        """
        Тест создания объекта News и проверки его полей.
        """
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
        self.assertEqual(news.user, self.user)
        self.assertIsNotNone(news.timestamp)

    def test_task_get_news_sentiment(self):
        """
        Тест задачи get_news_sentiment с mocking для requests, TextBlob, cache и channel_layer.
        """
        mock_articles = [
            {
                'title': 'Test Bitcoin News',
                'description': 'A test description for Bitcoin.',
                'url': 'https://example.com/test-bitcoin-news'
            }
        ]
        
        with patch('news.tasks.requests.get') as mock_get:
            # Mock для requests.get
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {'articles': mock_articles}
            mock_get.return_value = mock_response
            
            with patch('news.tasks.TextBlob') as mock_textblob:
                # Mock для TextBlob.sentiment.polarity
                mock_blob = MagicMock()
                mock_blob.sentiment.polarity = 0.8  # Фиктивный sentiment
                mock_textblob.return_value = mock_blob
                
                with patch('news.tasks.cache.get', return_value=None) as mock_cache_get:
                    # Mock для cache.get (возвращает None, чтобы не использовать кеш)
                    with patch('news.tasks.cache.set') as mock_cache_set:
                        # Mock для cache.set
                        with patch('news.tasks.get_channel_layer') as mock_get_channel:
                            # Mock для get_channel_layer
                            mock_channel = MagicMock()
                            mock_get_channel.return_value = mock_channel
                            
                            # Вызов задачи
                            get_news_sentiment('BTC', self.user.id)
                            
                            # Проверки
                            # Проверить, что requests.get был вызван
                            mock_get.assert_called_once()
                            
                            # Проверить, что TextBlob был создан
                            mock_textblob.assert_called_once_with(
                                'Test Bitcoin News A test description for Bitcoin.'
                            )
                            
                            # Проверить, что cache.set был вызван с avg_sentiment
                            mock_cache_set.assert_called_once_with('news_BTC', 0.8, 3600)
                            
                            # Проверить создание новости в БД
                            news = News.objects.filter(
                                symbol='BTC',
                                url='https://example.com/test-bitcoin-news'
                            ).first()
                            self.assertIsNotNone(news)
                            self.assertEqual(news.sentiment, 0.8)
                            self.assertEqual(news.title, 'Test Bitcoin News')
                            self.assertEqual(news.user_id, self.user.id)
                            
                            # Проверить отправку сообщения через channel_layer
                            mock_channel.group_send.assert_called_once_with(
                                'news_btc',
                                {
                                    'type': 'news_update',
                                    'message': {
                                        'symbol': 'BTC',
                                        'title': 'Test Bitcoin News',
                                        'sentiment': 0.8,
                                        'timestamp': str(news.timestamp),
                                    }
                                }
                            )
