from django.db import models
from django.contrib.auth.models import User

class HistoricalData(models.Model):
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    price = models.FloatField()
    volume = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Prediction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    predicted_price = models.FloatField()
    action = models.IntegerField()  # 0=hold, 1=buy, 2=sell (ДОБАВЛЕНО: Для RL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # ДОБАВЛЕНО: Поле для profit/loss
    profit_loss = models.FloatField(default=0.0)
