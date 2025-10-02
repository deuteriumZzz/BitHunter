from django.db import models
from django.contrib.auth.models import User

class AlertRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    symbol = models.CharField(max_length=10, verbose_name="Символ")
    threshold = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Порог")

    class Meta:
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['user']),
        ]
        verbose_name = "Правило алерта"
        verbose_name_plural = "Правила алертов"

    def __str__(self):
        return f"{self.user.username} - {self.symbol} >= {self.threshold}"

class Notification(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name="Правило")
    message = models.TextField(verbose_name="Сообщение")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")

    class Meta:
        indexes = [
            models.Index(fields=['rule']),
        ]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"Notification for {self.rule.symbol}: {self.message[:50]}..."
