from django.apps import AppConfig


class AlertsConfig(AppConfig):
    """
    Конфигурация приложения Alerts.

    Определяет настройки для приложения оповещений, включая авто-поле и отображаемое имя.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "alerts"
    verbose_name = "Оповещения"
