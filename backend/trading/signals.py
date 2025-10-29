"""
Модуль сигналов для логирования изменений в трейдах.

Обрабатывает сигналы post_save и post_delete для модели Trade,
автоматически создавая записи в TradeAudit с деталями действий.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Trade, TradeAudit


@receiver(post_save, sender=Trade)
def log_trade_save(sender, instance, created, **kwargs):
    """
    Логирует создание или обновление трейда в TradeAudit.

    При создании или сохранении трейда создаёт запись аудита с действием 'create' или 'update',
    включая детали о символе и сумме.
    """
    action = 'create' if created else 'update'
    TradeAudit.objects.create(
        user=instance.user,
        trade=instance,
        action=action,
        details={'symbol': instance.symbol, 'amount': instance.amount}
    )


@receiver(post_delete, sender=Trade)
def log_trade_delete(sender, instance, **kwargs):
    """
    Логирует удаление трейда в TradeAudit.

    При удалении трейда создаёт запись аудита с действием 'delete',
    включая деталь о символе.
    """
    TradeAudit.objects.create(
        user=instance.user,
        trade=instance,
        action='delete',
        details={'symbol': instance.symbol}
    )
