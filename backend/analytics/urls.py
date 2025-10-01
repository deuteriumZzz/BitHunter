from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict, name='predict'),
    path('news/', views.news_analysis, name='news'),
    path('train/', views.train_model, name='train'),
]
