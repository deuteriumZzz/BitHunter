"""
Модуль тестов для моделей приложения трейдинга.

Содержит тест-кейсы для проверки создания стратегий, кэшированных метрик и других аспектов.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from .models import ApiKey, Strategy, Trade


class StrategyTestCase(TestCase):
    """
    Тест-кейсы для модели Strategy.

    Проверяет создание стратегии, кэшированные метрики и другие связанные функции.
    """

    def setUp(self):
        """
        Настройка тестового окружения.

        Создаёт тестового пользователя и стратегию для использования в тестах.
        """
        self.user = User.objects.create_user(username='test', password='test')
        self.strategy = Strategy.objects.create(
            user=self.user,
            name='Test Strategy',
            symbol='BTC/USDT',
            is_active=True
        )

    def test_strategy_creation(self):
        """
        Тестирует создание стратегии.

        Проверяет, что стратегия создана с правильным именем.
        """
        self.assertEqual(self.strategy.name, 'Test Strategy')

    def test_cached_metrics(self):
        """
        Тестирует кэшированные метрики стратегии.

        Создаёт трейд и проверяет, что метрики корректно рассчитаны и кэшированы.
        """
        Trade.objects.create(
            strategy=self.strategy,
            symbol='BTC/USDT',
            action='long',
            amount=0.001,
            price=50000,
            profit_loss=100
        )
        metrics = self.strategy.get_cached_metrics()
        self.assertEqual(metrics['profit'], 100)
