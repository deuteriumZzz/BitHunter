from django.db import models
from django.contrib.auth.models import User

class AlertRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    threshold = models.DecimalField(max_digits=10, decimal_places=2)

class Notification(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
