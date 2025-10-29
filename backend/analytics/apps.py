from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Конфигурация для приложения Django 'analytics'.
    
    Этот класс определяет метаданные приложения, включая его имя, человеко-читаемое
    название (verbose_name) для отображения в админ-интерфейсе и других интерфейсах,
    а также тип поля по умолчанию для первичных ключей моделей.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Аналитика'
