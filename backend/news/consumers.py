import json

from channels.auth import get_user
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


class NewsConsumer(AsyncWebsocketConsumer):
    """Класс для обработки WebSocket соединений новостей."""

    async def connect(self):
        """
        Метод для обработки подключения к WebSocket.

        Проверяет токен аутентификации из querystring,
        аутентифицирует пользователя и присоединяет к группе новостей
        для указанного символа, если пользователь аутентифицирован.
        """
        # Проверка токена из querystring (например, ?token=your_token)
        query_string = self.scope['query_string'].decode()
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[1].split('&')[0]

        if token:
            try:
                user = Token.objects.get(key=token).user
            except Token.DoesNotExist:
                await self.close()
                return
        else:
            user = AnonymousUser()

        self.scope['user'] = user
        self.symbol = self.scope['url_route']['kwargs']['symbol'].lower()
        self.room_group_name = f'news_{self.symbol}'

        if not user.is_authenticated:
            await self.close()  # Закрыть если не аутентифицирован
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Метод для обработки отключения от WebSocket.

        Удаляет соединение из группы новостей.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def news_update(self, event):
        """
        Метод для обработки обновлений новостей.

        Отправляет сообщение обновления новостей аутентифицированным пользователям.
        """
        if self.scope['user'].is_authenticated:
            message = event['message']
            await self.send(text_data=json.dumps({
                'type': 'news_update',
                'data': message
            }))
