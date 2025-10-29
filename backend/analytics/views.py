from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .models import AnalyticsData, Prediction
from api.serializers import AnalyticsSerializer
from .tasks import predict_price, analyze_news, train_model_task
import ccxt
import tensorflow as tf
import numpy as np
import logging
from django_prometheus.models import model_to_counter
from .models import Trade

logger = logging.getLogger(__name__)

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsData.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [IsAuthenticated]  # Аутентификация
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['symbol']

    def get_queryset(self):
        # Фильтрация по пользователю для безопасности
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def history(self, request):
        symbol = request.query_params.get('symbol')
        period = request.query_params.get('period', '1d')
        if not symbol:
            return Response({'error': 'Symbol required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Кэширование: Проверяем кэш
        cache_key = f'history_{symbol}_{period}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'data': cached_data})
        
        try:
            exchange = ccxt.binance()
            # Получение исторических данных (пример для OHLCV)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=period, limit=100)
            data = [{'timestamp': o[0], 'open': o[1], 'high': o[2], 'low': o[3], 'close': o[4], 'volume': o[5]} for o in ohlcv]
            
            # Сохранение в AnalyticsData для кэширования
            AnalyticsData.objects.create(user=request.user, symbol=symbol, data=data)
            cache.set(cache_key, data, timeout=3600)  # Кэш на 1 час
            
            return Response({'data': data})
        except Exception as e:
            logger.error(f"Error in history: {e}")
            return Response({'error': 'Failed to fetch data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def predict(self, request):
        symbol = request.data.get('symbol')
        data_input = request.data.get('data')  # Ожидаем numpy-like данные
        if not symbol or not data_input:
            return Response({'error': 'Symbol and data required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Загрузка модели (предполагаем путь)
            model = tf.keras.models.load_model('analytics/model.h5')
            data_np = np.array(data_input)
            prediction = model.predict(data_np).tolist()
            
            # Сохранение в Prediction (с action и profit_loss, если предоставлены)
            action = request.data.get('action', 0)  # Default hold
            profit_loss = request.data.get('profit_loss', 0.0)
            pred_obj = Prediction.objects.create(
                user=request.user,
                symbol=symbol,
                predicted_price=prediction[0][0] if prediction else 0,  # Пример для цены
                action=action,
                profit_loss=profit_loss
            )
            
            return Response({'prediction': prediction, 'saved_id': pred_obj.id})
        except Exception as e:
            logger.error(f"Error in predict: {e}")
            return Response({'error': 'Prediction failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def news_analysis(self, request):
        symbol = request.data.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sentiment = analyze_news.delay(symbol).get()  # Синхронное ожидание
            return Response({'sentiment': sentiment})
        except Exception as e:
            logger.error(f"Error in news_analysis: {e}")
            return Response({'error': 'Analysis failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def train_model(self, request):
        try:
            train_model_task.delay()
            return Response({'status': 'Training started'})
        except Exception as e:
            logger.error(f"Error in train_model: {e}")
            return Response({'error': 'Training failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_profit(request):
    trades = Trade.objects.filter(user=request.user)
    profit = sum((t.sell_price - t.buy_price) * t.amount for t in trades if t.sell_price)
    model_to_counter(Trade, 'trades_count').inc()
    return Response({'profit': profit})