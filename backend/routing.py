from django.urls import re_path
from .consumers import TechSupportConsumer

websocket_urlpatterns = [
    re_path('ws/support/chat/<int:chat_id>/', TechSupportConsumer.as_asgi()),
]