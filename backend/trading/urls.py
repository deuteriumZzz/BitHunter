from django.urls import path
from . import views

urlpatterns = [
    path('', views.strategy_list, name='strategy_list'),
    path('create/', views.strategy_create, name='strategy_create'),
    path('<int:strategy_id>/start/', views.start_bot, name='start_bot'),
    path('<int:strategy_id>/metrics/', views.strategy_metrics, name='strategy_metrics'),
    path('api-keys/', views.ApiKeyView.as_view(), name='api_keys'),
]
