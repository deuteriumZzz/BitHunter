"""
Модуль конфигурации приложения трейдинга.

Определяет настройки для приложения 'trading' в Django-проекте.
"""

from django.apps import AppConfig


class TradingConfig(AppConfig):
    """
    Конфигурация приложения Trading.

    Устанавливает тип авто-поля по умолчанию и имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "trading"
    verbose_name = "трейдинг"
