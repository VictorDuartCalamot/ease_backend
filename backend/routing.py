from django.urls import re_path
from backend.consumers.chat import ChatConsumer
'''
    Route for the websocket connection
'''
websocket_urlpatterns = [
    re_path(r'^ws/support/chat/(?P<chat_uuid>[0-9a-f-]{36})/$', ChatConsumer.as_asgi()),
]