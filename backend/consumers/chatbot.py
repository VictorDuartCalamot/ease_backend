import json
from channels.generic.websocket import AsyncWebsocketConsumer
import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOTCHAT_ID = os.environ.get('BOT_ID')
class ChatBotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_bot'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send the message to the Telegram bot
        bot_token = BOT_TOKEN
        chat_id = BOTCHAT_ID
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'
        requests.get(url)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
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