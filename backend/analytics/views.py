from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import predict_price, analyze_news, train_model_task
import ccxt
import json

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        symbol = data['symbol']
        exchange = ccxt.binance()
        prediction = predict_price.delay(exchange, symbol).get()
        return JsonResponse({'prediction': prediction})

@csrf_exempt
def news_analysis(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        symbol = data['symbol']
        sentiment = analyze_news.delay(symbol).get()
        return JsonResponse({'sentiment': sentiment})

@csrf_exempt
def train_model(request):
    train_model_task.delay()
    return JsonResponse({'status': 'training started'})
