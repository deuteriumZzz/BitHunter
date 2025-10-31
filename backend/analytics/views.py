"""
Модуль представлений для аналитики и предсказаний.

Этот модуль содержит ViewSet для работы с аналитическими данными,
предсказаниями цен, анализом новостей и обучением моделей.
Включает интеграцию с S3, Celery, TensorFlow и мониторингом.
"""

import logging

from api.serializers import AnalyticsSerializer
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from django_prometheus.models import model_to_counter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AnalyticsData, Prediction, Trade
from .tasks import (
    analyze_data_with_news,
    predict_price,
    train_ml_model,
)  # Исправлены импорты на основе tasks.py

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с аналитическими данными.

    Предоставляет CRUD-операции для AnalyticsData,
    а также кастомные действия для истории, предсказаний,
    анализа новостей и обучения моделей.
    """

    queryset = AnalyticsData.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["symbol"]

    def get_queryset(self):
        """
        Возвращает queryset, отфильтрованный по текущему пользователю.

        Returns:
            QuerySet: Отфильтрованные объекты AnalyticsData.
        """
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def history(self, request):
        """
        Получает исторические данные для символа, используя задачу bulk_load_historical_data.

        Args:
            request: HTTP-запрос с параметрами symbol и period.

        Returns:
            Response: Данные истории или ошибка.
        """
        symbol = request.query_params.get("symbol")
        period = request.query_params.get(
            "period", "1h"
        )  # Изменено на '1h' по умолчанию, как в tasks.py
        if not symbol:
            return Response(
                {"error": "Symbol required"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"history_{symbol}_{period}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({"data": cached_data})

        try:
            # Вызываем задачу bulk_load_historical_data для загрузки данных
            from .tasks import bulk_load_historical_data

            bulk_load_historical_data.delay(
                symbol, period, 100
            )  # limit=100, как в оригинале

            # После вызова задачи, получаем данные из БД (предполагаем, что задача сохранила их)
            # Поскольку bulk_load_historical_data сохраняет данные, извлекаем их
            analytics_data = AnalyticsData.objects.filter(
                symbol=symbol, user=request.user
            ).order_by("-timestamp")[:100]
            data = [
                {
                    "timestamp": obj.timestamp,
                    "open": obj.open,
                    "high": obj.high,
                    "low": obj.low,
                    "close": obj.close,
                    "volume": obj.volume,
                }
                for obj in analytics_data
            ]

            cache.set(cache_key, data, timeout=3600)

            return Response({"data": data})
        except Exception as e:
            logger.error(f"Error in history: {e}")
            return Response(
                {"error": "Failed to fetch data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def predict(self, request):
        """
        Выполняет предсказание цены с использованием задачи predict_price.

        Args:
            request: HTTP-запрос с данными symbol и data.

        Returns:
            Response: Предсказание (действие) или ошибка.
        """
        symbol = request.data.get("symbol")
        if not symbol:
            return Response(
                {"error": "Symbol required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Вызываем задачу predict_price, которая использует RL-модель и сохраняет результат
            action = (
                predict_price.delay().get()
            )  # predict_price не принимает параметры, использует last_hist

            # Получаем последнее предсказание из БД
            last_prediction = Prediction.objects.filter(user=request.user).last()
            if last_prediction:
                return Response(
                    {
                        "action": action,
                        "predicted_price": last_prediction.predicted_price,
                        "saved_id": last_prediction.id,
                    }
                )
            else:
                return Response({"action": action})
        except Exception as e:
            logger.error(f"Error in predict: {e}")
            return Response(
                {"error": "Prediction failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def news_analysis(self, request):
        """
        Выполняет анализ новостей для символа с использованием задачи analyze_data_with_news.

        Args:
            request: HTTP-запрос с параметром symbol.

        Returns:
            Response: Результат анализа или ошибка.
        """
        symbol = request.data.get("symbol")
        if not symbol:
            return Response(
                {"error": "Symbol required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Вызываем задачу analyze_data_with_news
            result = analyze_data_with_news.delay(symbol, request.user.id).get()
            return Response({"result": result})
        except Exception as e:
            logger.error(f"Error in news_analysis: {e}")
            return Response(
                {"error": "Analysis failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def train_model(self, request):
        """
        Запускает задачу обучения модели с использованием train_ml_model.

        Args:
            request: HTTP-запрос.

        Returns:
            Response: Статус или ошибка.
        """
        try:
            # Вызываем задачу train_ml_model
            result = train_ml_model.delay()
            return Response({"status": "Training started", "task_id": result.id})
        except Exception as e:
            logger.error(f"Error in train_model: {e}")
            return Response(
                {"error": "Training failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def calculate_profit(request):
    """
    Рассчитывает общую прибыль по сделкам пользователя.

    Args:
        request: HTTP-запрос с аутентифицированным пользователем.

    Returns:
        Response: Общая прибыль.
    """
    trades = Trade.objects.filter(user=request.user)
    profit = sum(
        (t.sell_price - t.buy_price) * t.amount for t in trades if t.sell_price
    )
    model_to_counter(Trade, "trades_count").inc()
    return Response({"profit": profit})
