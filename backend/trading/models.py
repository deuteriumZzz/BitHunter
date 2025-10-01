from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone  # ДОБАВЛЕНО: Для timestamp
from cryptography.fernet import Fernet
import os
from django.core.validators import JSONSchemaValidator  # ДОБАВЛЕНО: Для валидации JSON

# Схема для валидации parameters (пример: ограничение типов)
PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "learning_rate": {"type": "number", "minimum": 0},
        "gamma": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "additionalProperties": False,
}

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    exchange = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'exchange')  # ДОБАВЛЕНО: Запрет дублирования ключей для одной биржи

    def __str__(self):
        return f"{self.exchange} - {self.user.username}"

    def get_decrypted_api_key(self):
        fernet = Fernet(os.environ.get('FERNET_KEY').encode())
        return fernet.decrypt(self.api_key.encode()).decode()

    def get_decrypted_secret(self):
        fernet = Fernet(os.environ.get('FERNET_KEY').encode())
        return fernet.decrypt(self.secret.encode()).decode()

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=10, db_index=True)
    is_active = models.BooleanField(default=False)
    parameters = models.JSONField(default=dict, validators=[JSONSchemaValidator(PARAMETERS_SCHEMA)])  # ДОБАВЛЕНО: Валидация JSON
    api_key = models.ForeignKey(ApiKey, on_delete=models.SET_NULL, null=True, blank=True)
    profit_loss = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_cached_metrics(self):
        from django.core.cache import cache
        cache_key = f"strategy_metrics_{self.id}"
        data = cache.get(cache_key)
        if not data:
            total_profit = sum(trade.profit_loss for trade in self.trade_set.all())
            win_rate = (self.trade_set.filter(profit_loss__gt=0).count() / self.trade_set.count()) * 100 if self.trade_set.exists() else 0
            data = {'profit': total_profit, 'win_rate': win_rate}
            cache.set(cache_key, data, 300)
        return data

    @property
    def exchange(self):
        if self.api_key:
            import ccxt
            exchange_class = getattr(ccxt, self.api_key.exchange)
            return exchange_class({'apiKey': self.api_key.get_decrypted_api_key(), 'secret': self.api_key.get_decrypted_secret()})
        return None

    # ДОБАВЛЕНО: Метод для получения новостей (интеграция с news.py или API)
    def get_news(self, limit=5):
        # Предполагаем модель News из news.py (если нет, замените на API-вызов, e.g., requests.get)
        try:
            from news.models import News  # Импорт из вашего news.py
            return News.objects.filter(symbol=self.symbol).order_by('-timestamp')[:limit]
        except ImportError:
            # Fallback: вызов внешнего API (e.g., NewsAPI)
            import requests
            api_key = os.environ.get('NEWS_API_KEY')
            response = requests.get(f'https://newsapi.org/v2/everything?q={self.symbol}&apiKey={api_key}')
            return response.json().get('articles', [])[:limit] if response.status_code == 200 else []

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    action = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short'), ('hold', 'Hold')])
    amount = models.FloatField()
    price = models.FloatField()
    profit_loss = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f"{self.symbol} {self.action} at {self.price}"

    def save(self, *args, **kwargs):
        with transaction.atomic():  # ДОБАВЛЕНО: Атомарность для обновления P&L
            super().save(*args, **kwargs)
            self.strategy.profit_loss += self.profit_loss
            self.strategy.save()

    def trigger_rl_training(self):
        from analytics.tasks import train_model_on_trade
        trade_result = {'profit': self.profit_loss}
        historical_data = [[self.price, self.amount]]  # Упрощённо; расширьте для реальных данных
        news_data = self.strategy.get_news()  # ДОБАВЛЕНО: Интеграция новостей
        train_model_on_trade.delay(trade_result, historical_data, news_data)
