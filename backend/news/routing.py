from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/news/(?P<symbol>\w+)/$", consumers.NewsConsumer.as_asgi()),
]
