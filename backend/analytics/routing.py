"""
Модуль для определения URL-шаблонов WebSocket соединений в приложении.
Используется для маршрутизации WebSocket запросов к соответствующим потребителям (consumers).
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/analytics/", consumers.AnalyticsConsumer.as_asgi()),
]
