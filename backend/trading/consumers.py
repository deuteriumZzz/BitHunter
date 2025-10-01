import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TradingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Connected to trading'}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'start_trading':
            from .tasks import start_trading
            start_trading.delay(data['strategy_id'])
            await self.send(text_data=json.dumps({'status': 'started'}))
