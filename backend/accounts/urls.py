"""
Модуль URL-шаблонов для приложения.

Определяет маршрутизацию API с использованием DefaultRouter от Django REST Framework,
включая маршруты для UserViewSet и UserProfileViewSet, а также дополнительный путь для отключения 2FA.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserProfileViewSet, disable_2fa


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('disable-2fa/', disable_2fa, name='disable_2fa'),
]
