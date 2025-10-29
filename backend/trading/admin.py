"""
Модуль админ-панели для приложения трейдинга.

Регистрирует модели Strategy, Trade и ApiKey в Django Admin с настройкой отображения полей.
"""

from django.contrib import admin

from .models import Strategy, Trade, ApiKey


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Strategy.

    Отображает список стратегий с полями: имя, пользователь, символ, активность и дата создания.
    """
    list_display = ['name', 'user', 'symbol', 'is_active', 'created_at']


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Trade.

    Отображает список трейдов с полями: стратегия, символ, действие, сумма, цена, прибыль/убыток и время.
    """
    list_display = ['strategy', 'symbol', 'action', 'amount', 'price', 'profit_loss', 'timestamp']


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели ApiKey.

    Отображает список API-ключей с полями: пользователь, биржа и дата создания.
    """
    list_display = ['user', 'exchange', 'created_at']
