import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from messenger.models import Channel, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем slug канала из URL
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.room_group_name = f'chat_{self.chat_slug}'

        # Проверяем, что пользователь аутентифицирован и имеет доступ к каналу
        if self.scope['user'].is_anonymous:
            await self.close()
            return

        # Проверяем, существует ли канал и состоит ли пользователь в нем
        if not await self.has_access_to_channel():
            await self.close()
            return

        # Подключаем пользователя к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отключаем пользователя от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Получаем сообщение от клиента
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Сохраняем сообщение в базе данных
        user = self.scope['user']
        await self.save_message(user, message)

        # Отправляем сообщение всем в группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
            }
        )

    async def chat_message(self, event):
        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def has_access_to_channel(self):
        try:
            channel = Channel.objects.get(slug=self.chat_slug)
            return channel.members.contains(self.scope['user'])
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, content):
        channel = Channel.objects.get(slug=self.chat_slug)
        Message.objects.create(
            channel=channel,
            user=user,
            content=content
        )
