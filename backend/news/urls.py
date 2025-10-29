"""
Модуль URL-конфигурации для приложения новостей.

Определяет маршруты для API новостей с использованием DRF DefaultRouter.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import NewsViewSet


router = DefaultRouter()
router.register(r'news', NewsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
