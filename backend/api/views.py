from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# Импорты моделей
from trading.models import ApiKey, Strategy, Trade
from analytics.models import HistoricalData, Prediction
from alerts.models import Alert

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

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol', 'action']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return self.queryset.filter(strategy__user=self.request.user)

class HistoricalDataViewSet(viewsets.ModelViewSet):
    queryset = HistoricalData.objects.all()
    serializer_class = HistoricalDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['symbol']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class PredictionViewSet(viewsets.ModelViewSet):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active', 'symbol']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

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
