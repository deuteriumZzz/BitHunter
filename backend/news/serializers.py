from rest_framework import serializers

from .models import News


class NewsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели News.

    Преобразует объекты News в JSON и обратно,
    с полями для чтения и записи, и read_only полями для id и timestamp.
    """

    class Meta:
        model = News
        fields = [
            'id',
            'user',
            'symbol',
            'title',
            'description',
            'url',
            'sentiment',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
