from django.urls import path
from backend.consumers.chat import ChatConsumer
from backend.consumers.chatbot import ChatBotConsumer
'''
    Route for the websocket connection
'''
websocket_urlpatterns = [
    path('ws/support/chat/<uuid:chat_uuid>/', ChatConsumer.as_asgi()),
    path('ws/support/chatbot/)',ChatBotConsumer.as_asgi()),
]