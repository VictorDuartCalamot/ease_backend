from django.urls import re_path
from .consumers import TechSupportConsumer

websocket_urlpatterns = [
    re_path(r'^ws/support/chat/(?P<chat_id>\d+)/$', TechSupportConsumer.as_asgi()),
]