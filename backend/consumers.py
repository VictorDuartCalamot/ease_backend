import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from backend.models import ChatSession
from django.db.utils import OperationalError

# Configure logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Check if user is authenticated (assuming user is already set in scope by middleware)
        if self.scope['user'].is_anonymous:
            #logger.error(f'Unauthorized connection attempt to chat {self.chat_id}.')
            await self.close(code=4001)  # Unauthorized
            return

        # Check if user is part of the chat
        try:
            is_allowed = await self.is_user_in_chat_session(self.scope['user'], self.chat_id)
        except OperationalError as e:
            #logger.exception("Database error while checking chat session membership: %s", str(e))
            await self.close(code=4004)  # Database error
            return
        except ChatSession.DoesNotExist:
            #logger.warning(f'Chat session {self.chat_id} does not exist.')
            await self.close(code=4005)  # Chat session does not exist
            return

        if not is_allowed:
            #logger.warning(f'User {self.scope["user"].id} not part of chat {self.chat_id}.')
            await self.close(code=4006)  # User not part of the chat
            return

        # Add user to the chat group
        try:
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
            #logger.info(f'User {self.scope["user"].id} added to chat {self.chat_id}.')
        except Exception as e:
            #logger.exception("Failed to add to chat group: %s", str(e))
            await self.close(code=4007)  # Error while adding to group

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )
        #logger.info(f'User {self.scope["user"].id} disconnected from chat {self.chat_id} with code {close_code}.')

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        #logger.debug(f'Message received in chat {self.chat_id}: {message}')

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
        #logger.debug(f'Sending message to WebSocket in chat {self.chat_id}: {message}')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def is_user_in_chat_session(self, user, chat_id):
        session = ChatSession.objects.get(id=chat_id)
        return session.admin == user or session.customer == user
