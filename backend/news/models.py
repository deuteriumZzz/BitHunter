from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class News(models.Model):
    """
    Модель для хранения новостей о криптовалюте.

    Содержит информацию о новости, включая символ, заголовок,
    описание, ссылку, sentiment и временную метку.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Опционально, для персонализации новостей",
    )
    symbol = models.CharField(
        max_length=10, help_text="Символ криптовалюты, например BTC"
    )
    title = models.TextField(help_text="Заголовок новости")
    description = models.TextField(blank=True, help_text="Описание новости")
    url = models.URLField(help_text="Ссылка на новость")
    sentiment = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Polarity sentiment от TextBlob",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="Время получения новости"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["symbol", "timestamp"]),
            models.Index(fields=["sentiment"]),
        ]
        unique_together = ("symbol", "url")

    def __str__(self):
        """
        Возвращает строковое представление новости.

        Включает символ, начало заголовка и значение sentiment.
        """
        return f"{self.symbol}: {self.title[:50]}... (Sentiment: {self.sentiment:.2f})"
