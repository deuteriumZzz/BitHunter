"""
Модуль представлений (views) для приложения трейдинга.

Содержит представления для управления стратегиями (список, создание, запуск бота, метрики)
и API-ключами. Включает шифрование чувствительных данных для API-ключей с улучшенной обработкой ошибок.

Добавлена оптимизация с помощью select_related и prefetch_related для улучшения производительности запросов.
"""

import os

from cryptography.fernet import Fernet
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets  # Добавлен импорт для ViewSets
from rest_framework.permissions import IsAuthenticated  # Для аутентификации в ViewSets

from .forms import ApiKeyForm, StrategyForm
from .models import ApiKey, Strategy
from .tasks import calculate_metrics, run_bot


@login_required
def strategy_list(request):
    """
    Отображает список стратегий текущего пользователя.

    Получает все стратегии, связанные с аутентифицированным пользователем,
    и рендерит шаблон списка стратегий.

    Параметры:
    - request: HttpRequest объект.

    Возвращает:
    - HttpResponse: Рендеренный шаблон 'trading/strategy_list.html' с контекстом стратегий.
    """
    strategies = (
        Strategy.objects.filter(user=request.user)
        .select_related("user")
        .prefetch_related("parameters")
    )  # Добавлена оптимизация для производительности
    return render(request, "trading/strategy_list.html", {"strategies": strategies})


@login_required
def strategy_create(request):
    """
    Обрабатывает создание новой стратегии.

    При GET-запросе отображает форму создания стратегии.
    При POST-запросе валидирует форму, сохраняет стратегию для текущего пользователя
    и перенаправляет на список стратегий.

    Параметры:
    - request: HttpRequest объект.

    Возвращает:
    - HttpResponse: Рендеренный шаблон 'trading/strategy_form.html' с формой
      или перенаправление на 'strategy_list'.
    """
    if request.method == "POST":
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            return redirect("strategy_list")
    else:
        form = StrategyForm()
    return render(request, "trading/strategy_form.html", {"form": form})


@login_required
def start_bot(request, strategy_id):
    """
    Запускает бота для указанной стратегии в демо-режиме.

    Проверяет, что стратегия принадлежит текущему пользователю,
    и асинхронно запускает задачу трейдинга с обработкой ошибок.

    Параметры:
    - request: HttpRequest объект.
    - strategy_id: ID стратегии (int).

    Возвращает:
    - JsonResponse: Статус 'started' или ошибку.
    """
    try:
        strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
        run_bot.delay(
            strategy_id
        )  # Исправлено: start_trading на run_bot, добавлен demo=True как параметр по умолчанию в задаче
        return JsonResponse({"status": "started"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def strategy_metrics(request, strategy_id):
    """
    Запускает асинхронный расчёт метрик для указанной стратегии и возвращает task_id.

    Проверяет, что стратегия принадлежит текущему пользователю,
    запускает задачу и возвращает ID задачи для последующего опроса статуса.
    Это обеспечивает асинхронность и предотвращает таймауты.

    Параметры:
    - request: HttpRequest объект.
    - strategy_id: ID стратегии (int).

    Возвращает:
    - JsonResponse: task_id для опроса или ошибку.
    """
    try:
        strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
        task = calculate_metrics.delay(strategy_id)
        return JsonResponse({"task_id": task.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Дополнительное представление для получения результата метрик по task_id (рекомендуется добавить в urls.py)
@login_required
def get_metrics_result(request, task_id):
    """
    Получает результат метрик по task_id.

    Параметры:
    - request: HttpRequest объект.
    - task_id: ID задачи Celery (str).

    Возвращает:
    - JsonResponse: Метрики или статус задачи.
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id)
    if result.ready():
        if result.successful():
            return JsonResponse(result.result)
        else:
            return JsonResponse({"error": str(result.info)}, status=500)
    else:
        return JsonResponse({"status": "pending"})


class ApiKeyView(View):
    """
    Представление для управления API-ключами.

    Обрабатывает GET-запросы для отображения списка ключей и формы создания,
    и POST-запросы для создания нового ключа с шифрованием чувствительных данных и обработкой ошибок.
    """

    @method_decorator(login_required)
    def get(self, request):
        """
        Отображает список API-ключей текущего пользователя и форму создания.

        Параметры:
        - request: HttpRequest объект.

        Возвращает:
        - HttpResponse: Рендеренный шаблон 'trading/api_keys.html' с контекстом ключей и формы.
        """
        keys = ApiKey.objects.filter(user=request.user)
        form = ApiKeyForm()
        return render(request, "trading/api_keys.html", {"keys": keys, "form": form})

    @method_decorator(login_required)
    def post(self, request):
        """
        Создаёт новый API-ключ с шифрованием.

        Валидирует форму, шифрует api_key и secret с помощью Fernet (с проверкой FERNET_KEY),
        сохраняет ключ для текущего пользователя и перенаправляет на список ключей.
        Добавлена обработка ошибок для шифрования и сохранения.

        Параметры:
        - request: HttpRequest объект.

        Возвращает:
        - HttpResponse: Рендеренный шаблон 'trading/api_key_form.html' с формой и ошибками
          или перенаправление на 'api_keys'.
        """
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            try:
                fernet_key = os.environ.get("FERNET_KEY")
                if not fernet_key:
                    raise ValueError("FERNET_KEY environment variable is not set.")
                fernet = Fernet(fernet_key.encode())
                key = form.save(commit=False)
                key.user = request.user
                key.api_key = fernet.encrypt(key.api_key.encode()).decode()
                key.secret = fernet.encrypt(key.secret.encode()).decode()
                key.save()
                return redirect("api_keys")
            except Exception as e:
                form.add_error(None, f"Error encrypting or saving API key: {str(e)}")
        return render(request, "trading/api_key_form.html", {"form": form})


# Добавлен ViewSet для стратегий с оптимизацией производительности
class StrategyViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления стратегиями через API.

    Использует select_related для оптимизации запросов к связанным объектам (user)
    и prefetch_related для параметров стратегии.
    """

    queryset = Strategy.objects.select_related("user").prefetch_related("parameters")
    permission_classes = [
        IsAuthenticated
    ]  # Убедитесь, что пользователь аутентифицирован

    def get_queryset(self):
        # Фильтрация по текущему пользователю для безопасности
        return self.queryset.filter(user=self.request.user)
