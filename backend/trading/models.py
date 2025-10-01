from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import os

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=50)  # ДОБАВЛЕНО: Название биржи (e.g., 'binance')
    api_key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exchange} - {self.user.username}"

    def get_decrypted_api_key(self):
        fernet = Fernet(os.environ.get('FERNET_KEY').encode())
        return fernet.decrypt(self.api_key.encode()).decode()

    def get_decrypted_secret(self):
        fernet = Fernet(os.environ.get('FERNET_KEY').encode())
        return fernet.decrypt(self.secret.encode()).decode()

class Strategy(models.Model):  # ОБНОВЛЕНО: Переименовано из Bot для совместимости; добавлены поля для RL и интеграции
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=20, default='BTC/USDT')
    is_active = models.BooleanField(default=False)  # ДОБАВЛЕНО: Для активации стратегии
    parameters = models.JSONField(default=dict)  # ДОБАВЛЕНО: Параметры для RL (e.g., {'learning_rate': 0.001})
    api_key = models.ForeignKey(ApiKey, on_delete=models.SET_NULL, null=True, blank=True)  # ДОБАВЛЕНО: Связь с ApiKey для биржи
    profit_loss = models.FloatField(default=0.0)  # ДОБАВЛЕНО: Общий P&L для стратегии
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

    # ДОБАВЛЕНО: Метод для получения exchange из связанного ApiKey (интеграция ccxt)
    @property
    def exchange(self):
        if self.api_key:
            import ccxt
            exchange_class = getattr(ccxt, self.api_key.exchange)
            return exchange_class({'apiKey': self.api_key.get_decrypted_api_key(), 'secret': self.api_key.get_decrypted_secret()})
        return None

class Trade(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)  # ОБНОВЛЕНО: Связь с Strategy вместо Bot
    symbol = models.CharField(max_length=20)
    action = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short'), ('hold', 'Hold')])  # ДОБАВЛЕНО: 'hold' для RL
    amount = models.FloatField()
    price = models.FloatField()
    profit_loss = models.FloatField(default=0)  # УЖЕ ЕСТЬ: Обновлено для совместимости
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} {self.action} at {self.price}"

    # ДОБАВЛЕНО: Метод для обновления P&L стратегии после сделки
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.strategy.profit_loss += self.profit_loss
        self.strategy.save()

    # ДОБАВЛЕНО: Метод для триггера обучения RL после сделки (интеграция с tasks.py)
    def trigger_rl_training(self):
        from analytics.tasks import train_model_on_trade
        # Пример: передача данных для обучения
        trade_result = {'profit': self.profit_loss}
        historical_data = [[self.price, self.amount]]  # Упрощённо; используйте реальные данные
        news_data = ["Market news"]  # Интегрируйте новости из news.py
        train_model_on_trade.delay(trade_result, historical_data, news_data)
