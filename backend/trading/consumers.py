"""
Модуль WebSocket-консьюмера для приложения трейдинга.

Содержит TradingConsumer для обработки соединений, отключений и сообщений через WebSocket.
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TradingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket-консьюмер для трейдинга.

    Обрабатывает соединения, отключения и входящие сообщения. Поддерживает запуск стратегий трейдинга.
    """

    async def connect(self):
        """
        Обрабатывает подключение клиента.

        Принимает соединение и отправляет подтверждение.
        """
        await self.accept()
        await self.send(text_data=json.dumps({'message': 'Connected to trading'}))

    async def disconnect(self, close_code):
        """
        Обрабатывает отключение клиента.

        Не выполняет дополнительных действий.
        """
        pass

    async def receive(self, text_data):
        """
        Обрабатывает входящие сообщения от клиента.

        Если тип сообщения 'start_trading', запускает задачу трейдинга асинхронно и отправляет статус.
        """
        data = json.loads(text_data)
        if data['type'] == 'start_trading':
            from .tasks import run_bot
            run_bot.delay(data['strategy_id'])
            await self.send(text_data=json.dumps({'status': 'started'}))
