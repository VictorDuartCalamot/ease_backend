from django.urls import path
from backend.consumers.chat import ChatConsumer
'''
    Route for the websocket connection
'''
websocket_urlpatterns = [
    path('ws/support/chat/<uuid:chat_uuid>/', ChatConsumer.as_asgi()),
]