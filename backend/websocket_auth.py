from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from urllib.parse import parse_qs
from django.contrib.auth.models import User
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        close_old_connections()
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]
        user = self.verify_token(token)
        if user:
            scope['user'] = user
        return self.inner(scope)

    def verify_token(self, token):
        try:
            # Verify the token
            decoded_token = UntypedToken(token)
            user_id = decoded_token['user_id']
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
