import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AnalyticsConsumer(AsyncWebsocketConsumer):
    """
    Потребитель WebSocket для аналитики, обрабатывающий подключения и предсказания цен.
    """

    async def connect(self):
        """
        Обрабатывает подключение клиента к WebSocket.
        Принимает соединение и отправляет подтверждение.
        """
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Connected to analytics'}))

    async def receive(self, text_data):
        """
        Обрабатывает входящие данные от клиента.
        Если тип сообщения 'predict', вызывает задачу предсказания цены и отправляет результат.
        
        :param text_data: Входящие данные в формате JSON.
        """
        data = json.loads(text_data)
        if data['type'] == 'predict':
            from .tasks import predict_price
            prediction = predict_price.delay(data['exchange'], data['symbol']).get()
            await self.send(text_data=json.dumps({'prediction': prediction}))
