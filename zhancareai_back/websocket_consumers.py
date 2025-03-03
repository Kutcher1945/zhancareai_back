import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope["url_route"]["kwargs"]["meeting_id"]
        self.room_group_name = f"video_call_{self.meeting_id}"

        # ✅ Join WebSocket room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(json.dumps({"message": "Connected to video call room"}))

    async def disconnect(self, close_code):
        # ✅ Leave WebSocket room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles WebSocket messages."""
        data = json.loads(text_data)

        # ✅ Broadcast message to the room
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "video_call_message", "message": data}
        )

    async def video_call_message(self, event):
        """Sends messages to the WebSocket."""
        await self.send(text_data=json.dumps(event["message"]))
