from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom token auth middleware for Django Channels
    """
    
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'sec-websocket-protocol' in headers:
            token_name, token = headers[b'sec-websocket-protocol'].decode().split(', ')
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            scope['user'] = await database_sync_to_async(jwt_auth.get_user)(validated_token)
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
