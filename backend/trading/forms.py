from django import forms
from .models import Strategy, ApiKey

class StrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'description', 'symbol', 'is_active', 'parameters']

class ApiKeyForm(forms.ModelForm):
    class Meta:
        model = ApiKey
        fields = ['exchange', 'api_key', 'secret']
        widgets = {
            'api_key': forms.PasswordInput(),
            'secret': forms.PasswordInput(),
        }
