from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Trade, TradeAudit

@receiver(post_save, sender=Trade)
def log_trade_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    TradeAudit.objects.create(user=instance.user, trade=instance, action=action, details={'symbol': instance.symbol, 'amount': instance.amount})

@receiver(post_delete, sender=Trade)
def log_trade_delete(sender, instance, **kwargs):
    TradeAudit.objects.create(user=instance.user, trade=instance, action='delete', details={'symbol': instance.symbol})
