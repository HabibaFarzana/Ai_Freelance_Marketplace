# # user_notifications/consumers.py

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             await self.channel_layer.group_add(
#                 f"user_notifications_{self.user.id}",
#                 self.channel_name
#             )
#             await self.accept()

#     async def disconnect(self, close_code):
#         if self.user.is_authenticated:
#             await self.channel_layer.group_discard(
#                 f"user_notifications_{self.user.id}",
#                 self.channel_name
#             )

#     async def notification_message(self, event):
#         await self.send(text_data=json.dumps({
#             "type": "new_notification",
#             "notification": event["notification"]
#         }))