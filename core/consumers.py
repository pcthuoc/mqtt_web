# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Xác định nhóm người dùng dựa trên ID người dùng
        self.user_id = self.scope["user"].id
        self.user_group_name = f"user_{self.user_id}"

        # Thêm người dùng vào nhóm WebSocket dựa trên user_id
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi nhóm khi ngắt kết nối
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def send_data_update(self, event):
        # Phương thức nhận sự kiện từ `group_send`
        data = event["data"]
        await self.send(text_data=json.dumps(data))

    async def receive(self, text_data):
        # Xử lý tin nhắn nhận từ client nếu cần (không bắt buộc)
        pass
