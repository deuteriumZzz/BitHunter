from django.db import models
from django.contrib.auth.models import User

from news.models import News


class AnalyticsData(models.Model):
    """
    Модель для хранения аналитических данных пользователя, включая исторические данные,
    предсказания и связанные новости с анализом sentiment.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    symbol = models.CharField(max_length=10, verbose_name="Символ")
    data = models.JSONField(verbose_name="Данные")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    news_sentiment = models.FloatField(
        default=0.0,
        help_text="Средний sentiment новостей за период"
    )
    related_news = models.ManyToManyField(
        News,
        blank=True,
        help_text="Связанные новости"
    )

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'user']),
            models.Index(fields=['symbol', 'created_at']),
        ]
        verbose_name = "Аналитические данные"
        verbose_name_plural = "Аналитические данные"

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        
        :return: Строка с именем пользователя, символом и датой создания.
        """
        return f"{self.user.username} - {self.symbol} at {self.created_at}"


class Prediction(models.Model):
    """
    Модель для хранения предсказаний цен и рекомендаций действий по активам.
    """

    ACTION_CHOICES = [
        (0, 'Hold'),
        (1, 'Buy'),
        (2, 'Sell'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    symbol = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Символ"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время предсказания"
    )
    predicted_price = models.FloatField(verbose_name="Предсказанная цена")
    action = models.IntegerField(
        choices=ACTION_CHOICES,
        verbose_name="Рекомендация"
    )
    profit_loss = models.FloatField(
        default=0.0,
        verbose_name="Прибыль/убыток"
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]
        verbose_name = "Предсказание"
        verbose_name_plural = "Предсказания"

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        
        :return: Строка с именем пользователя, действием и предсказанной ценой.
        """
        return f"{self.user.username} - {self.get_action_display()} at {self.predicted_price}"


class Trade(models.Model):
    """
    Модель для хранения сделок пользователя по активам, включая цены покупки/продажи и расчет прибыли.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    symbol = models.CharField(max_length=10, verbose_name="Символ актива")
    buy_price = models.FloatField(verbose_name="Цена покупки")
    sell_price = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Цена продажи"
    )
    amount = models.FloatField(verbose_name="Количество актива")
    buy_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата покупки"
    )
    sell_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата продажи"
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'symbol']),
            models.Index(fields=['buy_date']),
        ]
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        
        :return: Строка с именем пользователя, символом, статусом и деталями сделки.
        """
        status = "Открыта" if not self.sell_price else "Закрыта"
        return f"{self.user.username} - {self.symbol}: {status} ({self.amount} @ {self.buy_price})"

    def calculate_trade_profit(self):
        """
        Рассчитывает прибыль или убыток по сделке.
        
        :return: Прибыль (положительная) или убыток (отрицательный), или 0.0 если сделка не закрыта.
        """
        if self.sell_price:
            return (self.sell_price - self.buy_price) * self.amount
        return 0.0
