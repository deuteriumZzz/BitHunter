"""
Views для приложения alerts.

Содержит представления для создания оповещений и отправки уведомлений пользователям.
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import AlertRule
from .tasks import send_message


@login_required
def create_alert(request):
    """
    Создает новое правило оповещения.

    Обрабатывает POST-запрос для создания алерта на основе данных пользователя.

    Args:
        request (HttpRequest): Объект запроса Django.

    Returns:
        JsonResponse: JSON-ответ с статусом создания алерта.
    """
    # Логика для создания алерта
    return JsonResponse({"status": "alert created"})


@login_required
def send_notification(request, rule_id):
    """
    Отправляет уведомление для указанного правила оповещения.

    Получает правило по ID, принадлежащее текущему пользователю, и инициирует
    асинхронную задачу отправки сообщения.

    Args:
        request (HttpRequest): Объект запроса Django.
        rule_id (int): ID правила оповещения.

    Returns:
        JsonResponse: JSON-ответ с статусом отправки.
    """
    rule = AlertRule.objects.get(id=rule_id, user=request.user)
    send_message.delay(request.user, f"Alert for {rule.symbol}")
    return JsonResponse({"status": "sent"})
