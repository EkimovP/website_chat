from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_slug>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]
