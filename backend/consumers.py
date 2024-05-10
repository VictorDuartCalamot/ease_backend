import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatSession

class TechSupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Autenticar usuario y verificar si pertenece a este chat
        if await self.authenticate_chat():
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enviar mensaje al grupo
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def authenticate_chat(self):
        try:
            chat = ChatSession.objects.get(id=self.chat_id, is_active=True)
            auth = self.scope['user'] == chat.customer or self.scope['user'] == chat.admin
            #logger.debug(f"Authentication for chat {self.chat_id} with user {self.scope['user']} : {auth}")
            return auth
        except ChatSession.DoesNotExist:
            #logger.debug(f"Chat session {self.chat_id} does not exist.")
            return False