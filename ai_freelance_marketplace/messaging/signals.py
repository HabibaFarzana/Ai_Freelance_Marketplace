from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Conversation
from user_notifications.models import UserNotification
from django.urls import reverse
from django.db.models import Q

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        conversation = instance.conversation
        recipient = conversation.participants.exclude(id=instance.sender.id).first()

        # Check if there's an existing unread notification for this conversation
        existing_notification = UserNotification.objects.filter(
            Q(recipient=recipient) & 
            Q(sender=instance.sender) & 
            Q(notification_type='new_message') & 
            Q(is_read=False) &
            Q(url=reverse('conversation', kwargs={'conversation_id': conversation.id}))
        ).first()

        if existing_notification:
            # Update existing notification
            existing_notification.message = f"New messages from {instance.sender.username}"
            existing_notification.save()
        else:
            # Create new notification
            UserNotification.objects.create(
                recipient=recipient,
                sender=instance.sender,
                message=f"New message from {instance.sender.username}",
                url=reverse('conversation', kwargs={'conversation_id': conversation.id}),
                notification_type='new_message'
            )