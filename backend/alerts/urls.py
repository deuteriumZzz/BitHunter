from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_alert, name='create_alert'),
    path('<int:rule_id>/notify/', views.send_notification, name='notify'),
]
