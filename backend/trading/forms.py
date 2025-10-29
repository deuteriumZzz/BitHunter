"""
Модуль форм для приложения трейдинга.

Содержит формы на основе моделей Strategy и ApiKey для создания и редактирования объектов.
"""

from django import forms

from .models import Strategy, ApiKey


class StrategyForm(forms.ModelForm):
    """
    Форма для модели Strategy.

    Позволяет редактировать имя, описание, символ, активность и параметры стратегии.
    """

    class Meta:
        model = Strategy
        fields = ['name', 'description', 'symbol', 'is_active', 'parameters']


class ApiKeyForm(forms.ModelForm):
    """
    Форма для модели ApiKey.

    Позволяет редактировать биржу, API-ключ и секрет. API-ключ и секрет отображаются как поля пароля.
    """

    class Meta:
        model = ApiKey
        fields = ['exchange', 'api_key', 'secret']
        widgets = {
            'api_key': forms.PasswordInput(),
            'secret': forms.PasswordInput(),
        }
