from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# Новые импорты для оптимизации и кэширования
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch

# Импорты для async views
from django.http import JsonResponse
from asgiref.sync import sync_to_async
import asyncio

# Импорты моделей
from trading.models import ApiKey, Strategy, Trade
from analytics.models import AnalyticsData, Prediction  # Исправлено: HistoricalData → AnalyticsData
from alerts.models import Alert

# Импорты сериализаторов (добавлено, предполагаю, что они есть в serializers.py)
from .serializers import ApiKeySerializer, StrategySerializer, TradeSerializer, AnalyticsSerializer, PredictionSerializer, AlertSerializer  # Исправлено: AnalyticsDataSerializer → AnalyticsSerializer

# Импорты задач
from trading.tasks import run_bot
from analytics.tasks import train_ml_model
from alerts.tasks import check_alerts

class ApiKeyViewSet(viewsets.ModelViewSet):
    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['exchange']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('user')  # Оптимизация FK

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('user').prefetch_related('trades')  # Предзагрузка связанных trades

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol', 'action']
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'strategy').prefetch_related(
            Prefetch('strategy__analytics_data', queryset=AnalyticsData.objects.only('id', 'symbol', 'timestamp'))  # Исправлено: historical_data → analytics_data, HistoricalData → AnalyticsData
        )

class AnalyticsDataViewSet(viewsets.ModelViewSet):  # Исправлено: HistoricalDataViewSet → AnalyticsDataViewSet
    queryset = AnalyticsData.objects.all()  # Исправлено: HistoricalData → AnalyticsData
    serializer_class = AnalyticsSerializer  # Исправлено: AnalyticsDataSerializer → AnalyticsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol']
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('user')  # Оптимизация FK

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['timestamp']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('user')  # Оптимизация FK

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    @method_decorator(cache_page(60 * 15))  # Кэширование на 15 минут
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('user')  # Оптимизация FK

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Кастомные API views для запуска задач
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_bot_view(request, strategy_id):
    """Запустить бота для стратегии (асинхронно через Celery)."""
    try:
        strategy = Strategy.objects.get(id=strategy_id, user=request.user)
        run_bot.delay(strategy_id)  # Вызов задачи
        return Response({'status': 'Bot started for strategy', 'strategy_id': strategy_id}, status=status.HTTP_200_OK)
    except Strategy.DoesNotExist:
        return Response({'error': 'Strategy not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_model_view(request):
    """Запустить обучение ML-модели (асинхронно)."""
    train_ml_model.delay()
    return Response({'status': 'Model training started'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_alerts_view(request):
    """Проверить алерты (асинхронно)."""
    check_alerts.delay()
    return Response({'status': 'Alerts check started'}, status=status.HTTP_200_OK)

# Async view для тяжелых операций
@sync_to_async
def heavy_task():
    """Имитация тяжелой операции (e.g., RL-обучение). Замените на реальную логику (e.g., вызов Stable Baselines3)."""
    import time
    time.sleep(5)  # Имитация задержки
    return {"status": "completed"}

async def async_train_rl(request):
    """Асинхронный эндпоинт для запуска RL-обучения. Доступен по /api/async-train/."""
    result = await heavy_task()
    return JsonResponse(result)
