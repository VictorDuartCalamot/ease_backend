import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import OperationalError
from backend.models import ChatSession, ChatMessage
from backend.serializers import ChatMessageSerializer
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.chat_group_name = f'chat_{self.chat_uuid}'
        print(self.scope)

        # Check if user is authenticated (assuming user is already set in scope by middleware)
        if self.scope['user'].is_anonymous:
            await self.close(code=4001)  # Unauthorized
            return

        # Check if user is part of the chat
        try:
            is_allowed = await self.is_user_in_chat_session(self.scope['user'], self.chat_uuid)
        except OperationalError:
            await self.close(code=4004)  # Database error
            return
        except ChatSession.DoesNotExist:
            await self.close(code=4005)  # Chat session does not exist
            return

        if not is_allowed:
            await self.close(code=4006)  # User not part of the chat
            return

        # Add user to the chat group and accept the connection
        try:
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()

        except Exception as e:
            print(f"Error while adding to group: {e}")
            await self.close(code=4007)  # Error while adding to group
            return

        # Send previous messages to the user (if any)
        try:
            messages = await self.get_chat_messages(self.chat_uuid)
            if messages.exists():
                serialized_messages = ChatMessageSerializer(messages, many=True).data
                await self.send(text_data=json.dumps(serialized_messages))
        except Exception as e:
            print(f"Error while retrieving messages: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        await self.save_message(self.scope['user'], self.chat_uuid, message)

        # Send message to chat group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'user': self.scope['user'].first_name,
                'message': message,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    async def chat_message(self, event):
        user = event['user']
        message = event['message']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'user': user,
            'message': message,
            'timestamp': timestamp                    
        }))

    @database_sync_to_async
    def is_user_in_chat_session(self, user, chat_uuid):
        session = ChatSession.objects.get(id=chat_uuid)
        return session.admin == user or session.customer == user

    @database_sync_to_async
    def get_chat_messages(self, chat_uuid):
        return ChatMessage.objects.filter(id=chat_uuid).order_by('timestamp')

    @database_sync_to_async
    def save_message(self, user, chat_uuid, message):
        ChatMessage.objects.create(user=user, chat_session=chat_uuid, message=message)
