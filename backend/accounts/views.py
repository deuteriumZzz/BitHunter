"""
Модуль представлений для приложения.

Содержит ViewSets для моделей User и UserProfile, а также функции для управления двухфакторной аутентификацией (2FA).
"""

from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import pyotp

from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели User.
    
    Предоставляет CRUD-операции для пользователей с ограничением доступа:
    пользователи могут видеть и редактировать только свой профиль.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает queryset, ограниченный текущим пользователем.
        
        :return: QuerySet пользователей, фильтрованный по ID текущего пользователя.
        """
        return self.queryset.filter(id=self.request.user.id)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели UserProfile.
    
    Предоставляет CRUD-операции для профилей пользователей с ограничением доступа:
    пользователи могут видеть и редактировать только свой профиль.
    """
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Возвращает queryset, ограниченный текущим пользователем.
        
        :return: QuerySet профилей, фильтрованный по пользователю.
        """
        return self.queryset.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Включает двухфакторную аутентификацию для пользователя.
    
    Генерирует секрет OTP, создает provisioning URI для QR-кода
    и возвращает данные для настройки аутентификатора.
    
    :param request: HTTP-запрос с данными пользователя.
    :return: Response с секретом, URI и сообщением.
    """
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    secret = profile.generate_otp_secret()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.username,
        issuer_name="BitHunter"
    )
    return Response({
        'secret': secret,
        'provisioning_uri': provisioning_uri,
        'message': 'Scan the QR code in your authenticator app and provide the token to verify.'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """
    Проверяет токен для включения 2FA.
    
    Проверяет предоставленный токен OTP и, если он верен,
    включает 2FA для профиля пользователя.
    
    :param request: HTTP-запрос с токеном.
    :return: Response с сообщением об успехе или ошибке.
    """
    token = request.data.get('token')
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if profile.verify_otp(token):
        profile.is_2fa_enabled = True
        profile.save()
        return Response({'message': '2FA enabled successfully'})
    else:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Отключает двухфакторную аутентификацию для пользователя.
    
    Проверяет токен для подтверждения доступа, затем отключает 2FA
    и очищает секрет OTP.
    
    :param request: HTTP-запрос с токеном для верификации.
    :return: Response с сообщением об успехе или ошибке.
    """
    token = request.data.get('token')
    if not token:
        return Response(
            {'error': 'Token is required for verification'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not profile.verify_otp(token):
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    profile.is_2fa_enabled = False
    profile.otp_secret = ''
    profile.save()
    return Response({'message': '2FA disabled successfully'})
