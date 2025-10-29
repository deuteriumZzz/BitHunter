from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
import pyotp

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # Ограничение: пользователи могут видеть/редактировать только свой профиль (необязательно, но безопаснее)
    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    user = request.user
    try:
        profile = user.userprofile  # Получаем профиль через OneToOneField
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    secret = profile.generate_otp_secret()  # Генерируем секрет через профиль
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="BitHunter")
    return Response({
        'secret': secret,
        'provisioning_uri': provisioning_uri,
        'message': 'Scan the QR code in your authenticator app and provide the token to verify.'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    try:
        profile = user.userprofile  # Получаем профиль
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if profile.verify_otp(token):  # Проверяем токен через профиль
        profile.is_2fa_enabled = True
        profile.save()
        return Response({'message': '2FA enabled successfully'})
    else:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required for verification'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    try:
        profile = user.userprofile  # Получаем профиль
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Проверяем токен для безопасности (чтобы подтвердить, что пользователь имеет доступ)
    if not profile.verify_otp(token):
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Отключаем 2FA и очищаем секрет
    profile.is_2fa_enabled = False
    profile.otp_secret = ''  # Очищаем секрет для безопасности
    profile.save()
    return Response({'message': '2FA disabled successfully'})
