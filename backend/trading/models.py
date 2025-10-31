"""
Модуль моделей для приложения трейдинга.

Определяет модели ApiKey, Strategy, Trade и TradeAudit для хранения данных о ключах API, стратегиях,
трейдах и аудите. Включает шифрование ключей, валидацию JSON, кэширование метрик, интеграцию с новостями
и триггеры для обучения RL-моделей.
"""

import os

from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from django.core.validators import JSONSchemaValidator
from django.db import models, transaction
from django.utils import timezone

# Схема для валидации parameters (пример: ограничение типов)
PARAMETERS_SCHEMA = {
    "type": "object",
    "properties": {
        "learning_rate": {"type": "number", "minimum": 0},
        "gamma": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "additionalProperties": False,
}


class ApiKey(models.Model):
    """
    Модель для хранения API-ключей бирж.

    Ассоциируется с пользователем. Ключи хранятся в зашифрованном виде.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    exchange = models.CharField(max_length=50)
    api_key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "exchange",
        )  # Запрет дублирования ключей для одной биржи

    def __str__(self):
        return f"{self.exchange} - {self.user.username}"

    def get_decrypted_api_key(self):
        """
        Возвращает расшифрованный API-ключ.

        Использует Fernet с ключом из окружения.
        """
        fernet = Fernet(os.environ.get("FERNET_KEY").encode())
        return fernet.decrypt(self.api_key.encode()).decode()

    def get_decrypted_secret(self):
        """
        Возвращает расшифрованный секрет.

        Использует Fernet с ключом из окружения.
        """
        fernet = Fernet(os.environ.get("FERNET_KEY").encode())
        return fernet.decrypt(self.secret.encode()).decode()


class Strategy(models.Model):
    """
    Модель для стратегий трейдинга.

    Ассоциируется с пользователем и API-ключом. Параметры валидируются по JSON-схеме.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=10, db_index=True)
    is_active = models.BooleanField(default=False)
    parameters = models.JSONField(
        default=dict,
        validators=[JSONSchemaValidator(PARAMETERS_SCHEMA)],  # Валидация JSON
    )
    api_key = models.ForeignKey(
        ApiKey, on_delete=models.SET_NULL, null=True, blank=True
    )
    profit_loss = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_cached_metrics(self):
        """
        Возвращает кэшированные метрики стратегии (прибыль и win_rate).

        Вычисляет на основе связанных трейдов, если кэш отсутствует.
        """
        from django.core.cache import cache

        cache_key = f"strategy_metrics_{self.id}"
        data = cache.get(cache_key)
        if not data:
            total_profit = sum(trade.profit_loss for trade in self.trade_set.all())
            win_rate = (
                (
                    self.trade_set.filter(profit_loss__gt=0).count()
                    / self.trade_set.count()
                )
                * 100
                if self.trade_set.exists()
                else 0
            )
            data = {"profit": total_profit, "win_rate": win_rate}
            cache.set(cache_key, data, 300)
        return data

    @property
    def exchange(self):
        """
        Возвращает экземпляр биржи (ccxt) с расшифрованными ключами.

        Если API-ключ не задан, возвращает None.
        """
        if self.api_key:
            import ccxt

            exchange_class = getattr(ccxt, self.api_key.exchange)
            return exchange_class(
                {
                    "apiKey": self.api_key.get_decrypted_api_key(),
                    "secret": self.api_key.get_decrypted_secret(),
                }
            )
        return None

    # Метод для получения новостей (интеграция с news.py или API)
    def get_news(self, limit=5):
        """
        Возвращает последние новости по символу стратегии.

        Пытается загрузить из локальной модели News; если нет данных, запускает асинхронную задачу
        для загрузки и возвращает пустой список (чтобы не блокировать).
        """
        try:
            from news.models import News  # Импорт из вашего news.py

            news = News.objects.filter(symbol=self.symbol).order_by("-timestamp")[
                :limit
            ]
            if news.exists():
                return news
            else:
                # Если новостей нет, запускаем асинхронную задачу для загрузки
                from news.tasks import (
                    get_news_sentiment,  # Используем вашу реальную задачу
                )

                get_news_sentiment.delay(
                    self.symbol, user_id=self.user.id
                )  # Передаём user_id
                return []  # Возвращаем пустой список, пока задача не выполнится
        except ImportError:
            # Если модель News недоступна, запускаем задачу и возвращаем []
            from news.tasks import get_news_sentiment

            get_news_sentiment.delay(self.symbol, user_id=self.user.id)
            return []


class Trade(models.Model):
    """
    Модель для трейдов.

    Ассоциируется со стратегией. Автоматически обновляет P&L стратегии при сохранении.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    action = models.CharField(
        max_length=10, choices=[("long", "Long"), ("short", "Short"), ("hold", "Hold")]
    )  # Исправлено: Добавлены корректные choices
    amount = models.FloatField()
    price = models.FloatField()
    profit_loss = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return f"{self.symbol} {self.action} at {self.price}"

    def save(self, *args, **kwargs):
        """
        Сохраняет трейд и атомарно обновляет profit_loss стратегии.
        """
        with transaction.atomic():  # Атомарность для обновления P&L
            super().save(*args, **kwargs)
            self.strategy.profit_loss += self.profit_loss
            self.strategy.save()

    def trigger_rl_training(self):
        """
        Триггерит асинхронное обучение RL-модели на основе этого трейда.

        Передаёт результат трейда, исторические данные и новости.
        """
        from analytics.tasks import train_model_on_trade

        trade_result = {"profit": self.profit_loss}
        historical_data = [
            [self.price, self.amount]
        ]  # Упрощённо; расширьте для реальных данных
        news_data = self.strategy.get_news()  # Интеграция новостей
        train_model_on_trade.delay(trade_result, historical_data, news_data)


class TradeAudit(models.Model):
    """
    Модель для аудита трейдов.

    Логирует действия (create, update, delete) над трейдами с деталями.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade = models.ForeignKey("Trade", on_delete=models.CASCADE)
    action = models.CharField(
        max_length=50,
        choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete")],
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(
        default=dict
    )  # Дополнительные детали, например, изменения

    class Meta:
        ordering = ["-timestamp"]
