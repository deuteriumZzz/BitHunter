from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import os

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=50)
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

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=20, default='BTC/USDT')
    is_active = models.BooleanField(default=False)
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_cached_metrics(self):
        from django.core.cache import cache
        cache_key = f"strategy_metrics_{self.id}"
        data = cache.get(cache_key)
        if not data:
            total_profit = sum(trade.profit for trade in self.trade_set.all())
            win_rate = (self.trade_set.filter(profit__gt=0).count() / self.trade_set.count()) * 100 if self.trade_set.exists() else 0
            data = {'profit': total_profit, 'win_rate': win_rate}
            cache.set(cache_key, data, 300)
        return data

class Trade(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    action = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])
    amount = models.FloatField()
    price = models.FloatField()
    profit_loss = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} {self.action} at {self.price}"
