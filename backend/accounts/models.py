import pyotp
from cryptography.fernet import Fernet, InvalidToken

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Модель профиля пользователя для хранения дополнительной информации,
    включая баланс, зашифрованные ключи API, настройки 2FA и Telegram.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    api_key_encrypted = models.TextField(
        blank=True
    )
    secret_key_encrypted = models.TextField(
        blank=True
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Telegram Chat ID must be numeric."
    )
    otp_secret = models.CharField(
        max_length=32,
        blank=True,
        help_text="Secret for 2FA (OTP)"
    )
    is_2fa_enabled = models.BooleanField(
        default=False,
        help_text="Whether 2FA is enabled"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление профиля пользователя.
        """
        return f"{self.user.username}'s profile"

    def clean(self):
        """
        Валидация полей модели.
        """
        super().clean()
        if self.telegram_chat_id and not self.telegram_chat_id.isdigit():
            raise ValidationError("Telegram Chat ID must be numeric.")

    def set_api_key(self, api_key):
        """
        Шифрует и сохраняет API-ключ для биржи.

        :param api_key: Нешифрованный API-ключ в виде строки.
        """
        try:
            cipher = Fernet(settings.FERNET_KEY.encode())
            self.api_key_encrypted = cipher.encrypt(api_key.encode()).decode()
        except Exception as e:
            raise ValidationError(f"Error encrypting API key: {str(e)}")

    def get_api_key(self):
        """
        Дешифрует и возвращает API-ключ для биржи.

        :return: Дешифрованный API-ключ или None, если ключ не установлен
        или ошибка.
        """
        if not self.api_key_encrypted:
            return None
        try:
            cipher = Fernet(settings.FERNET_KEY.encode())
            return cipher.decrypt(self.api_key_encrypted.encode()).decode()
        except (InvalidToken, ValueError, Exception):
            return None  # Логируйте ошибку в продакшене, если нужно

    def set_secret_key(self, secret_key):
        """
        Шифрует и сохраняет секретный ключ для биржи.

        :param secret_key: Нешифрованный секретный ключ в виде строки.
        """
        try:
            cipher = Fernet(settings.FERNET_KEY.encode())
            self.secret_key_encrypted = cipher.encrypt(
                secret_key.encode()).decode()
        except Exception as e:
            raise ValidationError(f"Error encrypting secret key: {str(e)}")

    def get_secret_key(self):
        """
        Дешифрует и возвращает секретный ключ для биржи.

        :return: Дешифрованный секретный ключ или None, если ключ
        не установлен или ошибка.
        """
        if not self.secret_key_encrypted:
            return None
        try:
            cipher = Fernet(settings.FERNET_KEY.encode())
            return cipher.decrypt(self.secret_key_encrypted.encode()).decode()
        except (InvalidToken, ValueError, Exception):
            return None  # Логируйте ошибку в продакшене, если нужно

    def generate_otp_secret(self):
        """
        Генерирует и сохраняет секрет для 2FA, если он не существует.

        :return: Секрет для 2FA в виде строки.
        """
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save()
        return self.otp_secret

    def verify_otp(self, token):
        """
        Проверяет введенный OTP-токен для 2FA.

        :param token: OTP-токен для проверки.
        :return: True, если токен верный, иначе False.
        """
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token)

    def save(self, *args, **kwargs):
        self.full_clean()  # Автоматическая валидация перед сохранением
        super().save(*args, **kwargs)
        # Инвалидация кэша
        cache.delete(f'profile_{self.user.id}')

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        indexes = [
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']  # Новые профили сверху для удобства


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Сигнал для автоматического создания профиля пользователя
    при создании нового пользователя.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Сигнал для автоматического сохранения профиля пользователя
    при обновлении пользователя.
    """
    # Безопасная проверка: если профиль существует, сохраняем
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
