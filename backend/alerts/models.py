from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class AlertRule(models.Model):
    """
    Модель правила оповещения.
    
    Определяет условия для отправки оповещений пользователю на основе цены криптовалюты.
    """
    
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
        """
        Валидирует модель перед сохранением.
        
        Проверяет, что для условия 'change_percent' значение находится в диапазоне от -100 до 100.
        """
        if self.condition == 'change_percent' and (self.value < -100 or self.value > 100):
            raise ValidationError("Процент изменения должен быть между -100 и 100.")
    
    def __str__(self):
        """
        Возвращает строковое представление правила оповещения.
        """
        return f"{self.user.username}: {self.symbol} {self.condition} {self.value}"
    
    class Meta:
        verbose_name = 'Правило оповещения'
        verbose_name_plural = 'Правила оповещений'


class Notification(models.Model):
    """
    Модель уведомления.
    
    Хранит информацию об отправленных оповещениях пользователям на основе правил.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """
        Возвращает строковое представление уведомления.
        """
        return f"Notification for {self.user.username}: {self.message[:50]}..."
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
