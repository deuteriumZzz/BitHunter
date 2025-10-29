from django.db import models
from django.contrib.auth.models import User
from news.models import News  # Добавлен импорт для связи с News

class AnalyticsData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    symbol = models.CharField(max_length=10, verbose_name="Символ")
    data = models.JSONField(verbose_name="Данные")  # Хранение исторических данных, предсказаний и т.д. (из второй версии)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    # Новые поля для связи с новостями (минимальные изменения, не влияют на существующую логику)
    news_sentiment = models.FloatField(default=0.0, help_text="Средний sentiment новостей за период")
    related_news = models.ManyToManyField(News, blank=True, help_text="Связанные новости")

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'user']),  # Из второй версии
            models.Index(fields=['symbol', 'created_at']),  # Добавлен для оптимизации запросов по новостям
        ]
        verbose_name = "Аналитические данные"
        verbose_name_plural = "Аналитические данные"

    def __str__(self):
        return f"{self.user.username} - {self.symbol} at {self.created_at}"

class Prediction(models.Model):
    # Выборы для action (0=hold, 1=buy, 2=sell)
    ACTION_CHOICES = [
        (0, 'Hold'),
        (1, 'Buy'),
        (2, 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    symbol = models.CharField(max_length=10, blank=True, verbose_name="Символ")  # Добавлено для связи
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время предсказания")
    predicted_price = models.FloatField(verbose_name="Предсказанная цена")
    action = models.IntegerField(choices=ACTION_CHOICES, verbose_name="Рекомендация")  # Из первой версии, с choices
    profit_loss = models.FloatField(default=0.0, verbose_name="Прибыль/убыток")  # Из первой версии

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]
        verbose_name = "Предсказание"
        verbose_name_plural = "Предсказания"

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.predicted_price}"
