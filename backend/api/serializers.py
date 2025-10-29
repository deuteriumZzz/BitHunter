from rest_framework import serializers

from trading.models import ApiKey, Strategy, Trade
from analytics.models import AnalyticsData, Prediction
from alerts.models import AlertRule, Notification


class ApiKeySerializer(serializers.ModelSerializer):
    """Сериализатор для модели ApiKey, обеспечивающий сериализацию и десериализацию данных API-ключей."""

    class Meta:
        model = ApiKey
        fields = [
            'id', 'user', 'exchange', 'api_key',
            'secret', 'created_at'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'secret': {'write_only': True},
        }


class StrategySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Strategy, включающий дополнительное поле для отображения названия биржи API-ключа."""

    api_key_name = serializers.CharField(
        source='api_key.exchange', read_only=True
    )

    class Meta:
        model = Strategy
        fields = [
            'id', 'user', 'name', 'description', 'symbol',
            'is_active', 'parameters', 'api_key', 'api_key_name',
            'profit_loss', 'created_at', 'updated_at'
        ]


class TradeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Trade, обеспечивающий сериализацию и десериализацию данных сделок."""

    class Meta:
        model = Trade
        fields = [
            'id', 'strategy', 'symbol', 'action', 'amount',
            'price', 'profit_loss', 'timestamp'
        ]


class AnalyticsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AnalyticsData, заменяющий HistoricalDataSerializer."""

    class Meta:
        model = AnalyticsData
        fields = [
            'id', 'user', 'symbol', 'data', 'timestamp'
        ]
        read_only_fields = ['user']


class PredictionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Prediction, обеспечивающий сериализацию и десериализацию данных прогнозов."""

    class Meta:
        model = Prediction
        fields = [
            'id', 'timestamp', 'predicted_price', 'action',
            'profit_loss', 'user'
        ]


class AlertRuleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AlertRule, обеспечивающий сериализацию и десериализацию данных правил оповещений."""

    class Meta:
        model = AlertRule
        fields = [
            'id', 'user', 'symbol', 'condition', 'value',
            'is_active', 'created_at', 'updated_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Notification, обеспечивающий сериализацию и десериализацию данных уведомлений."""

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'alert_rule', 'message',
            'is_sent', 'sent_at', 'created_at'
        ]
