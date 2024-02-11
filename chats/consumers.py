import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timesince import timesince

from users.models import User
import logging

from .models import Message, Room

logger = logging.getLogger("main")


class ChatSupportConsumer(AsyncWebsocketConsumer):
    # connect вызывается при подключении
    async def connect(self):
        logger.info("Start connect")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        # Join room group
        await self.get_room()
        await self.send_message_history()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info("Middle  connect")

        # Inform user
        if self.user.is_staff:
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "users_update"}
            )
        logger.info("End connect")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if not self.user.is_staff:
            await self.set_room_closed()

    async def send_message_history(self):
        message_history = await self.get_message_history()
        for message in message_history:
            await self.send_message_to_client(message)

    async def get_message_history(self):
        room = Room.objects.filter(uuid=self.room_name).first()
        return room.messages.all()
    
    async def send_message_to_client(self, message):
        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": message.text,
            "username": message.sent_by,
            "created_at": timesince(message.created_at),
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]
        message = text_data_json["message"]
        username = text_data_json["username"]

        if type == "message":
            new_message = await self.create_message(username, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": username,
                    "created_at": timesince(new_message.created_at),
                },
            )
        elif type == "update":
            await self.channel_layer.group_send(
                self.channel_group_name,
                {
                    "type": "writing_active",
                    "message": message,
                    "username": username,
                    "created_at": timesince(new_message.created_at),
                },
            )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["type"],
                    "message": event["message"],
                    "username": event["username"],
                    "created_at": event["created_at"],
                }
            )
        )

    async def users_update(self, event):
        logger.info("End connect5")
        await self.send(text_data=json.dumps({"type": "users-update"}))

    async def writing_active(self, event):
        # send writing is active to room
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["type"],
                    "message": event["message"],
                    "username": event["username"],
                    "created_at": event["created_at"],
                }
            )
        )
        logger.info("End connect6")

    @sync_to_async
    def get_room(self):
        self.room = Room.objects.get(uuid=self.room_name)

    @sync_to_async
    def set_room_closed(self):
        self.room = Room.objects.get(uuid=self.room_name)
        self.room.status = Room.CLOSED
        self.room.save()

    @sync_to_async
    def create_message(self, sent_by, message):
        message = Message.objects.create(text=message, sent_by=sent_by)

        self.room.messages.add(message)

        return message