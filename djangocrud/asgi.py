"""
ASGI config for djangocrud project.

It exposes the ASGI callable as a module-level variable named ``backend``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from backend.routing import websocket_urlpatterns  # Import después de django.setup()

backend = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Define cómo manejar los protocolos HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Utiliza las URL de WebSocket definidas en backend.routing
        )
    ),
})
