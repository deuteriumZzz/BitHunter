import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для обработки оповещений.
    
    Управляет соединениями пользователей, добавляя их в группы для получения персонализированных оповещений.
    """
    
    async def connect(self):
        """
        Устанавливает соединение WebSocket.
        
        Создает уникальную группу для пользователя и добавляет канал в эту группу,
        затем принимает соединение.
        """
        self.group_name = f'alerts_{self.scope["user"].id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Разрывает соединение WebSocket.
        
        Удаляет канал из группы пользователя.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def receive(self, text_data):
        """
        Обрабатывает входящие сообщения от клиента.
        
        Пока что не реализовано, оставлено для будущей обработки.
        """
        pass  # Обработка входящих сообщений
    
    async def send_alert(self, event):
        """
        Отправляет оповещение пользователю.
        
        Принимает событие и отправляет его сообщение в JSON-формате через WebSocket.
        """
        await self.send(text_data=json.dumps(event['message']))
