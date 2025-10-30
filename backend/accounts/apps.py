from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Конфигурация для приложения Django 'accounts'.

    Этот класс определяет метаданные приложения, включая его имя,
    а также тип поля по умолчанию для первичных ключей моделей.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Аккаунты'
