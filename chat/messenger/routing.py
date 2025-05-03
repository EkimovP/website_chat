from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('ws/channel/<slug:channel_slug>/', consumers.ChannelConsumer.as_asgi()),
]
