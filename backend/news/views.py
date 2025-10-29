from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import News
from .serializers import NewsSerializer

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol', 'user', 'sentiment']  # Фильтры
    ordering_fields = ['timestamp', 'sentiment']  # Сортировка
    ordering = ['-timestamp']  # По умолчанию по времени убывания

    def get_queryset(self):
        # Опционально: фильтр по пользователю (если аутентифицирован)
        user = self.request.user
        if user.is_authenticated:
            return News.objects.filter(user=user)
        return News.objects.all()
