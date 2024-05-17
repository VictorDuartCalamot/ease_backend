from django.urls import re_path
from backend.consumers.chat import ChatConsumer
'''
    Route for the websocket connection
'''
websocket_urlpatterns = [
    re_path('ws/support/chat/<uuid:chat_uuid>', ChatConsumer.as_asgi()),
]