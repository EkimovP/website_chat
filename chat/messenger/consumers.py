from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging


# Настраиваем логгер
logger = logging.getLogger(__name__)


class ChannelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем slug канала из URL
        self.channel_slug = self.scope['url_route']['kwargs']['channel_slug']
        # Имя группы для канала (уникальное для каждого канала)
        self.channel_group_name = f'chat_{self.channel_slug}'
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'

        # Логируем подключение
        logger.info(f"User {username} connected to channel {self.channel_slug}")

        # Добавляем пользователя в группу канала
        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )

        # Принимаем соединение
        await self.accept()

    async def disconnect(self, close_code):
        # Получаем имя пользователя
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'

        # Логируем отключение
        logger.info(f"User {username} disconnected from channel {self.channel_slug} with code {close_code}")

        # Удаляем пользователя из группы при отключении
        await self.channel_layer.group_discard(
            self.channel_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Получаем имя пользователя
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'

        # Получаем сообщение от клиента
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Логируем полученное сообщение
        logger.info(f"Message from {username} in channel {self.channel_slug}: {message}")

        # Отправляем сообщение всем в группе
        await self.channel_layer.group_send(
            self.channel_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username,
            }
        )

    async def chat_message(self, event):
        # Логируем отправку сообщения клиенту
        logger.info(
            f"Sending message to {self.scope['user'].username or 'anonymous'} in channel {self.channel_slug}: {event['message']}")

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))
