from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
import pyotp  # Добавлен импорт для 2FA

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Баланс для трейдинга
    api_key_encrypted = models.TextField(blank=True)  # Шифрованный API-ключ для биржи (например, Binance)
    secret_key_encrypted = models.TextField(blank=True)  # Шифрованный секретный ключ для биржи
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)  # Для алертов в Telegram
    otp_secret = models.CharField(max_length=32, blank=True, help_text="Secret for 2FA (OTP)")  # Для 2FA
    is_2fa_enabled = models.BooleanField(default=False, help_text="Whether 2FA is enabled")  # Добавлено для 2FA
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def set_api_key(self, api_key):
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.api_key_encrypted = cipher.encrypt(api_key.encode()).decode()

    def get_api_key(self):
        if not self.api_key_encrypted:
            return None
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(self.api_key_encrypted.encode()).decode()

    def set_secret_key(self, secret_key):
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.secret_key_encrypted = cipher.encrypt(secret_key.encode()).decode()

    def get_secret_key(self):
        if not self.secret_key_encrypted:
            return None
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(self.secret_key_encrypted.encode()).decode()

    # Методы для 2FA (интегрированы из добавленного кода)
    def generate_otp_secret(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save()
        return self.otp_secret

    def verify_otp(self, token):
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token)

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
