from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    api_key = serializers.CharField(write_only=True, required=False)
    secret = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'telegram_chat_id', 'balance', 'api_key', 'secret']

    def create(self, validated_data):
        api_key = validated_data.pop('api_key', '')
        secret = validated_data.pop('secret', '')
        profile = super().create(validated_data)
        if api_key:
            profile.set_api_key(api_key)
        if secret:
            profile.set_secret(secret)
        profile.save()
        return profile
