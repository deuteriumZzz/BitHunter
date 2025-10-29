"""
Модуль представлений для приложения новостей.

Содержит ViewSet для модели News с поддержкой фильтрации, сортировки и аутентификации.
"""

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from .models import News
from .serializers import NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели News.

    Предоставляет CRUD-операции с фильтрацией по символу, пользователю и сентименту,
    сортировкой по времени и сентименту. По умолчанию сортировка по времени убывания.
    Для аутентифицированных пользователей фильтрует новости только по текущему пользователю.
    """

    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol', 'user', 'sentiment']  # Фильтры
    ordering_fields = ['timestamp', 'sentiment']  # Сортировка
    ordering = ['-timestamp']  # По умолчанию по времени убывания

    def get_queryset(self):
        """
        Возвращает queryset новостей.

        Если пользователь аутентифицирован, фильтрует новости по текущему пользователю.
        В противном случае возвращает все новости.
        """
        user = self.request.user
        if user.is_authenticated:
            return News.objects.filter(user=user)
        return News.objects.all()
