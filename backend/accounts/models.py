from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Баланс для трейдинга
    api_key_encrypted = models.TextField(blank=True)  # Шифрованный API-ключ для биржи (например, Binance)
    secret_key_encrypted = models.TextField(blank=True)  # Шифрованный секретный ключ для биржи
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)  # Для алертов в Telegram
    otp_secret = models.CharField(max_length=32, blank=True)  # Для 2FA (OTP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def set_api_key(self, api_key):
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.api_key_encrypted = cipher.encrypt(api_key.encode()).decode()

    def get_api_key(self):
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(self.api_key_encrypted.encode()).decode()

    def set_secret_key(self, secret_key):
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.secret_key_encrypted = cipher.encrypt(secret_key.encode()).decode()

    def get_secret_key(self):
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(self.secret_key_encrypted.encode()).decode()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=['user']),
        ]

# Сигнал для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
