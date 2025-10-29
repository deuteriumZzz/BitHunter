"""
Модуль для определения URL-шаблонов приложения.

Этот модуль содержит конфигурацию маршрутов для приложения Django,
включая пути для предсказаний, анализа новостей и обучения модели.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict, name='predict'),
    path('news/', views.news_analysis, name='news'),
    path('train/', views.train_model, name='train'),
]
