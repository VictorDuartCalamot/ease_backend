import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from backend.models import ChatSession
from django.db.utils import OperationalError


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Check if user is authenticated (assuming user is already set in scope by middleware)
        if self.scope['user'].is_anonymous:
            await self.close(code=4001)  # Unauthorized
            return

        # Check if user is part of the chat
        try:
            is_allowed = await self.is_user_in_chat_session(self.scope['user'], self.chat_id)
        except OperationalError as e:
            await self.close(code=4004)  # Database error
            return
        except ChatSession.DoesNotExist:
            await self.close(code=4005)  # Chat session does not exist
            return

        if not is_allowed:
            await self.close(code=4006)  # User not part of the chat
            return

        # Add user to the chat group
        try:
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            await self.close(code=4007)  # Error while adding to group

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
    def is_user_in_chat_session(self, user, chat_id):
        session = ChatSession.objects.get(id=chat_id)
        return session.admin == user or session.customer == user
