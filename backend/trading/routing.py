"""
Модуль маршрутизации для WebSocket соединений.

Определяет URL-шаблоны для WebSocket эндпоинтов, используя Django Channels.
Включает маршрут для TradingConsumer, обрабатывающего реал-тайм данные трейдинга.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/trading/", consumers.TradingConsumer.as_asgi()),
]
