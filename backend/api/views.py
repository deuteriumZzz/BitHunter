"""
Views для приложения API.
Определяет ViewSets для моделей и кастомные API views для запуска задач.
"""

# Импорты стандартной библиотеки
import asyncio

# Импорты Django и DRF
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Импорты сторонних библиотек
from asgiref.sync import sync_to_async
from django_filters.rest_framework import DjangoFilterBackend

# Импорты локальных модулей
from alerts.models import AlertRule, Notification
from alerts.tasks import check_alerts
from analytics.models import AnalyticsData, Prediction
from analytics.tasks import train_ml_model
from trading.models import ApiKey, Strategy, Trade
from trading.tasks import run_bot

from .serializers import (
    AlertRuleSerializer, AnalyticsSerializer, ApiKeySerializer,
    NotificationSerializer, PredictionSerializer, StrategySerializer,
    TradeSerializer,
)


class StandardPagination(PageNumberPagination):
    """
    Стандартная пагинация для API.
    Устанавливает размер страницы по умолчанию и максимальный размер.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели ApiKey.
    Предоставляет CRUD-операции с фильтрацией, сортировкой и кэшированием.
    """
    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['exchange']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список ApiKey с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с select_related для FK.
        """
        return super().get_queryset().select_related('user')

    def perform_create(self, serializer):
        """
        Создать ApiKey, автоматически присваивая текущего пользователя.
        """
        serializer.save(user=self.request.user)


class StrategyViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Strategy.
    Предоставляет CRUD-операции с фильтрацией, сортировкой и предзагрузкой.
    """
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список Strategy с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с select_related и prefetch_related.
        """
        return (
            super().get_queryset()
            .select_related('user')
            .prefetch_related('trades')
        )

    def perform_create(self, serializer):
        """
        Создать Strategy, автоматически присваивая текущего пользователя.
        """
        serializer.save(user=self.request.user)


class TradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Trade.
    Предоставляет CRUD-операции с фильтрацией и оптимизацией запросов.
    """
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol', 'action']
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список Trade с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с select_related и prefetch_related.
        """
        return (
            super().get_queryset()
            .select_related('user', 'strategy')
            .prefetch_related(
                Prefetch(
                    'strategy__analytics_data',
                    queryset=AnalyticsData.objects.only(
                        'id', 'symbol', 'timestamp'
                    )
                )
            )
        )


class AnalyticsDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели AnalyticsData.
    Предоставляет CRUD-операции с пагинацией, фильтрацией и кэшированием.
    """
    queryset = AnalyticsData.objects.all()
    serializer_class = AnalyticsSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol']
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список AnalyticsData с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с фильтрацией по пользователю.
        """
        return (
            self.queryset
            .filter(user=self.request.user)
            .select_related('user')
        )


class PredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Prediction.
    Предоставляет CRUD-операции с фильтрацией и кэшированием.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список Prediction с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с фильтрацией по пользователю.
        """
        return (
            self.queryset
            .filter(user=self.request.user)
            .select_related('user')
        )


class AlertRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели AlertRule.
    Предоставляет CRUD-операции с фильтрацией, сортировкой и кэшированием.
    """
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список AlertRule с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с фильтрацией по пользователю.
        """
        return (
            self.queryset
            .filter(user=self.request.user)
            .select_related('user')
        )

    def perform_create(self, serializer):
        """
        Создать AlertRule, автоматически присваивая текущего пользователя.
        """
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Notification.
    Предоставляет CRUD-операции с фильтрацией, сортировкой и кэшированием.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_sent']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получить список Notification с кэшированием.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Оптимизированный queryset с фильтрацией по пользователю.
        """
        return (
            self.queryset
            .filter(user=self.request.user)
            .select_related('user', 'alert_rule')
        )


# Кастомные API views для запуска задач
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_bot_view(request, strategy_id):
    """
    Запустить бота для стратегии (асинхронно через Celery).
    """
    try:
        strategy = Strategy.objects.get(
            id=strategy_id, user=request.user
        )
        run_bot.delay(strategy_id)  # Вызов задачи
        return Response(
            {
                'status': 'Bot started for strategy',
                'strategy_id': strategy_id
            },
            status=status.HTTP_200_OK
        )
    except Strategy.DoesNotExist:
        return Response(
            {'error': 'Strategy not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_model_view(request):
    """
    Запустить обучение ML-модели (асинхронно).
    """
    train_ml_model.delay()
    return Response(
        {'status': 'Model training started'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_alerts_view(request):
    """
    Проверить алерты (асинхронно).
    """
    check_alerts.delay()
    return Response(
        {'status': 'Alerts check started'},
        status=status.HTTP_200_OK
    )


# Async view для тяжелых операций
@sync_to_async
def heavy_task():
    """
    Имитация тяжелой операции (e.g., RL-обучение).
    Замените на реальную логику (e.g., вызов Stable Baselines3).
    """
    import time
    time.sleep(5)  # Имитация задержки
    return {"status": "completed"}


async def async_train_rl(request):
    """
    Асинхронный эндпоинт для запуска RL-обучения.
    Доступен по /api/async-train/.
    """
    result = await heavy_task()
    return JsonResponse(result)
