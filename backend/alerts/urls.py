from django.urls import path

from . import views

"""
URL-шаблоны для приложения alerts.

Определяет маршруты для создания оповещений и отправки уведомлений.
"""

urlpatterns = [
    path("create/", views.create_alert, name="create_alert"),
    path("<int:rule_id>/notify/", views.send_notification, name="notify"),
]
