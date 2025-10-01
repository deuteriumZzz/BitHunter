from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AlertRule
from .tasks import send_message

@login_required
def create_alert(request):
    # Логика для создания алерта
    return JsonResponse({'status': 'alert created'})

@login_required
def send_notification(request, rule_id):
    rule = AlertRule.objects.get(id=rule_id, user=request.user)
    send_message.delay(request.user, f"Alert for {rule.symbol}")
    return JsonResponse({'status': 'sent'})
