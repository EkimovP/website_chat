import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from messenger.models import Channel, Message
from django.contrib.auth import get_user_model

# Настраиваем логгер
logger = logging.getLogger(__name__)


class ChannelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_slug = self.scope['url_route']['kwargs']['channel_slug']
        self.channel_group_name = f'chat_{self.channel_slug}'
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'

        # Проверяем, что пользователь авторизован и состоит в канале
        if not self.scope['user'].is_authenticated:
            logger.warning(f"Anonymous user tried to connect to channel {self.channel_slug}")
            await self.close()
            return

        if not await self.is_user_in_channel():
            logger.warning(f"User {username} not in channel {self.channel_slug}")
            await self.close()
            return

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
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'
        logger.info(f"User {username} disconnected from channel {self.channel_slug} with code {close_code}")

        # Удаляем пользователя из группы
        await self.channel_layer.group_discard(
            self.channel_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        username = self.scope['user'].username if self.scope['user'].is_authenticated else 'anonymous'
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        # Логируем полученное сообщение
        logger.info(f"Message from {username} in channel {self.channel_slug}: {message_content}")

        # Сохраняем сообщение в базе данных
        message = await self.save_message(message_content)

        # Отправляем сообщение всем в группе
        await self.channel_layer.group_send(
            self.channel_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'username': username,
                'time_create': message.time_create.strftime('%H:%M'),  # Форматируем время
            }
        )

    async def chat_message(self, event):
        logger.info(f"Sending message to {self.scope['user'].username or 'anonymous'} in channel {self.channel_slug}: {event['message']}")

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'time_create': event['time_create'],
        }))

    @database_sync_to_async
    def is_user_in_channel(self):
        """Проверяем, состоит ли пользователь в канале."""
        try:
            channel = Channel.objects.get(slug=self.channel_slug)
            return channel.users.filter(id=self.scope['user'].id).exists()
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """Сохраняем сообщение в базе данных."""
        channel = Channel.objects.get(slug=self.channel_slug)
        message = Message.objects.create(
            content=content,
            user=self.scope['user'],
            channel=channel,
            time_create=timezone.now()
        )
        return message
