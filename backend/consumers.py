import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from backend.models import ChatSession
from django.contrib.auth.tokens import default_token_generator
from django.db.utils import OperationalError
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Check if user is authenticated (assuming user is already set in scope by middleware)
        if isinstance(self.scope['user'], AnonymousUser) or self.scope['user'].is_anonymous:
            await self.close(code=4001)  # Close the connection with specific error code
            return

        # Extract token from the query string safely
        try:
            token = self.scope['query_string'].decode().split('token=')[1]
        except IndexError:
            await self.close(code=4002)  # Error code for "Token not provided"
            return

        # Authenticate the user
        user = await self.authenticate_user(token)
        if user is None:
            await self.close(code=4003)  # Error code for "Invalid token"
            return

        # Check if user is part of the chat
        try:
            is_allowed = await self.is_user_in_chat_session(user, self.chat_id)
        except OperationalError:
            await self.close(code=4004)  # Error code for database issues
            return
        except ChatSession.DoesNotExist:
            await self.close(code=4005)  # Error code for "Chat session does not exist"
            return

        if not is_allowed:
            await self.close(code=4006)  # Error code for "User not part of the chat"
            return

        # Add user to the chat group
        try:
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            await self.close(code=4007)  # General error handling for adding to group
            print(f"Failed to add to chat group: {str(e)}")  # Optionally log the error

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to chat group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            user_id = default_token_generator.check_token(token)  # Adjust based on your token logic
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_in_chat_session(self, user, chat_id):
        session = ChatSession.objects.get(id=chat_id)
        return session.admin == user or session.customer == user
