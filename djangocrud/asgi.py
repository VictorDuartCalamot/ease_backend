"""
ASGI config for djangocrud project.

It exposes the ASGI callable as a module-level variable named ``backend``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from backend.routing import websocket_urlpatterns
from backend.websocket_auth import TokenAuthMiddlewareStack
backend = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP protocol management
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Using the websocket URLS specified in backend.routing
        )
    ),
})
