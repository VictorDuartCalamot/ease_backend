from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async  # Importing the decorator
from urllib.parse import parse_qs
import jwt  # Assuming JWT for token handling
from django.contrib.auth.models import User
import os
SECRET_KEY = os.environ.get("SECRET_KEY")
class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware for Django Channels that extracts token from the query string,
    validates it, and sets the user in the scope.
    """
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = parse_qs(scope['query_string'].decode('utf8'))
        token = query_string.get('token', [None])[0]
        
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id')
                if user_id:
                    scope['user'] = await self.get_user(user_id)
            except jwt.ExpiredSignatureError:
                print("Token expired")
            except jwt.InvalidTokenError:
                print("Invalid token")
        
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
