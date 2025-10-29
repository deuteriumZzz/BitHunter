import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import get_user
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

class NewsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
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
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def news_update(self, event):
        if self.scope['user'].is_authenticated:
            message = event['message']
            await self.send(text_data=json.dumps({
                'type': 'news_update',
                'data': message
            }))
