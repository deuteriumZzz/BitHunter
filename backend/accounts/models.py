import pyotp

from cryptography.fernet import Fernet

from django.conf import settings
from django.contrib.auth.models import User
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
        null=True
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

    def set_api_key(self, api_key):
        """
        Шифрует и сохраняет API-ключ для биржи.

        :param api_key: Нешифрованный API-ключ в виде строки.
        """
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.api_key_encrypted = cipher.encrypt(
            api_key.encode()
        ).decode()

    def get_api_key(self):
        """
        Дешифрует и возвращает API-ключ для биржи.

        :return: Дешифрованный API-ключ или None, если ключ не установлен.
        """
        if not self.api_key_encrypted:
            return None
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(
            self.api_key_encrypted.encode()
        ).decode()

    def set_secret_key(self, secret_key):
        """
        Шифрует и сохраняет секретный ключ для биржи.

        :param secret_key: Нешифрованный секретный ключ в виде строки.
        """
        cipher = Fernet(settings.SECRET_KEY.encode())
        self.secret_key_encrypted = cipher.encrypt(
            secret_key.encode()
        ).decode()

    def get_secret_key(self):
        """
        Дешифрует и возвращает секретный ключ для биржи.

        :return: Дешифрованный секретный ключ или None, если ключ не установлен.
        """
        if not self.secret_key_encrypted:
            return None
        cipher = Fernet(settings.SECRET_KEY.encode())
        return cipher.decrypt(
            self.secret_key_encrypted.encode()
        ).decode()

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

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        indexes = [
            models.Index(fields=['user']),
        ]


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
    instance.userprofile.save()
