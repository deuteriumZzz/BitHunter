from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'user', 'symbol', 'title', 'description', 'url', 'sentiment', 'timestamp']
        read_only_fields = ['id', 'timestamp']  # Только чтение для авто-полей
