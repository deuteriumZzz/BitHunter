from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class News(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, help_text="Опционально, для персонализации новостей")
    symbol = models.CharField(max_length=10, help_text="Символ криптовалюты, например BTC")  # Уникальность по символу и таймстампу
    title = models.TextField(help_text="Заголовок новости")
    description = models.TextField(blank=True, help_text="Описание новости")
    url = models.URLField(help_text="Ссылка на новость")
    sentiment = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],  # Sentiment от -1 (негатив) до 1 (позитив)
        help_text="Polarity sentiment от TextBlob"
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Время получения новости")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),  # Для быстрого поиска по символу и времени
            models.Index(fields=['sentiment']),  # Для фильтрации по sentiment
        ]
        unique_together = ('symbol', 'url')  # Избегать дубликатов новостей по URL для символа

    def __str__(self):
        return f"{self.symbol}: {self.title[:50]}... (Sentiment: {self.sentiment:.2f})"
