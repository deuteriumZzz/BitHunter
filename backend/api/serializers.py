from rest_framework import serializers
from trading.models import ApiKey, Strategy, Trade
from analytics.models import AnalyticsData, Prediction  # Обновлено: AnalyticsData вместо HistoricalData
from alerts.models import Alert

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'user', 'exchange', 'api_key', 'secret', 'created_at']
        extra_kwargs = {
            'api_key': {'write_only': True},  # Не возвращать в ответе
            'secret': {'write_only': True},
        }

class StrategySerializer(serializers.ModelSerializer):
    api_key_name = serializers.CharField(source='api_key.exchange', read_only=True)  # ДОБАВЛЕНО: Для отображения названия биржи

    class Meta:
        model = Strategy
        fields = ['id', 'user', 'name', 'description', 'symbol', 'is_active', 'parameters', 'api_key', 'api_key_name', 'profit_loss', 'created_at', 'updated_at']

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'strategy', 'symbol', 'action', 'amount', 'price', 'profit_loss', 'timestamp']

# ДОБАВЛЕНО: Сериализатор для новой модели AnalyticsData (замена HistoricalDataSerializer)
class AnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsData
        fields = ['id', 'user', 'symbol', 'data', 'timestamp']
        read_only_fields = ['user']  # Пользователь устанавливается автоматически из запроса

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'timestamp', 'predicted_price', 'action', 'profit_loss', 'user']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'user', 'symbol', 'condition', 'message', 'is_active', 'created_at']
