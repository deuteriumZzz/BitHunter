import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Connected to analytics'}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'predict':
            from .tasks import predict_price
            prediction = predict_price.delay(data['exchange'], data['symbol']).get()
            await self.send(text_data=json.dumps({'prediction': prediction}))
