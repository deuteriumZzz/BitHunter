from django.test import TestCase
from django.contrib.auth.models import User
from .models import Strategy, Trade, ApiKey

class StrategyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.strategy = Strategy.objects.create(user=self.user, name='Test Strategy', symbol='BTC/USDT', is_active=True)

    def test_strategy_creation(self):
        self.assertEqual(self.strategy.name, 'Test Strategy')

    def test_cached_metrics(self):
        Trade.objects.create(strategy=self.strategy, symbol='BTC/USDT', action='long', amount=0.001, price=50000, profit_loss=100)
        metrics = self.strategy.get_cached_metrics()
        self.assertEqual(metrics['profit'], 100)
