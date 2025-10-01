from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Strategy, Trade, ApiKey
from .forms import StrategyForm, ApiKeyForm
from .tasks import start_trading, calculate_metrics
import json

@login_required
def strategy_list(request):
    strategies = Strategy.objects.filter(user=request.user)
    return render(request, 'trading/strategy_list.html', {'strategies': strategies})

@login_required
def strategy_create(request):
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            return redirect('strategy_list')
    else:
        form = StrategyForm()
    return render(request, 'trading/strategy_form.html', {'form': form})

@login_required
def start_bot(request, strategy_id):
    strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
    start_trading.delay(strategy_id, demo=True)
    return JsonResponse({'status': 'started'})

@login_required
def strategy_metrics(request, strategy_id):
    strategy = get_object_or_404(Strategy, id=strategy_id, user=request.user)
    metrics = calculate_metrics.delay(strategy_id).get()
    return JsonResponse(metrics)

class ApiKeyView(View):
    @method_decorator(login_required)
    def get(self, request):
        keys = ApiKey.objects.filter(user=request.user)
        return render(request, 'trading/api_keys.html', {'keys': keys})

    @method_decorator(login_required)
    def post(self, request):
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            key = form.save(commit=False)
            key.user = request.user
            fernet = Fernet(os.environ.get('FERNET_KEY').encode())
            key.api_key = fernet.encrypt(key.api_key.encode()).decode()
            key.secret = fernet.encrypt(key.secret.encode()).decode()
            key.save()
            return redirect('api_keys')
        return render(request, 'trading/api_key_form.html', {'form': form})
