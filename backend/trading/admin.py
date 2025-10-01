from django.contrib import admin
from .models import Strategy, Trade, ApiKey

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'symbol', 'is_active', 'created_at']

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['strategy', 'symbol', 'action', 'amount', 'price', 'profit_loss', 'timestamp']

@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'exchange', 'created_at']
