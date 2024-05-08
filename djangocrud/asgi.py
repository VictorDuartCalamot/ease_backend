"""
ASGI config for djangocrud project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import django
from django.urls import path
from backend.routing import websocket_urlpatterns  # Asegúrate de tener esto configurado en tu aplicación

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Define cómo manejar los protocolos HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Utiliza las URL de WebSocket definidas en backend.routing
        )
    ),
})