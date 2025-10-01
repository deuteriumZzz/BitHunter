from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import async_train_rl

router = DefaultRouter()
# Регистрация ViewSets для моделей
router.register(r'apikeys', views.ApiKeyViewSet)
router.register(r'strategies', views.StrategyViewSet)
router.register(r'trades', views.TradeViewSet)
router.register(r'historicaldata', views.HistoricalDataViewSet)
router.register(r'predictions', views.PredictionViewSet)
router.register(r'alerts', views.AlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Кастомные эндпоинты для задач
    path('run-bot/<int:strategy_id>/', views.run_bot_view, name='run_bot'),
    path('train-model/', views.train_model_view, name='train_model'),
    path('check-alerts/', views.check_alerts_view, name='check_alerts'),
    path('async-train/', async_train_rl, name='async_train_rl'),
]
