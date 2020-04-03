import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        print(other_user, me)
        thread_obj = await self.get_thread(me, other_user)
        print(me, thread_obj.id)
        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name,
            # channel_name is a default attribute of channels
            # but it only comes out if you have channels_layers in your settings.
            # this creates the chat room for us.
            # we've added the current users channel to the unique name of that chat room.
            # chat_room doesnt have to be exactly unique. just kind of.
            # It has to be unique in the sense that you can have all of your users in the same chat room
            # or you could have it unique per user or per user group like we are doing here.
        )
        await self.send({
            "type": "websocket.accept"
        })

        # await asyncio.sleep(10)  # 10 seconds

    async def websocket_receive(self, event):
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            user = self.scope['user']
            username = 'default'
            if user.is_authenticated:
                username = user.username
            my_response = {
                'message': msg,
                'username': username
            }

            # Broadcasts the message event to be sent
            # which triggers chat_babloo_xyz function
            # for all the members of the group which here is the chat_room.
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    'type': 'chat_babloo_xyz',
                    'text_to_channel': json.dumps(my_response)
                }
            )

    async def chat_babloo_xyz(self, event):
        # the name is made up. Not related to websockets.
        # Sends the actual message
        await self.send({
            'type': 'websocket.send',
            'text': event['text_to_channel']
        })

    async def websocket_disconnect(self, event):
        print('disconnected', event)

    @database_sync_to_async
    def get_thread(self, user, other_username):
        return Thread.objects.get_or_new(user, other_username)[0]
