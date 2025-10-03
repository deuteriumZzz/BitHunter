from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class AlertRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, help_text="Криптовалютная пара, например, BTC/USDT")
    condition = models.CharField(max_length=20, choices=[
        ('above', 'Цена выше'),
        ('below', 'Цена ниже'),
        ('change_percent', 'Изменение в %'),
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.condition == 'change_percent' and (self.value < -100 or self.value > 100):
            raise ValidationError("Процент изменения должен быть между -100 и 100.")

    def __str__(self):
        return f"{self.user.username}: {self.symbol} {self.condition} {self.value}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."
