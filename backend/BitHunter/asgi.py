import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from trading.routing import websocket_urlpatterns as trading_websockets
from analytics.routing import websocket_urlpatterns as analytics_websockets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BitHunter.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            trading_websockets + analytics_websockets
        )
    ),
})

