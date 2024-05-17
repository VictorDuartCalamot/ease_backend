from django.urls import re_path
from .consumers.chat import ChatConsumer
'''
    Route for the websocket connection
'''
websocket_urlpatterns = [
    re_path(r'^ws/support/chat/(?P<chat_id>\d+)/$', ChatConsumer.as_asgi()),
]