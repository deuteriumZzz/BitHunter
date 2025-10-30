from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Преобразует данные пользователя в формат JSON и обратно.
    Включает поля: id, username, email.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели UserProfile.

    Преобразует данные профиля пользователя в формат JSON и обратно.
    Включает вложенный сериализатор User, а также поля для API-ключа и секрета.
    Поля api_key и secret предназначены только для записи и не обязательны.
    """

    user = UserSerializer()
    api_key = serializers.CharField(write_only=True, required=False)
    secret = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'telegram_chat_id', 'balance', 'api_key', 'secret']

    def create(self, validated_data):
        """
        Создает новый экземпляр UserProfile.

        Извлекает api_key и secret из validated_data, создает профиль,
        устанавливает API-ключ и секрет если они предоставлены, затем сохраняет.

        :param validated_data: Проверенные данные для создания профиля.
        :return: Созданный экземпляр UserProfile.
        """
        api_key = validated_data.pop('api_key', '')
        secret = validated_data.pop('secret', '')
        profile = super().create(validated_data)
        if api_key:
            profile.set_api_key(api_key)
        if secret:
            profile.set_secret(secret)
        profile.save()
        return profile
