import os

from analytics.routing import websocket_urlpatterns as analytics_websockets
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from trading.routing import websocket_urlpatterns as trading_websockets

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BitHunter.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(trading_websockets + analytics_websockets)
        ),
    }
)
